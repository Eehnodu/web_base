# app/schemas/jsonapi.py
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

# JSON 객체 타입 별칭 (dict[str, Any])
JsonObj = Dict[str, Any]

# ---------------------------
# 🔗 JSON:API Links 관련 모델
# ---------------------------
class Link(BaseModel):
    href: str   # 단일 링크 객체, 반드시 href 속성을 가짐

class Links(BaseModel):
    # JSON:API 문서 최상위 links 구조
    self: Optional[Link] = None   # 현재 리소스 자기 자신을 가리키는 링크
    next: Optional[Link] = None   # 페이지네이션 시 다음 페이지 링크
    prev: Optional[Link] = None   # 페이지네이션 시 이전 페이지 링크

# ---------------------------
# ℹ️ JSON:API Meta 정보
# ---------------------------
class Meta(BaseModel):
    total: Optional[int] = None   # 전체 개수 (ex: 총 유저 수)
    page: Optional[int] = None    # 현재 페이지 번호
    size: Optional[int] = None    # 한 페이지 크기
    # 필요하면 확장 가능 (status, timestamp 등 커스텀 필드 넣어도 됨)

# ---------------------------
# 📦 JSON:API Resource 객체
# ---------------------------
class Resource(BaseModel):
    id: Union[int, str]        # 리소스 고유 ID (문자열 또는 숫자)
    type: str                  # 리소스 타입 (ex: "user", "post")
    attributes: JsonObj        # 리소스 속성들 (실제 데이터)

# ---------------------------
# 📄 JSON:API Document (단일)
# ---------------------------
class DocumentSingle(BaseModel):
    data: Resource             # 하나의 리소스
    links: Optional[Links] = None
    meta: Optional[Meta] = None

# ---------------------------
# 📄 JSON:API Document (리스트)
# ---------------------------
class DocumentList(BaseModel):
    data: List[Resource]       # 여러 개의 리소스
    links: Optional[Links] = None
    meta: Optional[Meta] = None

# ---------------------------
# 🛠️ 편의 함수들
# ---------------------------

def resource(type_: str, id_: Union[int, str], attrs: JsonObj) -> Resource:
    """
    개별 Resource 객체를 생성하는 헬퍼.
    예: resource("user", 1, {"name": "Alice"})
    """
    return Resource(id=id_, type=type_, attributes=attrs)

def single_doc(res: Resource, *, self_url: Optional[str] = None,
               meta: Optional[Meta] = None) -> DocumentSingle:
    """
    단일 리소스를 JSON:API DocumentSingle 형태로 감싸주는 헬퍼.
    self_url이 있으면 links.self 자동 추가.
    """
    return DocumentSingle(
        data=res,
        links=Links(self=Link(href=self_url)) if self_url else None,
        meta=meta
    )

def list_doc(res_list: List[Resource], *, self_url: Optional[str] = None,
             meta: Optional[Meta] = None,
             next_url: Optional[str] = None,
             prev_url: Optional[str] = None) -> DocumentList:
    """
    여러 리소스를 JSON:API DocumentList 형태로 감싸주는 헬퍼.
    self, next, prev 링크와 meta 정보를 포함할 수 있음.
    """
    return DocumentList(
        data=res_list,
        links=Links(
            self=Link(href=self_url) if self_url else None,
            next=Link(href=next_url) if next_url else None,
            prev=Link(href=prev_url) if prev_url else None,
        ),
        meta=meta
    )
