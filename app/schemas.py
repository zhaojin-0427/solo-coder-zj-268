from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(default=200, description="响应状态码，200表示成功")
    message: str = Field(default="success", description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")


class IngredientInfo(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    benefits: Optional[List[str]] = None
    efficacy_score: Optional[float] = None
    safety_level: Optional[int] = None
    risk_level: Optional[int] = None
    risk_type: Optional[str] = None
    risk_description: Optional[str] = None
    skin_types: Optional[List[str]] = None
    max_concentration: Optional[str] = None


class ParseRequest(BaseModel):
    ingredient_list: str = Field(..., description="产品成分表文本，支持逗号、顿号、换行、分号分隔")


class ParseResult(BaseModel):
    total_count: int
    active_ingredients: List[IngredientInfo]
    preservatives: List[IngredientInfo]
    risk_ingredients: List[IngredientInfo]
    unknown_ingredients: List[str]


class SkinProfile(BaseModel):
    skin_type: str = Field(..., description="肤质类型：干性、油性、混合性、敏感性、痘痘、中性、成熟肌、暗沉")
    is_sensitive: Optional[bool] = Field(default=False, description="是否敏感肌")
    concerns: Optional[List[str]] = Field(default=[], description="主要护肤诉求")
    allergies: Optional[List[str]] = Field(default=[], description="过敏成分")


class ProductIngredients(BaseModel):
    product_name: str
    ingredients: List[str]


class AdaptabilityRequest(BaseModel):
    ingredient_list: List[str]
    skin_profile: SkinProfile


class IngredientAdaptDetail(BaseModel):
    name: str
    is_benefit: bool
    is_risk: bool
    score: float
    reason: str


class AdaptabilityResult(BaseModel):
    calculation_id: str
    total_score: float
    level: str
    skin_type: str
    details: List[IngredientAdaptDetail]
    benefit_ingredients: List[str]
    risk_ingredients: List[str]
    warnings: List[str]


class ConflictCheckRequest(BaseModel):
    products: List[ProductIngredients]


class ConflictItem(BaseModel):
    conflict_type: str
    severity: str
    ingredients_involved: List[str]
    products_involved: List[str]
    description: str
    alternative: str


class ConflictResult(BaseModel):
    has_conflict: bool
    conflict_count: int
    conflicts: List[ConflictItem]
    overuse_ingredients: List[dict]


class SuggestionRequest(BaseModel):
    skin_profile: SkinProfile
    season: Optional[str] = Field(default=None, description="季节：春季、夏季、秋季、冬季，不传则自动判断")
    current_ingredients: Optional[List[str]] = Field(default=[], description="当前使用产品成分")


class SeasonalTip(BaseModel):
    season: str
    general_tips: str
    skin_specific: str
    recommended_ingredients: List[str]
    avoid_ingredients: List[str]


class DailyRoutine(BaseModel):
    morning: List[str]
    evening: List[str]
    weekly: List[str]


class SuggestionResult(BaseModel):
    suggestion_id: str
    seasonal_tip: SeasonalTip
    daily_routine: DailyRoutine
    ingredient_recommendations: List[dict]
    notes: List[str]


class SchemeAdoptRequest(BaseModel):
    adopted: bool = Field(..., description="是否采纳方案")
    suggestion_id: Optional[str] = Field(default=None, description="方案ID")


class FeedbackRequest(BaseModel):
    calculation_id: Optional[str] = Field(default=None)
    is_correct: bool = Field(..., description="适配计算是否准确")
