import re
from typing import List, Tuple
from app.database.ingredients import (
    get_ingredient_info,
    ACTIVE_INGREDIENTS,
    PRESERVATIVES,
    RISK_INGREDIENTS
)
from app.schemas import IngredientInfo, ParseResult
from app.database.stats import stats_store


class IngredientParser:
    
    @staticmethod
    def split_ingredient_list(text: str) -> List[str]:
        text = text.strip()
        parts = re.split(r'[、,，;；\n\r\t]+', text)
        ingredients = []
        for part in parts:
            part = part.strip()
            if part and not re.match(r'^[\d\s.]+$', part):
                cleaned = re.sub(r'^\d+[\.\)、]\s*', '', part)
                cleaned = cleaned.strip()
                if cleaned:
                    ingredients.append(cleaned)
        return ingredients
    
    @staticmethod
    def parse_ingredients(ingredient_list_text: str) -> ParseResult:
        raw_ingredients = IngredientParser.split_ingredient_list(ingredient_list_text)
        
        active_list: List[IngredientInfo] = []
        preservative_list: List[IngredientInfo] = []
        risk_list: List[IngredientInfo] = []
        unknown_list: List[str] = []
        
        matched_names = set()
        
        for raw_name in raw_ingredients:
            info = get_ingredient_info(raw_name)
            
            if info is None:
                unknown_list.append(raw_name)
                continue
            
            canonical_name = info["name"]
            if canonical_name in matched_names:
                continue
            
            matched_names.add(canonical_name)
            category = info["category"]
            
            ingredient_data = IngredientInfo(
                name=info["name"],
                category=category,
                description=info.get("description"),
                benefits=info.get("benefits"),
                efficacy_score=info.get("efficacy_score"),
                safety_level=info.get("safety_level"),
                risk_level=info.get("risk_level"),
                risk_type=info.get("risk_type"),
                risk_description=info.get("risk_description"),
                skin_types=info.get("skin_types"),
                max_concentration=info.get("max_concentration")
            )
            
            if category == "active":
                active_list.append(ingredient_data)
            elif category == "preservative":
                preservative_list.append(ingredient_data)
            elif category == "risk":
                risk_list.append(ingredient_data)
        
        all_identified_names = [i.name for i in active_list] + \
                               [i.name for i in preservative_list] + \
                               [i.name for i in risk_list]
        
        stats_store.record_ingredient_usage(all_identified_names)
        stats_store.record_analysis()
        
        return ParseResult(
            total_count=len(raw_ingredients),
            active_ingredients=active_list,
            preservatives=preservative_list,
            risk_ingredients=risk_list,
            unknown_ingredients=unknown_list
        )
    
    @staticmethod
    def get_all_active_ingredients() -> List[dict]:
        return [
            {
                "name": name,
                "benefits": data["benefits"],
                "skin_types": data["skin_types"],
                "efficacy_score": data["efficacy_score"],
                "description": data["description"]
            }
            for name, data in ACTIVE_INGREDIENTS.items()
        ]
    
    @staticmethod
    def get_all_preservatives() -> List[dict]:
        return [
            {
                "name": name,
                "safety_level": data["safety_level"],
                "risk_description": data["risk_description"],
                "max_concentration": data["max_concentration"]
            }
            for name, data in PRESERVATIVES.items()
        ]
    
    @staticmethod
    def get_all_risk_ingredients() -> List[dict]:
        return [
            {
                "name": name,
                "risk_level": data["risk_level"],
                "risk_type": data["risk_type"],
                "risk_description": data["risk_description"],
                "avoid_skin_types": data["avoid_skin_types"]
            }
            for name, data in RISK_INGREDIENTS.items()
        ]
