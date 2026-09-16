"""AI-модуль Arbitr AI: генерация документов и RAG-поиск.

API:
- POST /api/v1/ai/generate — генерация документа
- GET  /api/v1/ai/types — доступные типы документов
- GET  /api/v1/ai/search — поиск по базе знаний (RAG)
- GET  /api/v1/ai/stats  — статистика базы знаний
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.ai.generator import CaseContext, DocumentGenerator
from app.ai.rag_search import get_rag_search
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["ai"])

generator = DocumentGenerator()
rag = get_rag_search()


class GenerateRequest(BaseModel):
    """Запрос на генерацию документа."""

    doc_type: str = Field(min_length=2, max_length=64)
    case_number: str = ""
    court_name: str = "Арбитражный суд Краснодарского края"
    court_decision_date: str = ""
    kad_url: str = ""

    debtor_full_name: str = ""
    debtor_birth_date: str = ""
    debtor_birth_place: str = ""
    debtor_inn: str = ""
    debtor_snils: str = ""
    debtor_address: str = ""

    spouse_full_name: str = ""
    spouse_birth_date: str = ""
    spouse_birth_place: str = ""
    spouse_address: str = ""

    manager_full_name: str = ""
    manager_address: str = ""
    manager_email: str = ""
    manager_phone: str = ""
    manager_passport: str = ""
    manager_snils: str = ""

    period_start: str = "07.07.2015"
    date_today: str = ""


class SearchRequest(BaseModel):
    """Запрос на RAG-поиск."""

    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


@router.get("/types")
async def document_types(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Доступные типы документов для генерации."""
    return generator.document_types


@router.post("/generate")
async def generate_document(
    payload: GenerateRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Генерация юридического документа по шаблону кейса."""
    if payload.doc_type not in generator.document_types:
        raise HTTPException(status_code=404, detail=f"Unknown document type: {payload.doc_type}")

    context = CaseContext(
        case_number=payload.case_number,
        court_name=payload.court_name,
        court_decision_date=payload.court_decision_date,
        kad_url=payload.kad_url,
        debtor_full_name=payload.debtor_full_name,
        debtor_birth_date=payload.debtor_birth_date,
        debtor_birth_place=payload.debtor_birth_place,
        debtor_inn=payload.debtor_inn,
        debtor_snils=payload.debtor_snils,
        debtor_address=payload.debtor_address,
        spouse_full_name=payload.spouse_full_name,
        spouse_birth_date=payload.spouse_birth_date,
        spouse_birth_place=payload.spouse_birth_place,
        spouse_address=payload.spouse_address,
        manager_full_name=payload.manager_full_name,
        manager_address=payload.manager_address,
        manager_email=payload.manager_email,
        manager_phone=payload.manager_phone,
        manager_passport=payload.manager_passport,
        manager_snils=payload.manager_snils,
        period_start=payload.period_start,
        date_today=payload.date_today,
    )

    # RAG-контекст для проверки
    query = f"{payload.doc_type} {payload.debtor_full_name}".strip()
    chunks = rag.query(query, top_k=3)

    text = generator.generate(payload.doc_type, context, rag_chunks=chunks)

    return {
        "doc_type": payload.doc_type,
        "doc_type_name": generator.document_types[payload.doc_type],
        "text": text,
        "rag_sources": [
            {"source": ch.source, "case_id": ch.case_id, "doc_type": ch.doc_type}
            for ch in chunks
        ],
        "generated_by": "template+rag",
    }


@router.get("/search")
async def rag_search(
    q: str,
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Поиск по базе знаний кейсов."""
    if not q or len(q) < 3:
        raise HTTPException(status_code=400, detail="Query too short (min 3 chars)")
    results = rag.query(q, top_k=min(top_k, 20))
    return {
        "query": q,
        "results": [
            {
                "source": ch.source,
                "case_id": ch.case_id,
                "doc_type": ch.doc_type,
                "category": ch.category,
                "text": ch.text[:500],
            }
            for ch in results
        ],
        "total": len(results),
    }


@router.get("/stats")
async def rag_stats(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Статистика базы знаний."""
    return rag.stats()