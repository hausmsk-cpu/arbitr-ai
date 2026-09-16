"""Запросы в госорганы."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.case import Case
from app.models.request import Request
from app.models.user import User
from app.schemas.request import RequestCreate, RequestRead, RequestUpdate

router = APIRouter()


@router.get("", response_model=list[RequestRead])
async def list_requests(
    case_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Request]:
    """Список запросов (по делу или все)."""
    query = select(Request).order_by(Request.created_at.desc())
    if case_id is not None:
        query = query.where(Request.case_id == case_id)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: RequestCreate,
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Request:
    """Создание запроса в госорган."""
    case = await db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    request = Request(
        case_id=case_id,
        request_type=payload.request_type,
        title=payload.title,
        target_org=payload.target_org,
        content=payload.content,
        sending_method=payload.sending_method,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request)
    return request


@router.get("/{request_id}", response_model=RequestRead)
async def get_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Request:
    """Детали запроса."""
    request = await db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request


@router.patch("/{request_id}", response_model=RequestRead)
async def update_request(
    request_id: uuid.UUID,
    payload: RequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Request:
    """Обновление статуса/данных запроса."""
    request = await db.get(Request, request_id)
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(request, field, value)
    await db.flush()
    await db.refresh(request)
    return request