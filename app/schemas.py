from typing import Generic, TypeVar, Optional, List, Literal, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import date

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


VALID_SKIN_TYPES = ["干性", "油性", "混合性", "敏感性", "痘痘", "中性", "成熟肌", "暗沉"]
VALID_SEASONS = ["春季", "夏季", "秋季", "冬季"]


class SkinProfile(BaseModel):
    skin_type: str = Field(..., description="肤质类型：干性、油性、混合性、敏感性、痘痘、中性、成熟肌、暗沉")
    is_sensitive: Optional[bool] = Field(default=False, description="是否敏感肌")
    concerns: Optional[List[str]] = Field(default=[], description="主要护肤诉求")
    allergies: Optional[List[str]] = Field(default=[], description="过敏成分")

    @field_validator("skin_type")
    @classmethod
    def validate_skin_type(cls, v):
        if v not in VALID_SKIN_TYPES:
            raise ValueError(f"不支持的肤质类型: {v}，支持的类型: {', '.join(VALID_SKIN_TYPES)}")
        return v


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

    @field_validator("season")
    @classmethod
    def validate_season(cls, v):
        if v is None:
            return v
        if v not in VALID_SEASONS:
            raise ValueError(f"不支持的季节: {v}，支持的季节: {', '.join(VALID_SEASONS)}")
        return v


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


TimeSlot = Literal["morning", "evening", "weekly", "morning_evening"]
FrequencyUnit = Literal["daily", "times_per_week", "every_n_days"]


class RegimenProduct(BaseModel):
    product_name: str = Field(..., description="产品名称")
    ingredient_list: List[str] = Field(..., description="产品成分列表")
    time_slot: TimeSlot = Field(..., description="使用时段：morning/evening/weekly/morning_evening")
    frequency: int = Field(default=1, ge=1, description="使用频率，配合 frequency_unit 使用")
    frequency_unit: FrequencyUnit = Field(default="daily", description="频率单位：daily/times_per_week/every_n_days")
    order_index: int = Field(default=1, ge=1, description="使用顺序（在同时段内）")
    start_week: int = Field(default=1, ge=1, description="开始使用的周次")
    end_week: Optional[int] = Field(default=None, ge=1, description="停止使用的周次（None表示持续到疗程结束）")


class RegimenPlanRequest(BaseModel):
    skin_profile: SkinProfile
    total_weeks: int = Field(default=4, ge=1, le=52, description="疗程总周数")
    products: List[RegimenProduct] = Field(..., description="参与疗程的所有产品及其使用安排")
    notes: Optional[str] = Field(default=None, description="用户备注")


class IngredientAccumulationRisk(BaseModel):
    ingredient_name: str
    category: str
    daily_exposure_count: int
    weekly_exposure_count: int
    risk_level: Literal["low", "medium", "high", "critical"]
    risk_score: float
    description: str
    affected_time_slots: List[str]
    recommendation: str


class TolerancePoint(BaseModel):
    week: int
    tolerance_score: float
    irritation_risk: float
    status: str
    description: str


class ToleranceCurve(BaseModel):
    ingredient_name: str
    start_score: float
    current_score: float
    target_score: float
    points: List[TolerancePoint]
    is_tolerated: bool
    recommendation: str


class AlternationWindow(BaseModel):
    ingredient_a: str
    ingredient_b: str
    conflict_type: str
    min_interval_hours: int
    recommended_pattern: str
    current_plan_ok: bool
    description: str


class RestartAdvice(BaseModel):
    ingredient_name: str
    stop_week: int
    rest_weeks: int
    restart_week: Optional[int] = None
    reason: str
    restart_tips: List[str]


class DailyCareItem(BaseModel):
    date: Optional[str] = Field(default=None, description="日期，YYYY-MM-DD格式")
    weekday: str
    time_slot: str
    order_index: int
    product_name: str
    ingredients: List[str]
    notes: List[str]


class StageRiskWarning(BaseModel):
    stage: str
    start_week: int
    end_week: int
    risk_level: Literal["low", "medium", "high", "critical"]
    risk_type: str
    description: str
    triggered_ingredients: List[str]
    actions: List[str]


class AdjustmentSuggestion(BaseModel):
    priority: Literal["critical", "high", "medium", "low"]
    category: str
    current_plan: str
    suggested_plan: str
    reason: str
    impact_scope: List[str]


class RegimenPlanResult(BaseModel):
    regimen_id: str
    total_weeks: int
    skin_type: str
    plan_days: List[DailyCareItem]
    accumulation_risks: List[IngredientAccumulationRisk]
    tolerance_curves: List[ToleranceCurve]
    alternation_windows: List[AlternationWindow]
    restart_advices: List[RestartAdvice]
    stage_warnings: List[StageRiskWarning]
    adjustment_suggestions: List[AdjustmentSuggestion]
    overall_risk_level: Literal["low", "medium", "high", "critical"]
    overall_score: float
    summary: str


class RegimenTrackRequest(BaseModel):
    regimen_id: str = Field(..., description="疗程方案ID")
    week: int = Field(..., ge=1, description="当前周次")
    completed_days: int = Field(default=0, ge=0, description="本周已完成护理天数")
    acne_occurred: bool = Field(default=False, description="是否出现爆痘")
    sensitivity_occurred: bool = Field(default=False, description="是否出现敏感")
    irritation_areas: Optional[List[str]] = Field(default=None, description="不适部位")
    adjusted_products: Optional[List[str]] = Field(default=None, description="已调整的产品")
    user_notes: Optional[str] = Field(default=None, description="用户备注")


class RegimenTrackResult(BaseModel):
    track_id: str
    regimen_id: str
    week: int
    completion_rate: float
    stage: str
    warnings_triggered: List[str]
    adjusted: bool
    adjustment_details: List[str]
    next_week_advice: List[str]


class RegimenStats(BaseModel):
    total_regimens: int
    completed_regimens: int
    completion_rate: float
    total_tracks: int
    acne_warning_count: int
    sensitivity_warning_count: int
    total_risk_warnings: int
    adjustment_trigger_count: int
    adjustment_trigger_rate: float
    multi_product_regimens: int
    multi_product_adopted: int
    multi_product_adoption_rate: float


class RegimenAdoptRequest(BaseModel):
    regimen_id: str = Field(..., description="疗程方案ID")
    adopted: bool = Field(..., description="是否采纳该疗程方案")
