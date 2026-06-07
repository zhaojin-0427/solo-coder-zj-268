from typing import List, Dict, Set
from collections import defaultdict
from app.database.ingredients import (
    get_ingredient_info,
    INGREDIENT_CONFLICTS,
    ACTIVE_INGREDIENTS
)
from app.schemas import (
    ProductIngredients,
    ConflictCheckRequest,
    ConflictItem,
    ConflictResult
)
from app.database.stats import stats_store


class ConflictDetector:
    
    @staticmethod
    def _canonicalize_ingredients(ingredients: List[str]) -> Set[str]:
        canonical = set()
        for ing in ingredients:
            info = get_ingredient_info(ing)
            if info:
                canonical.add(info["name"])
        return canonical
    
    @staticmethod
    def _is_conflict_match(
        conflict_ingredients: List[str],
        present_ingredients: Set[str],
        is_overuse_check: bool = False
    ) -> bool:
        conflict_lower = [i.lower() for i in conflict_ingredients]
        present_lower = {i.lower() for i in present_ingredients}
        
        if is_overuse_check:
            match_count = sum(1 for ci in conflict_lower if ci in present_lower)
            return match_count >= 2
        else:
            matched = [ci for ci in conflict_lower if ci in present_lower]
            return len(matched) >= 2
    
    @staticmethod
    def detect_conflicts(request: ConflictCheckRequest) -> ConflictResult:
        all_ingredients_map: Dict[str, Set[str]] = {}
        all_canonical: Set[str] = set()
        ingredient_to_products: Dict[str, List[str]] = defaultdict(list)
        
        for product in request.products:
            canonical = ConflictDetector._canonicalize_ingredients(product.ingredients)
            all_ingredients_map[product.product_name] = canonical
            all_canonical.update(canonical)
            for ing in canonical:
                ingredient_to_products[ing].append(product.product_name)
        
        conflicts: List[ConflictItem] = []
        overuse_ingredients: List[dict] = []
        overuse_count: Dict[str, int] = defaultdict(int)
        
        for conflict in INGREDIENT_CONFLICTS:
            conflict_type = conflict["conflict_type"]
            
            if conflict_type == "过度叠加":
                target_ingredient = conflict["ingredients"][0]
                count = 0
                involved_products = []
                
                for product_name, ingredients in all_ingredients_map.items():
                    for ing in ingredients:
                        if ing.lower() == target_ingredient.lower():
                            count += 1
                            involved_products.append(product_name)
                            break
                
                if count >= 2:
                    overuse_count[target_ingredient] = count
                    conflicts.append(ConflictItem(
                        conflict_type=conflict_type,
                        severity=conflict["severity"],
                        ingredients_involved=[target_ingredient],
                        products_involved=involved_products,
                        description=conflict["description"],
                        alternative=conflict["alternative"]
                    ))
                    overuse_ingredients.append({
                        "name": target_ingredient,
                        "product_count": count,
                        "products": involved_products,
                        "description": conflict["description"]
                    })
                    stats_store.record_conflict_detected()
                    stats_store.record_risk_warning(f"成分过度叠加-{target_ingredient}")
            else:
                matched_ingredients = []
                for ci in conflict["ingredients"]:
                    for pi in all_canonical:
                        if pi.lower() == ci.lower():
                            matched_ingredients.append(pi)
                            break
                
                if len(matched_ingredients) >= 2:
                    involved_products_set: Set[str] = set()
                    for mi in matched_ingredients:
                        involved_products_set.update(ingredient_to_products.get(mi, []))
                    
                    conflicts.append(ConflictItem(
                        conflict_type=conflict_type,
                        severity=conflict["severity"],
                        ingredients_involved=matched_ingredients,
                        products_involved=list(involved_products_set),
                        description=conflict["description"],
                        alternative=conflict["alternative"]
                    ))
                    stats_store.record_conflict_detected()
                    stats_store.record_risk_warning(f"成分冲突-{conflict_type}")
        
        has_conflict = len(conflicts) > 0
        
        return ConflictResult(
            has_conflict=has_conflict,
            conflict_count=len(conflicts),
            conflicts=conflicts,
            overuse_ingredients=overuse_ingredients
        )
    
    @staticmethod
    def get_all_conflict_rules() -> List[dict]:
        return [
            {
                "ingredients": rule["ingredients"],
                "conflict_type": rule["conflict_type"],
                "severity": rule["severity"],
                "description": rule["description"],
                "alternative": rule["alternative"]
            }
            for rule in INGREDIENT_CONFLICTS
        ]
