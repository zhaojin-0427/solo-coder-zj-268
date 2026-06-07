from typing import List, Dict, Set, Tuple
from collections import defaultdict
import uuid
from datetime import datetime, timedelta
from app.database.ingredients import (
    get_ingredient_info,
    INGREDIENT_CONFLICTS,
    SKIN_TYPE_PROFILES,
    ACTIVE_INGREDIENTS
)
from app.schemas import (
    RegimenPlanRequest,
    RegimenProduct,
    RegimenPlanResult,
    IngredientAccumulationRisk,
    ToleranceCurve,
    TolerancePoint,
    AlternationWindow,
    RestartAdvice,
    DailyCareItem,
    StageRiskWarning,
    AdjustmentSuggestion,
    RegimenTrackRequest,
    RegimenTrackResult
)
from app.database.stats import stats_store


HIGH_IRRITATION_INGREDIENTS = {
    "视黄醇": {"base_tolerance": 20, "weekly_gain": 8, "max_cumulative_risk": 4, "need_rest": True, "rest_weeks": 1},
    "水杨酸": {"base_tolerance": 35, "weekly_gain": 10, "max_cumulative_risk": 4, "need_rest": True, "rest_weeks": 1},
    "果酸": {"base_tolerance": 30, "weekly_gain": 8, "max_cumulative_risk": 4, "need_rest": True, "rest_weeks": 1},
    "维生素C": {"base_tolerance": 50, "weekly_gain": 5, "max_cumulative_risk": 3, "need_rest": False, "rest_weeks": 0},
    "烟酰胺": {"base_tolerance": 60, "weekly_gain": 5, "max_cumulative_risk": 3, "need_rest": False, "rest_weeks": 0},
    "曲酸": {"base_tolerance": 40, "weekly_gain": 7, "max_cumulative_risk": 3, "need_rest": True, "rest_weeks": 1},
}

ACCUMULATION_THRESHOLDS = {
    "视黄醇": {"daily": 1, "weekly": 4, "risk_per_extra": 15},
    "水杨酸": {"daily": 1, "weekly": 4, "risk_per_extra": 12},
    "果酸": {"daily": 1, "weekly": 4, "risk_per_extra": 12},
    "维生素C": {"daily": 2, "weekly": 14, "risk_per_extra": 6},
    "烟酰胺": {"daily": 2, "weekly": 14, "risk_per_extra": 5},
    "酒精": {"daily": 1, "weekly": 5, "risk_per_extra": 10},
    "香精": {"daily": 1, "weekly": 3, "risk_per_extra": 15},
}

TIME_SLOT_HOURS = {
    "morning": 8,
    "evening": 20,
    "weekly": 12,
}


class RegimenPlanner:

    @staticmethod
    def _canonicalize_ingredients(ingredient_list: List[str]) -> Set[str]:
        canonical = set()
        for ing in ingredient_list:
            info = get_ingredient_info(ing)
            if info:
                canonical.add(info["name"])
        return canonical

    @staticmethod
    def _get_product_effective_slots(product: RegimenProduct) -> List[str]:
        if product.time_slot == "morning_evening":
            return ["morning", "evening"]
        return [product.time_slot]

    @staticmethod
    def _is_product_active_on_day(product: RegimenProduct, day_of_week: int, week: int) -> bool:
        if week < product.start_week:
            return False
        if product.end_week is not None and week > product.end_week:
            return False

        if product.frequency_unit == "daily":
            return True
        elif product.frequency_unit == "times_per_week":
            return day_of_week < product.frequency
        elif product.frequency_unit == "every_n_days":
            day_idx = (week - 1) * 7 + day_of_week
            return day_idx % product.frequency == 0
        return True

    @staticmethod
    def _build_ingredient_exposure(
        products: List[RegimenProduct],
        total_weeks: int
    ) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Set[str]], Dict[str, List[Tuple[int, int, str]]]]:
        daily_exposure: Dict[str, int] = defaultdict(int)
        weekly_exposure: Dict[str, int] = defaultdict(int)
        slot_ingredients: Dict[str, Set[str]] = defaultdict(set)
        ingredient_usage_details: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)

        for product in products:
            canonical = RegimenPlanner._canonicalize_ingredients(product.ingredient_list)
            slots = RegimenPlanner._get_product_effective_slots(product)
            end_w = product.end_week or total_weeks
            actual_weeks = min(end_w, total_weeks) - product.start_week + 1

            for ing in canonical:
                per_day = len(slots)
                if product.frequency_unit == "daily":
                    per_week = per_day * 7
                elif product.frequency_unit == "times_per_week":
                    per_week = per_day * product.frequency
                else:
                    per_week = per_day * max(1, 7 // max(1, product.frequency))

                daily_exposure[ing] += per_day
                weekly_exposure[ing] += per_week * actual_weeks

                for slot in slots:
                    slot_ingredients[slot].add(ing)

                for w in range(product.start_week, min(end_w, total_weeks) + 1):
                    for d in range(7):
                        if RegimenPlanner._is_product_active_on_day(product, d, w):
                            for slot in slots:
                                ingredient_usage_details[ing].append((w, d, slot))

        return daily_exposure, weekly_exposure, slot_ingredients, ingredient_usage_details

    @staticmethod
    def _calculate_accumulation_risks(
        daily_exposure: Dict[str, int],
        weekly_exposure: Dict[str, int],
        slot_ingredients: Dict[str, Set[str]],
        skin_type: str,
        is_sensitive: bool
    ) -> List[IngredientAccumulationRisk]:
        risks: List[IngredientAccumulationRisk] = []
        sens_multiplier = 1.5 if is_sensitive else 1.0

        for ing_name, threshold in ACCUMULATION_THRESHOLDS.items():
            daily_count = daily_exposure.get(ing_name, 0)
            weekly_count = weekly_exposure.get(ing_name, 0)

            if daily_count == 0 and weekly_count == 0:
                continue

            daily_extra = max(0, daily_count - threshold["daily"])
            weekly_extra = max(0, weekly_count // 7 - threshold["weekly"])

            risk_score = (daily_extra + weekly_extra) * threshold["risk_per_extra"] * sens_multiplier
            risk_score = min(100.0, risk_score)

            affected_slots = []
            for slot, ings in slot_ingredients.items():
                if ing_name in ings:
                    affected_slots.append(slot)

            if risk_score >= 70:
                level = "critical"
            elif risk_score >= 45:
                level = "high"
            elif risk_score >= 20:
                level = "medium"
            else:
                level = "low"

            description_parts = []
            if daily_count > threshold["daily"]:
                description_parts.append(f"单日暴露{daily_count}次，超过阈值{threshold['daily']}次")
            if weekly_count // 7 > threshold["weekly"]:
                description_parts.append(f"周均暴露{weekly_count // 7}次，超过阈值{threshold['weekly']}次/周")
            if not description_parts:
                description_parts.append(f"当前暴露量在安全范围内，需持续观察")

            category = get_ingredient_info(ing_name)
            cat = category["category"] if category else "unknown"

            if level in ["high", "critical"]:
                recommendation = f"建议减少{ing_name}的使用频率，单日不超过{threshold['daily']}次，每周不超过{threshold['weekly']}次，可考虑与温和修复产品交替使用"
                stats_store.record_risk_warning(f"成分累积风险-{ing_name}")
            elif level == "medium":
                recommendation = f"注意观察皮肤状态，{ing_name}使用量接近阈值，建议搭配舒缓修复成分（如积雪草、神经酰胺）"
            else:
                recommendation = f"{ing_name}暴露量在安全范围，可按当前方案使用"

            risks.append(IngredientAccumulationRisk(
                ingredient_name=ing_name,
                category=cat,
                daily_exposure_count=daily_count,
                weekly_exposure_count=weekly_count,
                risk_level=level,
                risk_score=round(risk_score, 1),
                description="；".join(description_parts),
                affected_time_slots=affected_slots,
                recommendation=recommendation
            ))

        return risks

    @staticmethod
    def _calculate_tolerance_curves(
        ingredient_usage_details: Dict[str, List[Tuple[int, int, str]]],
        total_weeks: int,
        is_sensitive: bool
    ) -> List[ToleranceCurve]:
        curves: List[ToleranceCurve] = []
        sens_penalty = 0.85 if is_sensitive else 1.0

        for ing_name, config in HIGH_IRRITATION_INGREDIENTS.items():
            details = ingredient_usage_details.get(ing_name, [])
            if not details:
                continue

            points: List[TolerancePoint] = []
            tolerance = config["base_tolerance"] * sens_penalty
            target = 85.0

            for week in range(1, total_weeks + 1):
                week_usage = sum(1 for d in details if d[0] == week)
                irritation_risk = min(100.0, week_usage * config["risk_per_extra"] if "risk_per_extra" in config else week_usage * 8)

                if week_usage > 0:
                    gain = config["weekly_gain"] * sens_penalty * (1 - irritation_risk / 200)
                    tolerance = min(95.0, tolerance + gain)

                if tolerance >= 75:
                    status = "耐受良好"
                elif tolerance >= 50:
                    status = "建立中"
                else:
                    status = "需谨慎"

                points.append(TolerancePoint(
                    week=week,
                    tolerance_score=round(tolerance, 1),
                    irritation_risk=round(irritation_risk, 1),
                    status=status,
                    description=f"第{week}周使用{week_usage}次，耐受度{round(tolerance, 1)}%"
                ))

            is_tolerated = tolerance >= 70

            if is_tolerated:
                recommendation = f"{ing_name}耐受已建立，可按计划继续使用，注意维持修复护理"
            else:
                recommendation = f"{ing_name}耐受建立不足，建议降低使用频率，配合神经酰胺/积雪草修复，必要时暂停1周"

            curves.append(ToleranceCurve(
                ingredient_name=ing_name,
                start_score=round(config["base_tolerance"] * sens_penalty, 1),
                current_score=round(tolerance, 1),
                target_score=target,
                points=points,
                is_tolerated=is_tolerated,
                recommendation=recommendation
            ))

        return curves

    @staticmethod
    def _calculate_alternation_windows(
        products: List[RegimenProduct],
        total_weeks: int
    ) -> List[AlternationWindow]:
        windows: List[AlternationWindow] = []

        for conflict in INGREDIENT_CONFLICTS:
            conflict_type = conflict["conflict_type"]
            if conflict_type == "过度叠加":
                continue

            ing_a, ing_b = conflict["ingredients"][0], conflict["ingredients"][1]

            products_with_a: List[Tuple[RegimenProduct, List[str]]] = []
            products_with_b: List[Tuple[RegimenProduct, List[str]]] = []

            for p in products:
                canonical = RegimenPlanner._canonicalize_ingredients(p.ingredient_list)
                slots = RegimenPlanner._get_product_effective_slots(p)
                if any(i.lower() == ing_a.lower() for i in canonical):
                    products_with_a.append((p, slots))
                if any(i.lower() == ing_b.lower() for i in canonical):
                    products_with_b.append((p, slots))

            if not products_with_a or not products_with_b:
                continue

            severity = conflict["severity"]
            min_interval = 12 if severity == "high" else 8 if severity == "medium" else 4

            current_ok = True
            for p_a, slots_a in products_with_a:
                for p_b, slots_b in products_with_b:
                    end_a = p_a.end_week or total_weeks
                    end_b = p_b.end_week or total_weeks
                    overlap_start = max(p_a.start_week, p_b.start_week)
                    overlap_end = min(end_a, end_b)
                    if overlap_start > overlap_end:
                        continue

                    for s_a in slots_a:
                        for s_b in slots_b:
                            if s_a == s_b:
                                current_ok = False
                            elif TIME_SLOT_HOURS.get(s_a, 0) and TIME_SLOT_HOURS.get(s_b, 0):
                                gap = abs(TIME_SLOT_HOURS[s_a] - TIME_SLOT_HOURS[s_b])
                                if gap < min_interval:
                                    current_ok = False

            if severity == "high":
                pattern = "严格分开时段使用，建议间隔至少12小时（如早C晚A模式）"
            elif severity == "medium":
                pattern = "建议不同时段使用，间隔至少8小时"
            else:
                pattern = "可同日使用，注意观察皮肤反应"

            windows.append(AlternationWindow(
                ingredient_a=ing_a,
                ingredient_b=ing_b,
                conflict_type=conflict_type,
                min_interval_hours=min_interval,
                recommended_pattern=pattern,
                current_plan_ok=current_ok,
                description=conflict["description"]
            ))
            if not current_ok:
                stats_store.record_risk_warning(f"交替窗口冲突-{ing_a}/{ing_b}")

        return windows

    @staticmethod
    def _calculate_restart_advices(
        products: List[RegimenProduct],
        total_weeks: int,
        is_sensitive: bool
    ) -> List[RestartAdvice]:
        advices: List[RestartAdvice] = []

        for ing_name, config in HIGH_IRRITATION_INGREDIENTS.items():
            if not config["need_rest"]:
                continue

            total_weeks_used = 0
            for p in products:
                canonical = RegimenPlanner._canonicalize_ingredients(p.ingredient_list)
                if any(i.lower() == ing_name.lower() for i in canonical):
                    end_w = p.end_week or total_weeks
                    used = end_w - p.start_week + 1
                    total_weeks_used = max(total_weeks_used, used)

            max_continuous = 4 if is_sensitive else 6
            if total_weeks_used >= max_continuous:
                stop_week = min(max_continuous, total_weeks_used)
                rest_weeks = config["rest_weeks"]
                restart_week = stop_week + rest_weeks + 1

                advices.append(RestartAdvice(
                    ingredient_name=ing_name,
                    stop_week=stop_week,
                    rest_weeks=rest_weeks,
                    restart_week=restart_week if restart_week <= total_weeks else None,
                    reason=f"{ing_name}连续使用超过{max_continuous}周，皮肤屏障需要休息，避免过度刺激导致敏感泛红",
                    restart_tips=[
                        f"停用期间使用修复类成分（神经酰胺、积雪草、泛醇）",
                        "注意保湿和防晒，避免紫外线损伤",
                        f"恢复使用时从每周2次开始，逐步增加频率",
                        "若出现刺痛泛红，立即停用并加强舒缓修复"
                    ]
                ))
                stats_store.record_risk_warning(f"停用恢复建议-{ing_name}")

        return advices

    @staticmethod
    def _build_plan_days(
        products: List[RegimenProduct],
        total_weeks: int,
        alternation_windows: List[AlternationWindow]
    ) -> List[DailyCareItem]:
        plan_items: List[DailyCareItem] = []
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        start_date = datetime.now().date()
        conflict_notes_map: Dict[Tuple[str, str], List[str]] = defaultdict(list)
        for w in alternation_windows:
            if not w.current_plan_ok:
                conflict_notes_map[(w.ingredient_a.lower(), w.ingredient_b.lower())].append(
                    f"注意：{w.ingredient_a}与{w.ingredient_b}需间隔至少{w.min_interval_hours}小时"
                )

        for week in range(1, total_weeks + 1):
            for day in range(7):
                current_date = start_date + timedelta(days=(week - 1) * 7 + day)
                weekday = weekdays[day]

                daily_products: List[Tuple[RegimenProduct, str]] = []
                for p in products:
                    if not RegimenPlanner._is_product_active_on_day(p, day, week):
                        continue
                    slots = RegimenPlanner._get_product_effective_slots(p)
                    for slot in slots:
                        daily_products.append((p, slot))

                daily_products.sort(key=lambda x: (
                    {"morning": 0, "evening": 1, "weekly": 2}.get(x[1], 99),
                    x[0].order_index
                ))

                for idx, (product, slot) in enumerate(daily_products, 1):
                    canonical = RegimenPlanner._canonicalize_ingredients(product.ingredient_list)
                    notes: List[str] = []

                    for ing in canonical:
                        for (a, b), note_list in conflict_notes_map.items():
                            if ing.lower() == a or ing.lower() == b:
                                notes.extend(note_list)

                    if week == 1 and any(i.lower() in ["视黄醇", "水杨酸", "果酸"] for i in canonical):
                        notes.append("第1周建立耐受，建议从少量开始使用")

                    if slot == "weekly":
                        notes.append("周护理产品，建议选择周末时间充裕时使用")

                    plan_items.append(DailyCareItem(
                        date=current_date.strftime("%Y-%m-%d"),
                        weekday=weekday,
                        time_slot=slot,
                        order_index=idx,
                        product_name=product.product_name,
                        ingredients=list(canonical),
                        notes=list(dict.fromkeys(notes))
                    ))

        return plan_items

    @staticmethod
    def _calculate_stage_warnings(
        accumulation_risks: List[IngredientAccumulationRisk],
        tolerance_curves: List[ToleranceCurve],
        total_weeks: int,
        skin_type: str
    ) -> List[StageRiskWarning]:
        warnings: List[StageRiskWarning] = []

        if total_weeks <= 2:
            stages = [("启动期", 1, total_weeks)]
        elif total_weeks <= 4:
            stages = [("启动期", 1, 1), ("建立期", 2, total_weeks)]
        else:
            stages = [
                ("启动期", 1, 2),
                ("建立期", 3, max(3, total_weeks // 2)),
                ("维持期", max(3, total_weeks // 2) + 1, total_weeks)
            ]

        for stage_name, start_w, end_w in stages:
            stage_risks: List[str] = []
            triggered_ings: Set[str] = set()
            risk_score = 0

            for risk in accumulation_risks:
                if risk.risk_level in ["high", "critical"]:
                    stage_risks.append(risk.description)
                    triggered_ings.add(risk.ingredient_name)
                    risk_score += {"low": 5, "medium": 15, "high": 30, "critical": 50}[risk.risk_level]

            for tc in tolerance_curves:
                relevant_points = [p for p in tc.points if start_w <= p.week <= end_w]
                if relevant_points:
                    worst = min(p.tolerance_score for p in relevant_points)
                    if worst < 50:
                        stage_risks.append(f"{tc.ingredient_name}耐受建立不足，可能刺激")
                        triggered_ings.add(tc.ingredient_name)
                        risk_score += 25

            if risk_score >= 70:
                level = "critical"
            elif risk_score >= 45:
                level = "high"
            elif risk_score >= 20:
                level = "medium"
            else:
                level = "low"

            if level != "low":
                actions = []
                if stage_name == "启动期":
                    actions.append("从低频率少量开始，建立皮肤耐受")
                    actions.append("配合修复保湿产品，加强屏障保护")
                elif stage_name == "建立期":
                    actions.append("观察皮肤反应，出现刺痛泛红立即减量")
                    actions.append("保持充足防晒，避免光敏反应")
                else:
                    actions.append("维持当前使用节奏，定期观察皮肤状态")
                    actions.append("可考虑周期性停用刺激性成分让皮肤休息")

                actions.append("如有不适及时调整方案，必要时咨询皮肤科医生")

                warnings.append(StageRiskWarning(
                    stage=stage_name,
                    start_week=start_w,
                    end_week=end_w,
                    risk_level=level,
                    risk_type="成分刺激累积" if not stage_risks else stage_risks[0],
                    description=f"{stage_name}（第{start_w}-{end_w}周）综合风险：{'；'.join(stage_risks) if stage_risks else '需关注皮肤状态'}",
                    triggered_ingredients=list(triggered_ings),
                    actions=actions
                ))

        return warnings

    @staticmethod
    def _calculate_adjustment_suggestions(
        accumulation_risks: List[IngredientAccumulationRisk],
        tolerance_curves: List[ToleranceCurve],
        alternation_windows: List[AlternationWindow],
        restart_advices: List[RestartAdvice]
    ) -> List[AdjustmentSuggestion]:
        suggestions: List[AdjustmentSuggestion] = []

        for risk in accumulation_risks:
            if risk.risk_level == "critical":
                suggestions.append(AdjustmentSuggestion(
                    priority="critical",
                    category="累积风险",
                    current_plan=f"{risk.ingredient_name} 每日{risk.daily_exposure_count}次/每周{risk.weekly_exposure_count}次",
                    suggested_plan=f"降低{risk.ingredient_name}使用频率至每日1次以内，每周不超过{ACCUMULATION_THRESHOLDS.get(risk.ingredient_name, {}).get('weekly', 4)}次",
                    reason=risk.description,
                    impact_scope=risk.affected_time_slots
                ))
            elif risk.risk_level == "high":
                suggestions.append(AdjustmentSuggestion(
                    priority="high",
                    category="累积风险",
                    current_plan=f"{risk.ingredient_name} 每日{risk.daily_exposure_count}次",
                    suggested_plan=f"适当减少{risk.ingredient_name}使用频率，搭配舒缓修复成分",
                    reason=risk.description,
                    impact_scope=risk.affected_time_slots
                ))

        for tc in tolerance_curves:
            if not tc.is_tolerated:
                suggestions.append(AdjustmentSuggestion(
                    priority="high",
                    category="耐受建立",
                    current_plan=f"{tc.ingredient_name} 当前耐受度{tc.current_score}%",
                    suggested_plan=f"从每周2-3次开始逐步增加，配合神经酰胺/积雪草修复",
                    reason=f"{tc.ingredient_name}耐受建立不足，直接高频使用易引发刺激",
                    impact_scope=["morning", "evening"]
                ))

        for w in alternation_windows:
            if not w.current_plan_ok:
                suggestions.append(AdjustmentSuggestion(
                    priority="high" if w.min_interval_hours >= 12 else "medium",
                    category="交替窗口",
                    current_plan=f"{w.ingredient_a} 与 {w.ingredient_b} 使用时段安排过近",
                    suggested_plan=w.recommended_pattern,
                    reason=w.description,
                    impact_scope=["morning", "evening"]
                ))

        for ra in restart_advices:
            suggestions.append(AdjustmentSuggestion(
                priority="high",
                category="停用恢复",
                current_plan=f"{ra.ingredient_name} 连续使用计划超过安全周数",
                suggested_plan=f"第{ra.stop_week}周后停用{ra.rest_weeks}周，第{ra.restart_week}周再恢复使用",
                reason=ra.reason,
                impact_scope=["morning", "evening", "weekly"]
            ))

        suggestions.sort(key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x.priority])
        return suggestions

    @staticmethod
    def generate_regimen_plan(request: RegimenPlanRequest) -> RegimenPlanResult:
        skin_type = request.skin_profile.skin_type
        is_sensitive = request.skin_profile.is_sensitive
        total_weeks = request.total_weeks
        products = request.products

        (
            daily_exposure,
            weekly_exposure,
            slot_ingredients,
            ingredient_usage_details
        ) = RegimenPlanner._build_ingredient_exposure(products, total_weeks)

        accumulation_risks = RegimenPlanner._calculate_accumulation_risks(
            daily_exposure, weekly_exposure, slot_ingredients, skin_type, is_sensitive
        )

        tolerance_curves = RegimenPlanner._calculate_tolerance_curves(
            ingredient_usage_details, total_weeks, is_sensitive
        )

        alternation_windows = RegimenPlanner._calculate_alternation_windows(products, total_weeks)

        restart_advices = RegimenPlanner._calculate_restart_advices(products, total_weeks, is_sensitive)

        plan_days = RegimenPlanner._build_plan_days(products, total_weeks, alternation_windows)

        stage_warnings = RegimenPlanner._calculate_stage_warnings(
            accumulation_risks, tolerance_curves, total_weeks, skin_type
        )

        adjustment_suggestions = RegimenPlanner._calculate_adjustment_suggestions(
            accumulation_risks, tolerance_curves, alternation_windows, restart_advices
        )

        risk_scores = []
        for r in accumulation_risks:
            risk_scores.append(r.risk_score)
        for tc in tolerance_curves:
            if not tc.is_tolerated:
                risk_scores.append(100 - tc.current_score)
        for w in alternation_windows:
            if not w.current_plan_ok:
                risk_scores.append(30 if w.min_interval_hours >= 12 else 15)
        for ra in restart_advices:
            risk_scores.append(25)

        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        if avg_risk >= 70:
            overall_risk = "critical"
        elif avg_risk >= 45:
            overall_risk = "high"
        elif avg_risk >= 20:
            overall_risk = "medium"
        else:
            overall_risk = "low"

        overall_score = round(max(0.0, 100.0 - avg_risk), 1)

        summary_parts = [f"疗程共{total_weeks}周，包含{len(products)}款产品"]
        if accumulation_risks:
            high_risk_ings = [r.ingredient_name for r in accumulation_risks if r.risk_level in ["high", "critical"]]
            if high_risk_ings:
                summary_parts.append(f"发现{len(high_risk_ings)}项高累积风险成分：{', '.join(high_risk_ings)}")
        if alternation_windows:
            bad_windows = [w for w in alternation_windows if not w.current_plan_ok]
            if bad_windows:
                summary_parts.append(f"发现{len(bad_windows)}组成分时序冲突")
        untolerated = [tc.ingredient_name for tc in tolerance_curves if not tc.is_tolerated]
        if untolerated:
            summary_parts.append(f"{', '.join(untolerated)}需建立耐受")

        if not any("高" in p or "冲突" in p for p in summary_parts[1:]):
            summary_parts.append("方案整体风险可控，按计划执行即可")

        regimen_id = uuid.uuid4().hex
        stats_store.register_regimen_id(regimen_id)
        stats_store.record_regimen_generated(len(products) >= 3)
        stats_store.record_analysis(skin_type=skin_type)

        all_ings: Set[str] = set()
        for p in products:
            all_ings.update(RegimenPlanner._canonicalize_ingredients(p.ingredient_list))
        stats_store.record_ingredient_usage(list(all_ings))

        return RegimenPlanResult(
            regimen_id=regimen_id,
            total_weeks=total_weeks,
            skin_type=skin_type,
            plan_days=plan_days,
            accumulation_risks=accumulation_risks,
            tolerance_curves=tolerance_curves,
            alternation_windows=alternation_windows,
            restart_advices=restart_advices,
            stage_warnings=stage_warnings,
            adjustment_suggestions=adjustment_suggestions,
            overall_risk_level=overall_risk,
            overall_score=overall_score,
            summary="；".join(summary_parts)
        )

    @staticmethod
    def track_regimen(request: RegimenTrackRequest) -> RegimenTrackResult:
        warnings_triggered: List[str] = []
        adjustment_details: List[str] = []
        adjusted = False

        if request.acne_occurred:
            warnings_triggered.append("爆痘预警")
            adjustment_details.append("出现爆痘，建议暂停酸类/视黄醇等刺激性成分，加强抗菌消炎护理")
            adjusted = True
            stats_store.record_risk_warning("疗程阶段爆痘")

        if request.sensitivity_occurred:
            warnings_triggered.append("敏感预警")
            adjustment_details.append("出现敏感，建议精简护肤，只用修复保湿类产品，避开所有刺激性成分")
            adjusted = True
            stats_store.record_risk_warning("疗程阶段敏感")

        if request.adjusted_products:
            adjusted = True
            adjustment_details.append(f"已主动调整产品：{', '.join(request.adjusted_products)}")
            stats_store.record_regimen_adjustment()

        completion_rate = round(min(100.0, request.completed_days / 7 * 100), 1) if request.completed_days <= 7 else 100.0

        total_weeks_info = stats_store.get_regimen_info(request.regimen_id)
        total_weeks = total_weeks_info.get("total_weeks", 4) if total_weeks_info else 4

        if request.week <= max(2, total_weeks // 3):
            stage = "启动期"
        elif request.week <= max(3, (total_weeks * 2) // 3):
            stage = "建立期"
        else:
            stage = "维持期"

        next_week_advice = []
        if completion_rate < 70:
            next_week_advice.append("本周完成度较低，下周尽量保持规律护肤节奏")
        if request.acne_occurred:
            next_week_advice.append("下周重点控油抗菌，可使用水杨酸/茶树精油局部点涂，避免厚重产品")
        if request.sensitivity_occurred:
            next_week_advice.append("下周继续精简修复，使用神经酰胺、积雪草、泛醇，避免功效成分")
        if completion_rate >= 85 and not warnings_triggered:
            next_week_advice.append("状态良好，可按计划继续执行，注意保持防晒")
        if stage == "建立期":
            next_week_advice.append("耐受建立关键期，注意观察皮肤反应，不要贸然加量")

        if not next_week_advice:
            next_week_advice.append("保持当前护理节奏，持续观察皮肤状态")

        track_id = uuid.uuid4().hex
        stats_store.record_regimen_track(
            regimen_id=request.regimen_id,
            week=request.week,
            completion_rate=completion_rate,
            acne=request.acne_occurred,
            sensitivity=request.sensitivity_occurred,
            adjusted=adjusted
        )

        return RegimenTrackResult(
            track_id=track_id,
            regimen_id=request.regimen_id,
            week=request.week,
            completion_rate=completion_rate,
            stage=stage,
            warnings_triggered=warnings_triggered,
            adjusted=adjusted,
            adjustment_details=adjustment_details,
            next_week_advice=next_week_advice
        )
