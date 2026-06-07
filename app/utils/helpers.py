from typing import Any, Optional
from app.schemas import ApiResponse
from datetime import datetime


def success_response(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(code=200, message=message, data=data)


def error_response(message: str, code: int = 400, data: Any = None) -> ApiResponse:
    return ApiResponse(code=code, message=message, data=data)


def not_found_response(message: str = "资源不存在", data: Any = None) -> ApiResponse:
    return ApiResponse(code=404, message=message, data=data)


def server_error_response(message: str = "服务器内部错误", data: Any = None) -> ApiResponse:
    return ApiResponse(code=500, message=message, data=data)


def detect_season(month: Optional[int] = None) -> str:
    if month is None:
        month = datetime.now().month
    
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"


def get_adaptability_level(score: float) -> str:
    if score >= 85:
        return "非常适配"
    elif score >= 70:
        return "较为适配"
    elif score >= 55:
        return "一般适配"
    elif score >= 40:
        return "不太适配"
    else:
        return "不适配"
