from typing import List, Optional
from app.database.ingredients import (
    SEASONAL_ADVICE,
    SKIN_TYPE_PROFILES,
    ACTIVE_INGREDIENTS,
    get_ingredient_info
)
from app.schemas import (
    SkinProfile,
    SuggestionRequest,
    SeasonalTip,
    DailyRoutine,
    SuggestionResult
)
from app.utils.helpers import detect_season
from app.database.stats import stats_store


class SuggestionEngine:
    
    @staticmethod
    def generate_suggestions(request: SuggestionRequest) -> SuggestionResult:
        skin_profile = request.skin_profile
        skin_type = skin_profile.skin_type
        is_sensitive = skin_profile.is_sensitive
        current_ingredients = request.current_ingredients or []
        
        season = request.season or detect_season()
        if season not in SEASONAL_ADVICE:
            season = detect_season()
        
        seasonal_data = SEASONAL_ADVICE[season]
        skin_profile_data = SKIN_TYPE_PROFILES.get(skin_type, SKIN_TYPE_PROFILES["中性"])
        
        skin_specific = seasonal_data["skin_specific"].get(
            skin_type,
            seasonal_data["general_tips"]
        )
        
        seasonal_tip = SeasonalTip(
            season=season,
            general_tips=seasonal_data["general_tips"],
            skin_specific=skin_specific,
            recommended_ingredients=seasonal_data["recommended_ingredients"],
            avoid_ingredients=seasonal_data["avoid_ingredients"]
        )
        
        current_canonical = set()
        for ing in current_ingredients:
            info = get_ingredient_info(ing)
            if info:
                current_canonical.add(info["name"])
        
        preferred_ingredients = skin_profile_data["preferred_ingredients"]
        avoid_ingredients = skin_profile_data["avoid_ingredients"]
        key_needs = skin_profile_data["key_needs"]
        
        morning_routine = SuggestionEngine._get_morning_routine(
            skin_type, season, is_sensitive
        )
        evening_routine = SuggestionEngine._get_evening_routine(
            skin_type, season, is_sensitive
        )
        weekly_routine = SuggestionEngine._get_weekly_routine(
            skin_type, season, is_sensitive
        )
        
        daily_routine = DailyRoutine(
            morning=morning_routine,
            evening=evening_routine,
            weekly=weekly_routine
        )
        
        recommendations: List[dict] = []
        recommended_pool = list(preferred_ingredients)
        for si in seasonal_data["recommended_ingredients"]:
            if si not in recommended_pool:
                recommended_pool.append(si)
        
        for ing_name in recommended_pool:
            if ing_name in current_canonical:
                continue
            if ing_name in avoid_ingredients:
                continue
            if is_sensitive and ing_name in ["果酸", "水杨酸", "视黄醇"]:
                continue
            
            ing_data = ACTIVE_INGREDIENTS.get(ing_name)
            if ing_data:
                matched_needs = [b for b in ing_data["benefits"] if b in key_needs]
                recommendations.append({
                    "name": ing_name,
                    "benefits": ing_data["benefits"],
                    "matched_needs": matched_needs,
                    "priority": "高" if len(matched_needs) >= 2 else "中" if matched_needs else "低"
                })
        
        recommendations.sort(key=lambda x: {"高": 0, "中": 1, "低": 2}[x["priority"]])
        recommendations = recommendations[:6]
        
        notes: List[str] = []
        notes.append(f"当前季节：{season}，注意{seasonal_data['keywords'][0]}相关的护肤问题")
        
        if is_sensitive:
            notes.append("敏感肌建议使用前先在耳后或小臂内侧做皮肤测试")
            notes.append("换季期间精简护肤，减少成分叠加")
        
        if skin_type in ["干性", "成熟肌"] and season in ["秋季", "冬季"]:
            notes.append("干燥季节建议多层保湿，可叠加精华+面霜+护肤油")
        
        if skin_type in ["油性", "痘痘"] and season in ["夏季"]:
            notes.append("夏季出油多，注意及时清洁，可适当增加酸类产品使用频率")
        
        if current_ingredients:
            for ai in avoid_ingredients:
                for ci in current_ingredients:
                    ci_info = get_ingredient_info(ci)
                    if ci_info and ci_info["name"] == ai:
                        notes.append(f"注意：您当前使用的产品中含有{ai}，这是{skin_type}肤质应避开的成分")
        
        stats_store.record_suggestion_by_season(season)
        stats_store.record_analysis(skin_type=skin_type)
        stats_store.record_scheme_generated()
        
        return SuggestionResult(
            seasonal_tip=seasonal_tip,
            daily_routine=daily_routine,
            ingredient_recommendations=recommendations,
            notes=notes
        )
    
    @staticmethod
    def _get_morning_routine(skin_type: str, season: str, is_sensitive: bool) -> List[str]:
        base = ["温和洁面", "爽肤水/化妆水"]
        
        if skin_type in ["干性", "敏感性", "成熟肌"]:
            base.append("保湿精华（玻尿酸/神经酰胺）")
        elif skin_type in ["油性", "痘痘", "混合性"]:
            base.append("控油/修护精华（烟酰胺）")
        else:
            base.append("基础精华")
        
        if season in ["春季", "夏季"]:
            if not is_sensitive:
                base.append("抗氧化精华（维生素C）")
            else:
                base.append("舒缓精华（积雪草/泛醇）")
        
        if skin_type in ["干性", "成熟肌"]:
            if season in ["秋季", "冬季"]:
                base.append("滋润面霜")
            else:
                base.append("保湿乳液/面霜")
        elif skin_type in ["油性", "痘痘"]:
            base.append("清爽乳液/凝胶")
        else:
            base.append("保湿乳液")
        
        base.append("防晒（四季必备）")
        return base
    
    @staticmethod
    def _get_evening_routine(skin_type: str, season: str, is_sensitive: bool) -> List[str]:
        base = ["卸妆（如化妆）", "洁面"]
        
        if skin_type in ["油性", "痘痘", "混合性"] and season in ["夏季"]:
            base.append("二次清洁水")
        
        base.append("爽肤水/化妆水")
        
        if skin_type in ["成熟肌", "暗沉"] and not is_sensitive:
            base.append("抗老/美白精华（视黄醇/胜肽/熊果苷）")
        elif skin_type in ["干性", "敏感性"]:
            base.append("修复精华（神经酰胺/积雪草）")
        else:
            base.append("功效精华")
        
        if season in ["秋季", "冬季"] and skin_type in ["干性", "成熟肌", "敏感性"]:
            base.append("护肤油（可选）")
        
        if skin_type in ["干性", "成熟肌"]:
            base.append("滋润晚霜")
        elif skin_type in ["油性", "痘痘"]:
            base.append("清爽晚霜/乳液")
        else:
            base.append("晚霜/乳液")
        
        if skin_type in ["干性"] and season in ["冬季"]:
            base.append("唇膜+眼霜")
        else:
            base.append("眼霜")
        
        return base
    
    @staticmethod
    def _get_weekly_routine(skin_type: str, season: str, is_sensitive: bool) -> List[str]:
        routine = []
        
        if not is_sensitive:
            if skin_type in ["油性", "痘痘", "混合性", "暗沉"]:
                if season in ["夏季"]:
                    routine.append("清洁面膜 2-3次/周")
                    routine.append("酸类去角质 1-2次/周（水杨酸/果酸）")
                else:
                    routine.append("清洁面膜 1-2次/周")
                    routine.append("温和去角质 1次/周")
            elif skin_type in ["干性", "成熟肌"]:
                routine.append("保湿面膜 2-3次/周")
                routine.append("温和去角质 1次/2周")
            else:
                routine.append("面膜 1-2次/周")
                routine.append("温和去角质 1次/周")
        else:
            routine.append("舒缓修复面膜 1-2次/周")
            routine.append("避免去角质")
        
        routine.append("彻底防晒复查")
        routine.append("皮肤状态检查，根据状态调整护肤品")
        
        return routine
