# app/errors/problem_details.py
from fastapi import Request

def problem(status: int, title: str, detail: str, instance: str | None = None):
    """
    RFC 7807 Problem Details 응답 포맷 빌더
    """
    return {
        "type": "about:blank",   # 필요 시 특정 문서 URL로 교체 가능
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
    }
