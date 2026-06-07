from typing import Dict, List, Set
from collections import defaultdict
from datetime import datetime


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
        self.adaptability_feedback_ids: Set[str] = set()
        self.risk_warning_count: Dict[str, int] = defaultdict(int)
        self.total_schemes_generated: int = 0
        self.schemes_adopted_count: int = 0
        self.adopted_scheme_ids: Set[str] = set()
        self.conflict_detected_count: int = 0
        self.analysis_by_skin_type: Dict[str, int] = defaultdict(int)
        self.suggestions_by_season: Dict[str, int] = defaultdict(int)
        self.analysis_dates: List[str] = []
    
    def record_ingredient_usage(self, ingredient_names: List[str]):
        for name in ingredient_names:
            self.ingredient_usage_count[name] += 1
    
    def record_analysis(self, skin_type: str = None):
        self.total_analyses += 1
        if skin_type:
            self.analysis_by_skin_type[skin_type] += 1
        self.analysis_dates.append(datetime.now().strftime("%Y-%m-%d"))
    
    def record_adaptability_calculation(self):
        self.total_adaptability_calculations += 1
    
    def record_adaptability_feedback(self, is_correct: bool, calculation_id: str = None) -> bool:
        if calculation_id:
            dedup_key = f"feedback:{calculation_id}"
            if dedup_key in self.adaptability_feedback_ids:
                return False
            self.adaptability_feedback_ids.add(dedup_key)
        if is_correct:
            self.correct_adaptability_count += 1
        return True
    
    def record_risk_warning(self, risk_type: str):
        self.risk_warning_count[risk_type] += 1
    
    def record_scheme_generated(self):
        self.total_schemes_generated += 1
    
    def record_scheme_adopted(self, suggestion_id: str = None) -> bool:
        if suggestion_id:
            dedup_key = f"adopt:{suggestion_id}"
            if dedup_key in self.adopted_scheme_ids:
                return False
            self.adopted_scheme_ids.add(dedup_key)
        if self.schemes_adopted_count < self.total_schemes_generated:
            self.schemes_adopted_count += 1
            return True
        return False
    
    def record_conflict_detected(self):
        self.conflict_detected_count += 1
    
    def record_suggestion_by_season(self, season: str):
        self.suggestions_by_season[season] += 1
    
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
        return {
            "accuracy": round(self.correct_adaptability_count / self.total_adaptability_calculations * 100, 2),
            "total": self.total_adaptability_calculations,
            "correct": self.correct_adaptability_count
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
        return {
            "adoption_rate": round(self.schemes_adopted_count / self.total_schemes_generated * 100, 2),
            "total": self.total_schemes_generated,
            "adopted": self.schemes_adopted_count
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
