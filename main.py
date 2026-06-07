import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import (
    ApiResponse,
    ParseRequest,
    ParseResult,
    AdaptabilityRequest,
    AdaptabilityResult,
    ConflictCheckRequest,
    ConflictResult,
    SuggestionRequest,
    SuggestionResult,
    SchemeAdoptRequest,
    FeedbackRequest
)
from app.utils.helpers import success_response, error_response
from app.services.ingredient_parser import IngredientParser
from app.services.adaptability import AdaptabilityCalculator
from app.services.conflict_detector import ConflictDetector
from app.services.suggestion_engine import SuggestionEngine
from app.database.stats import stats_store


app = FastAPI(
    title="护肤品成分分析与肤质适配推荐 API",
    description="提供成分解析、肤质适配计算、成分冲突检测、护肤建议推送和数据统计服务",
    version="1.0.0"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', '')}")
    message = "参数校验失败: " + "; ".join(errors) if errors else "参数校验失败"
    return JSONResponse(
        status_code=200,
        content={"code": 400, "message": message, "data": None}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": 500, "message": f"服务器内部错误: {str(exc)}", "data": None}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=ApiResponse)
async def root():
    return success_response(data={
        "service": "护肤品成分分析与肤质适配推荐 API",
        "version": "1.0.0",
        "endpoints": {
            "成分解析": "POST /api/parse",
            "成分库查询": "GET /api/ingredients/{category}",
            "肤质适配计算": "POST /api/adaptability",
            "成分冲突检测": "POST /api/conflict",
            "冲突规则库": "GET /api/conflict/rules",
            "护肤建议推送": "POST /api/suggestions",
            "统计概览": "GET /api/stats/overview",
            "热门成分分布": "GET /api/stats/hot-ingredients",
            "肤质适配准确率": "GET /api/stats/adaptability-accuracy",
            "风险成分预警次数": "GET /api/stats/risk-warnings",
            "护肤方案采纳率": "GET /api/stats/adoption-rate",
            "方案采纳反馈": "POST /api/stats/adopt-scheme",
            "适配准确率反馈": "POST /api/stats/adaptability-feedback"
        }
    })


@app.post("/api/parse", response_model=ApiResponse)
async def parse_ingredients(request: ParseRequest):
    try:
        result: ParseResult = IngredientParser.parse_ingredients(request.ingredient_list)
        return success_response(data=result.model_dump(), message="成分解析成功")
    except Exception as e:
        return error_response(message=f"成分解析失败: {str(e)}", code=500)


@app.get("/api/ingredients/{category}", response_model=ApiResponse)
async def get_ingredients_library(category: str):
    try:
        if category == "active":
            data = IngredientParser.get_all_active_ingredients()
            return success_response(data=data, message="获取活性成分库成功")
        elif category == "preservative":
            data = IngredientParser.get_all_preservatives()
            return success_response(data=data, message="获取防腐剂库成功")
        elif category == "risk":
            data = IngredientParser.get_all_risk_ingredients()
            return success_response(data=data, message="获取风险成分库成功")
        else:
            return error_response(message=f"不支持的成分分类: {category}，支持 active/preservative/risk", code=400)
    except Exception as e:
        return error_response(message=f"获取成分库失败: {str(e)}", code=500)


@app.post("/api/adaptability", response_model=ApiResponse)
async def calculate_adaptability(request: AdaptabilityRequest):
    try:
        result: AdaptabilityResult = AdaptabilityCalculator.calculate(
            ingredient_list=request.ingredient_list,
            skin_profile=request.skin_profile
        )
        return success_response(data=result.model_dump(), message="肤质适配计算成功")
    except Exception as e:
        return error_response(message=f"适配计算失败: {str(e)}", code=500)


@app.post("/api/conflict", response_model=ApiResponse)
async def detect_conflicts(request: ConflictCheckRequest):
    try:
        result: ConflictResult = ConflictDetector.detect_conflicts(request)
        return success_response(data=result.model_dump(), message="成分冲突检测完成")
    except Exception as e:
        return error_response(message=f"冲突检测失败: {str(e)}", code=500)


@app.get("/api/conflict/rules", response_model=ApiResponse)
async def get_conflict_rules():
    try:
        rules = ConflictDetector.get_all_conflict_rules()
        return success_response(data=rules, message="获取冲突规则库成功")
    except Exception as e:
        return error_response(message=f"获取冲突规则失败: {str(e)}", code=500)


@app.post("/api/suggestions", response_model=ApiResponse)
async def get_suggestions(request: SuggestionRequest):
    try:
        result: SuggestionResult = SuggestionEngine.generate_suggestions(request)
        return success_response(data=result.model_dump(), message="护肤建议生成成功")
    except Exception as e:
        return error_response(message=f"建议生成失败: {str(e)}", code=500)


@app.get("/api/stats/overview", response_model=ApiResponse)
async def get_stats_overview():
    try:
        overview = stats_store.get_overview()
        return success_response(data=overview, message="获取统计概览成功")
    except Exception as e:
        return error_response(message=f"获取统计概览失败: {str(e)}", code=500)


@app.get("/api/stats/hot-ingredients", response_model=ApiResponse)
async def get_hot_ingredients(top_n: int = 10):
    try:
        data = stats_store.get_hot_ingredients(top_n=top_n)
        return success_response(data={"top_n": top_n, "ingredients": data}, message="获取热门成分分布成功")
    except Exception as e:
        return error_response(message=f"获取热门成分失败: {str(e)}", code=500)


@app.get("/api/stats/adaptability-accuracy", response_model=ApiResponse)
async def get_adaptability_accuracy():
    try:
        data = stats_store.get_adaptability_accuracy()
        return success_response(data=data, message="获取肤质适配准确率成功")
    except Exception as e:
        return error_response(message=f"获取适配准确率失败: {str(e)}", code=500)


@app.get("/api/stats/risk-warnings", response_model=ApiResponse)
async def get_risk_warnings():
    try:
        data = stats_store.get_risk_warning_stats()
        return success_response(data=data, message="获取风险成分预警次数成功")
    except Exception as e:
        return error_response(message=f"获取风险预警失败: {str(e)}", code=500)


@app.get("/api/stats/adoption-rate", response_model=ApiResponse)
async def get_adoption_rate():
    try:
        data = stats_store.get_scheme_adoption_rate()
        return success_response(data=data, message="获取护肤方案采纳率成功")
    except Exception as e:
        return error_response(message=f"获取采纳率失败: {str(e)}", code=500)


@app.post("/api/stats/adopt-scheme", response_model=ApiResponse)
async def record_scheme_adoption(request: SchemeAdoptRequest):
    try:
        if request.adopted:
            ok = stats_store.record_scheme_adopted(suggestion_id=request.suggestion_id)
            if not ok:
                return error_response(message="该方案已记录采纳或无可用方案可采纳", code=400)
        return success_response(data={"adopted": request.adopted}, message="方案采纳记录成功")
    except Exception as e:
        return error_response(message=f"记录失败: {str(e)}", code=500)


@app.post("/api/stats/adaptability-feedback", response_model=ApiResponse)
async def record_adaptability_feedback(request: FeedbackRequest):
    try:
        ok = stats_store.record_adaptability_feedback(
            is_correct=request.is_correct,
            calculation_id=request.calculation_id
        )
        if not ok:
            return error_response(message="该计算结果已反馈过", code=400)
        return success_response(
            data={"is_correct": request.is_correct},
            message="适配反馈记录成功"
        )
    except Exception as e:
        return error_response(message=f"记录失败: {str(e)}", code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9101)
