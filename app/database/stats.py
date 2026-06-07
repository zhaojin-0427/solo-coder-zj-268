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
            "scheme_adoption": self.get_scheme_adoption_rate()
        }


stats_store = StatisticsStore()
