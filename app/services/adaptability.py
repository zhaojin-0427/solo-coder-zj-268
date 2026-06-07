from typing import List, Set
import uuid
from app.database.ingredients import (
    get_ingredient_info,
    SKIN_TYPE_PROFILES
)
from app.schemas import (
    SkinProfile,
    AdaptabilityResult,
    IngredientAdaptDetail
)
from app.utils.helpers import get_adaptability_level
from app.database.stats import stats_store


def _canonicalize_allergy_names(allergy_list: List[str]) -> Set[str]:
    canonical = set()
    for allergy in allergy_list or []:
        info = get_ingredient_info(allergy)
        if info:
            canonical.add(info["name"].lower())
        else:
            canonical.add(allergy.strip().lower())
    return canonical


class AdaptabilityCalculator:
    
    @staticmethod
    def calculate(
        ingredient_list: List[str],
        skin_profile: SkinProfile
    ) -> AdaptabilityResult:
        skin_type = skin_profile.skin_type
        is_sensitive = skin_profile.is_sensitive
        allergies = _canonicalize_allergy_names(skin_profile.allergies)
        
        skin_profile_data = SKIN_TYPE_PROFILES.get(skin_type, SKIN_TYPE_PROFILES["中性"])
        preferred = [p.lower() for p in skin_profile_data["preferred_ingredients"]]
        avoid = [a.lower() for a in skin_profile_data["avoid_ingredients"]]
        key_needs = skin_profile_data["key_needs"]
        sensitivity_level = skin_profile_data["sensitivity_level"]
        
        details: List[IngredientAdaptDetail] = []
        benefit_ingredients: List[str] = []
        risk_ingredients: List[str] = []
        warnings: List[str] = []
        total_score = 0.0
        processed_count = 0
        
        matched_names = set()
        
        for raw_name in ingredient_list:
            info = get_ingredient_info(raw_name)
            if info is None:
                continue
            
            canonical_name = info["name"]
            if canonical_name in matched_names:
                continue
            matched_names.add(canonical_name)
            
            category = info["category"]
            name_lower = canonical_name.lower()
            
            is_benefit = False
            is_risk = False
            score = 50.0
            reason = ""
            
            if name_lower in allergies:
                is_risk = True
                score = 0.0
                reason = f"{canonical_name} 是您的过敏成分，严禁使用"
                warnings.append(reason)
                risk_ingredients.append(canonical_name)
                stats_store.record_risk_warning("过敏成分")
            
            elif category == "active":
                efficacy = info.get("efficacy_score", 70)
                ingredient_skin_types = [s.lower() for s in info.get("skin_types", [])]
                
                if name_lower in preferred or skin_type.lower() in ingredient_skin_types:
                    is_benefit = True
                    score = min(efficacy * 1.0, 100)
                    benefits = info.get("benefits", [])
                    matched_needs = [b for b in benefits if b in key_needs]
                    if matched_needs:
                        score = min(score + 5, 100)
                        reason = f"{canonical_name} 适配{skin_type}肤质，命中护肤需求：{', '.join(matched_needs)}"
                    else:
                        reason = f"{canonical_name} 适合{skin_type}肤质使用"
                    benefit_ingredients.append(canonical_name)
                elif name_lower in avoid:
                    is_risk = True
                    score = 20.0
                    reason = f"{canonical_name} 不适合{skin_type}肤质，建议避开"
                    risk_ingredients.append(canonical_name)
                    warnings.append(reason)
                    stats_store.record_risk_warning("肤质不适配")
                else:
                    score = efficacy * 0.7
                    reason = f"{canonical_name} 对{skin_type}肤质中性偏友好"
            
            elif category == "preservative":
                safety = info.get("safety_level", 3)
                if safety >= 4:
                    is_risk = True
                    if is_sensitive or sensitivity_level >= 3:
                        score = 15.0
                        reason = f"{canonical_name} 是{safety}级风险防腐剂，敏感肌不建议使用"
                        risk_ingredients.append(canonical_name)
                        warnings.append(reason)
                        stats_store.record_risk_warning("高风险防腐剂")
                    else:
                        score = 40.0
                        reason = f"{canonical_name} 是{safety}级风险防腐剂，非敏感肌可少量使用"
                elif safety == 3:
                    score = 60.0
                    if is_sensitive:
                        score = 40.0
                        reason = f"{canonical_name} 是中等风险防腐剂，敏感肌需注意"
                    else:
                        reason = f"{canonical_name} 是常规防腐剂，在安全浓度下可使用"
                else:
                    score = 85.0
                    reason = f"{canonical_name} 是温和安全的防腐剂"
            
            elif category == "risk":
                risk_level = info.get("risk_level", 3)
                risk_type = info.get("risk_type", "刺激")
                avoid_skin_types = [s.lower() for s in info.get("avoid_skin_types", [])]
                
                if skin_type.lower() in avoid_skin_types or "所有肤质" in avoid_skin_types:
                    is_risk = True
                    score = 10.0 if risk_level >= 4 else 25.0
                    reason = f"{canonical_name} 是{risk_level}级风险成分（{risk_type}），{skin_type}肤质应避开"
                    risk_ingredients.append(canonical_name)
                    warnings.append(reason)
                    stats_store.record_risk_warning(f"风险成分-{risk_type}")
                elif is_sensitive and risk_level >= 3:
                    is_risk = True
                    score = 20.0
                    reason = f"{canonical_name} 是{risk_level}级风险成分（{risk_type}），敏感肌慎用"
                    risk_ingredients.append(canonical_name)
                    warnings.append(reason)
                    stats_store.record_risk_warning(f"敏感肌风险-{risk_type}")
                else:
                    score = 35.0 if risk_level >= 3 else 50.0
                    reason = f"{canonical_name} 是{risk_level}级风险成分（{risk_type}），{skin_type}肤质需注意使用浓度"
            
            details.append(IngredientAdaptDetail(
                name=canonical_name,
                is_benefit=is_benefit,
                is_risk=is_risk,
                score=round(score, 1),
                reason=reason
            ))
            
            total_score += score
            processed_count += 1
        
        if processed_count > 0:
            avg_score = total_score / processed_count
        else:
            avg_score = 50.0
        
        level = get_adaptability_level(avg_score)
        
        if len(benefit_ingredients) == 0 and processed_count > 0:
            warnings.append("未识别到明显适配您肤质的活性成分，建议选择针对性更强的产品")
        
        stats_store.record_analysis(skin_type=skin_type)
        stats_store.record_adaptability_calculation()
        calculation_id = uuid.uuid4().hex
        stats_store.register_calculation_id(calculation_id)
        
        return AdaptabilityResult(
            calculation_id=calculation_id,
            total_score=round(avg_score, 1),
            level=level,
            skin_type=skin_type,
            details=details,
            benefit_ingredients=benefit_ingredients,
            risk_ingredients=risk_ingredients,
            warnings=warnings
        )
