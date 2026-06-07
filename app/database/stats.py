import json
import os
from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime


PERSISTENCE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "stats_data.json"
)
PERSISTENCE_FILE = os.path.normpath(PERSISTENCE_FILE)


class StatisticsStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.ingredient_usage_count: Dict[str, int] = defaultdict(int)
        self.total_analyses: int = 0
        self.total_adaptability_calculations: int = 0
        self.correct_adaptability_count: int = 0
        self.issued_calculation_ids: Set[str] = set()
        self.adaptability_feedback_ids: Set[str] = set()
        self.risk_warning_count: Dict[str, int] = defaultdict(int)
        self.total_schemes_generated: int = 0
        self.schemes_adopted_count: int = 0
        self.issued_suggestion_ids: Set[str] = set()
        self.adopted_scheme_ids: Set[str] = set()
        self.conflict_detected_count: int = 0
        self.analysis_by_skin_type: Dict[str, int] = defaultdict(int)
        self.suggestions_by_season: Dict[str, int] = defaultdict(int)
        self.analysis_dates: List[str] = []
        self.total_regimens_generated: int = 0
        self.total_regimens_completed: int = 0
        self.issued_regimen_ids: Set[str] = set()
        self.regimen_info: Dict[str, Dict] = {}
        self.adopted_regimen_ids: Set[str] = set()
        self.multi_product_regimens_count: int = 0
        self.multi_product_adopted_count: int = 0
        self.total_regimen_tracks: int = 0
        self.regimen_acne_warnings: int = 0
        self.regimen_sensitivity_warnings: int = 0
        self.regimen_adjustment_count: int = 0
        self.regimen_completion_sum: float = 0.0
        self._load_from_disk()

    def _to_serializable(self) -> dict:
        return {
            "ingredient_usage_count": dict(self.ingredient_usage_count),
            "total_analyses": self.total_analyses,
            "total_adaptability_calculations": self.total_adaptability_calculations,
            "correct_adaptability_count": self.correct_adaptability_count,
            "issued_calculation_ids": list(self.issued_calculation_ids),
            "adaptability_feedback_ids": list(self.adaptability_feedback_ids),
            "risk_warning_count": dict(self.risk_warning_count),
            "total_schemes_generated": self.total_schemes_generated,
            "schemes_adopted_count": self.schemes_adopted_count,
            "issued_suggestion_ids": list(self.issued_suggestion_ids),
            "adopted_scheme_ids": list(self.adopted_scheme_ids),
            "conflict_detected_count": self.conflict_detected_count,
            "analysis_by_skin_type": dict(self.analysis_by_skin_type),
            "suggestions_by_season": dict(self.suggestions_by_season),
            "analysis_dates": self.analysis_dates,
            "total_regimens_generated": self.total_regimens_generated,
            "total_regimens_completed": self.total_regimens_completed,
            "issued_regimen_ids": list(self.issued_regimen_ids),
            "regimen_info": self.regimen_info,
            "adopted_regimen_ids": list(self.adopted_regimen_ids),
            "multi_product_regimens_count": self.multi_product_regimens_count,
            "multi_product_adopted_count": self.multi_product_adopted_count,
            "total_regimen_tracks": self.total_regimen_tracks,
            "regimen_acne_warnings": self.regimen_acne_warnings,
            "regimen_sensitivity_warnings": self.regimen_sensitivity_warnings,
            "regimen_adjustment_count": self.regimen_adjustment_count,
            "regimen_completion_sum": self.regimen_completion_sum,
        }

    def _from_serializable(self, data: dict):
        self.ingredient_usage_count = defaultdict(int, data.get("ingredient_usage_count", {}))
        self.total_analyses = data.get("total_analyses", 0)
        self.total_adaptability_calculations = data.get("total_adaptability_calculations", 0)
        self.correct_adaptability_count = data.get("correct_adaptability_count", 0)
        self.issued_calculation_ids = set(data.get("issued_calculation_ids", []))
        self.adaptability_feedback_ids = set(data.get("adaptability_feedback_ids", []))
        self.risk_warning_count = defaultdict(int, data.get("risk_warning_count", {}))
        self.total_schemes_generated = data.get("total_schemes_generated", 0)
        self.schemes_adopted_count = data.get("schemes_adopted_count", 0)
        self.issued_suggestion_ids = set(data.get("issued_suggestion_ids", []))
        self.adopted_scheme_ids = set(data.get("adopted_scheme_ids", []))
        self.conflict_detected_count = data.get("conflict_detected_count", 0)
        self.analysis_by_skin_type = defaultdict(int, data.get("analysis_by_skin_type", {}))
        self.suggestions_by_season = defaultdict(int, data.get("suggestions_by_season", {}))
        self.analysis_dates = data.get("analysis_dates", [])
        self.total_regimens_generated = data.get("total_regimens_generated", 0)
        self.total_regimens_completed = data.get("total_regimens_completed", 0)
        self.issued_regimen_ids = set(data.get("issued_regimen_ids", []))
        self.regimen_info = data.get("regimen_info", {})
        self.adopted_regimen_ids = set(data.get("adopted_regimen_ids", []))
        self.multi_product_regimens_count = data.get("multi_product_regimens_count", 0)
        self.multi_product_adopted_count = data.get("multi_product_adopted_count", 0)
        self.total_regimen_tracks = data.get("total_regimen_tracks", 0)
        self.regimen_acne_warnings = data.get("regimen_acne_warnings", 0)
        self.regimen_sensitivity_warnings = data.get("regimen_sensitivity_warnings", 0)
        self.regimen_adjustment_count = data.get("regimen_adjustment_count", 0)
        self.regimen_completion_sum = float(data.get("regimen_completion_sum", 0.0))

    def _persist(self):
        try:
            with open(PERSISTENCE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._to_serializable(), f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_from_disk(self):
        try:
            if os.path.exists(PERSISTENCE_FILE):
                with open(PERSISTENCE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._from_serializable(data)
        except Exception:
            pass

    def register_calculation_id(self, calculation_id: str):
        self.issued_calculation_ids.add(calculation_id)
        self._persist()

    def register_suggestion_id(self, suggestion_id: str):
        self.issued_suggestion_ids.add(suggestion_id)
        self._persist()

    def record_ingredient_usage(self, ingredient_names: List[str]):
        for name in ingredient_names:
            self.ingredient_usage_count[name] += 1
        self._persist()

    def record_analysis(self, skin_type: str = None):
        self.total_analyses += 1
        if skin_type:
            self.analysis_by_skin_type[skin_type] += 1
        self.analysis_dates.append(datetime.now().strftime("%Y-%m-%d"))
        self._persist()

    def record_adaptability_calculation(self):
        self.total_adaptability_calculations += 1
        self._persist()

    def record_adaptability_feedback(self, is_correct: bool, calculation_id: str = None) -> int:
        if calculation_id:
            if calculation_id not in self.issued_calculation_ids:
                return -1
            dedup_key = f"feedback:{calculation_id}"
            if dedup_key in self.adaptability_feedback_ids:
                return 0
            self.adaptability_feedback_ids.add(dedup_key)
        else:
            return -1

        if is_correct and self.correct_adaptability_count < self.total_adaptability_calculations:
            self.correct_adaptability_count += 1

        self._persist()
        return 1

    def record_risk_warning(self, risk_type: str):
        self.risk_warning_count[risk_type] += 1
        self._persist()

    def record_scheme_generated(self):
        self.total_schemes_generated += 1
        self._persist()

    def record_scheme_adopted(self, suggestion_id: str = None) -> int:
        if suggestion_id:
            if suggestion_id not in self.issued_suggestion_ids:
                return -1
            dedup_key = f"adopt:{suggestion_id}"
            if dedup_key in self.adopted_scheme_ids:
                return 0
            self.adopted_scheme_ids.add(dedup_key)
        else:
            return -1

        if self.schemes_adopted_count < self.total_schemes_generated:
            self.schemes_adopted_count += 1
            self._persist()
            return 1
        return 0

    def record_conflict_detected(self):
        self.conflict_detected_count += 1
        self._persist()

    def record_suggestion_by_season(self, season: str):
        self.suggestions_by_season[season] += 1
        self._persist()

    def get_hot_ingredients(self, top_n: int = 10) -> List[Dict]:
        sorted_items = sorted(
            self.ingredient_usage_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        total = max(sum(self.ingredient_usage_count.values()), 1)
        return [
            {
                "name": name,
                "count": count,
                "percentage": round(count / total * 100, 2)
            }
            for name, count in sorted_items
        ]

    def get_adaptability_accuracy(self) -> Dict:
        if self.total_adaptability_calculations == 0:
            return {"accuracy": 0, "total": 0, "correct": 0}
        accuracy = round(min(self.correct_adaptability_count, self.total_adaptability_calculations) / self.total_adaptability_calculations * 100, 2)
        return {
            "accuracy": accuracy,
            "total": self.total_adaptability_calculations,
            "correct": min(self.correct_adaptability_count, self.total_adaptability_calculations)
        }

    def get_risk_warning_stats(self) -> List[Dict]:
        return [
            {"type": rtype, "count": count}
            for rtype, count in sorted(
                self.risk_warning_count.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

    def get_scheme_adoption_rate(self) -> Dict:
        if self.total_schemes_generated == 0:
            return {"adoption_rate": 0, "total": 0, "adopted": 0}
        adopted = min(self.schemes_adopted_count, self.total_schemes_generated)
        return {
            "adoption_rate": round(adopted / self.total_schemes_generated * 100, 2),
            "total": self.total_schemes_generated,
            "adopted": adopted
        }

    def get_overview(self) -> Dict:
        return {
            "total_analyses": self.total_analyses,
            "total_conflicts_detected": self.conflict_detected_count,
            "analysis_by_skin_type": dict(self.analysis_by_skin_type),
            "suggestions_by_season": dict(self.suggestions_by_season),
            "hot_ingredients": self.get_hot_ingredients(),
            "adaptability_accuracy": self.get_adaptability_accuracy(),
            "risk_warnings": self.get_risk_warning_stats(),
            "scheme_adoption": self.get_scheme_adoption_rate(),
            "regimen_stats": self.get_regimen_stats()
        }

    def register_regimen_id(self, regimen_id: str, total_weeks: int = 4):
        self.issued_regimen_ids.add(regimen_id)
        self.regimen_info[regimen_id] = {
            "total_weeks": total_weeks,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tracked_weeks": [],
            "completed": False,
            "is_multi_product": False
        }
        self._persist()

    def get_regimen_info(self, regimen_id: str) -> Optional[Dict]:
        return self.regimen_info.get(regimen_id)

    def record_regimen_generated(self, is_multi_product: bool = False):
        self.total_regimens_generated += 1
        if is_multi_product:
            self.multi_product_regimens_count += 1
        self._persist()

    def record_regimen_adopted(self, regimen_id: str) -> int:
        if regimen_id not in self.issued_regimen_ids:
            return -1
        dedup_key = f"adopt_regimen:{regimen_id}"
        if dedup_key in self.adopted_regimen_ids:
            return 0
        self.adopted_regimen_ids.add(dedup_key)
        if self.regimen_info.get(regimen_id, {}).get("is_multi_product"):
            self.multi_product_adopted_count += 1
        self._persist()
        return 1

    def record_regimen_adjustment(self):
        self.regimen_adjustment_count += 1
        self._persist()

    def record_regimen_track(
        self,
        regimen_id: str,
        week: int,
        completion_rate: float,
        acne: bool = False,
        sensitivity: bool = False,
        adjusted: bool = False
    ):
        self.total_regimen_tracks += 1
        self.regimen_completion_sum += completion_rate
        if acne:
            self.regimen_acne_warnings += 1
        if sensitivity:
            self.regimen_sensitivity_warnings += 1
        if regimen_id in self.regimen_info:
            tracked = self.regimen_info[regimen_id].get("tracked_weeks", [])
            if week not in tracked:
                tracked.append(week)
                self.regimen_info[regimen_id]["tracked_weeks"] = tracked
            total_w = self.regimen_info[regimen_id].get("total_weeks", 4)
            if len(tracked) >= total_w and completion_rate >= 70:
                if not self.regimen_info[regimen_id].get("completed"):
                    self.regimen_info[regimen_id]["completed"] = True
                    self.total_regimens_completed += 1
        self._persist()

    def get_regimen_completion_rate(self) -> Dict:
        if self.total_regimens_generated == 0:
            return {"completion_rate": 0, "total": 0, "completed": 0}
        completed = min(self.total_regimens_completed, self.total_regimens_generated)
        return {
            "completion_rate": round(completed / self.total_regimens_generated * 100, 2),
            "total": self.total_regimens_generated,
            "completed": completed,
            "avg_weekly_completion": round(
                self.regimen_completion_sum / max(1, self.total_regimen_tracks), 2
            )
        }

    def get_regimen_risk_warnings(self) -> Dict:
        return {
            "acne_warning_count": self.regimen_acne_warnings,
            "sensitivity_warning_count": self.regimen_sensitivity_warnings,
            "total_risk_warnings": self.regimen_acne_warnings + self.regimen_sensitivity_warnings,
            "breakdown": [
                {"type": "爆痘预警", "count": self.regimen_acne_warnings},
                {"type": "敏感预警", "count": self.regimen_sensitivity_warnings}
            ]
        }

    def get_regimen_adjustment_rate(self) -> Dict:
        if self.total_regimen_tracks == 0:
            return {"adjustment_trigger_rate": 0, "total_tracks": 0, "adjustments": 0}
        return {
            "adjustment_trigger_rate": round(
                self.regimen_adjustment_count / max(1, self.total_regimen_tracks) * 100, 2
            ),
            "total_tracks": self.total_regimen_tracks,
            "adjustments": self.regimen_adjustment_count
        }

    def get_multi_product_adoption_rate(self) -> Dict:
        if self.multi_product_regimens_count == 0:
            return {"multi_product_adoption_rate": 0, "total_multi_product": 0, "adopted": 0}
        adopted = min(self.multi_product_adopted_count, self.multi_product_regimens_count)
        return {
            "multi_product_adoption_rate": round(
                adopted / self.multi_product_regimens_count * 100, 2
            ),
            "total_multi_product": self.multi_product_regimens_count,
            "adopted": adopted
        }

    def get_regimen_stats(self) -> Dict:
        completion = self.get_regimen_completion_rate()
        risk_warnings = self.get_regimen_risk_warnings()
        adjustment = self.get_regimen_adjustment_rate()
        multi_adoption = self.get_multi_product_adoption_rate()
        return {
            "total_regimens": self.total_regimens_generated,
            "completed_regimens": self.total_regimens_completed,
            "completion_rate": completion["completion_rate"],
            "avg_weekly_completion": completion["avg_weekly_completion"],
            "total_tracks": self.total_regimen_tracks,
            "acne_warning_count": risk_warnings["acne_warning_count"],
            "sensitivity_warning_count": risk_warnings["sensitivity_warning_count"],
            "total_risk_warnings": risk_warnings["total_risk_warnings"],
            "adjustment_trigger_count": self.regimen_adjustment_count,
            "adjustment_trigger_rate": adjustment["adjustment_trigger_rate"],
            "multi_product_regimens": self.multi_product_regimens_count,
            "multi_product_adopted": self.multi_product_adopted_count,
            "multi_product_adoption_rate": multi_adoption["multi_product_adoption_rate"]
        }


stats_store = StatisticsStore()
