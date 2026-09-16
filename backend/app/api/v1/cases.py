"""CRUD дел о банкротстве."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.case import Case, Creditor, Debtor, Document, Property
from app.models.user import User
from app.schemas.case import (
    CaseCreate,
    CaseRead,
    CaseUpdate,
    CreditorCreate,
    CreditorRead,
    DebtorCreate,
    DebtorRead,
    DocumentRead,
    PropertyCreate,
    PropertyRead,
)

router = APIRouter()


def _get_case_or_404(case: Case | None) -> Case:
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get("", response_model=list[CaseRead])
async def list_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Case]:
    """Список дел текущего управляющего."""
    result = await db.execute(
        select(Case).where(Case.manager_id == current_user.id).order_by(Case.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Case:
    """Создание нового дела."""
    case = Case(
        manager_id=current_user.id,
        court_name=payload.court_name,
        court_region=payload.court_region,
        case_number=payload.case_number,
        procedure_type=payload.procedure_type,
    )
    db.add(case)
    await db.flush()
    await db.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseRead)
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Case:
    """Детали дела."""
    case = await db.get(Case, case_id)
    return _get_case_or_404(case)


@router.patch("/{case_id}", response_model=CaseRead)
async def update_case(
    case_id: uuid.UUID,
    payload: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Case:
    """Обновление дела."""
    case = await db.get(Case, case_id)
    case = _get_case_or_404(case)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    await db.flush()
    await db.refresh(case)
    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Удаление дела."""
    case = await db.get(Case, case_id)
    case = _get_case_or_404(case)
    await db.delete(case)


# ============ Должники ============


@router.get("/{case_id}/debtors", response_model=list[DebtorRead])
async def list_debtors(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Debtor]:
    """Список должников по делу."""
    result = await db.execute(select(Debtor).where(Debtor.case_id == case_id))
    return list(result.scalars().all())


@router.post("/{case_id}/debtors", response_model=DebtorRead, status_code=status.HTTP_201_CREATED)
async def create_debtor(
    case_id: uuid.UUID,
    payload: DebtorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Debtor:
    """Добавление должника в дело."""
    _get_case_or_404(await db.get(Case, case_id))
    debtor = Debtor(case_id=case_id, **payload.model_dump())
    db.add(debtor)
    await db.flush()
    await db.refresh(debtor)
    return debtor


# ============ Кредиторы ============


@router.get("/{case_id}/creditors", response_model=list[CreditorRead])
async def list_creditors(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Creditor]:
    """Список кредиторов по делу."""
    result = await db.execute(select(Creditor).where(Creditor.case_id == case_id))
    return list(result.scalars().all())


@router.post("/{case_id}/creditors", response_model=CreditorRead, status_code=status.HTTP_201_CREATED)
async def create_creditor(
    case_id: uuid.UUID,
    payload: CreditorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Creditor:
    """Добавление кредитора."""
    _get_case_or_404(await db.get(Case, case_id))
    creditor = Creditor(case_id=case_id, **payload.model_dump())
    db.add(creditor)
    await db.flush()
    await db.refresh(creditor)
    return creditor


# ============ Имущество ============


@router.get("/{case_id}/properties", response_model=list[PropertyRead])
async def list_properties(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Property]:
    """Список имущества должника."""
    result = await db.execute(select(Property).where(Property.case_id == case_id))
    return list(result.scalars().all())


@router.post("/{case_id}/properties", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
async def create_property(
    case_id: uuid.UUID,
    payload: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Property:
    """Добавление имущества."""
    _get_case_or_404(await db.get(Case, case_id))
    prop = Property(case_id=case_id, **payload.model_dump())
    db.add(prop)
    await db.flush()
    await db.refresh(prop)
    return prop


# ============ Документы ============


@router.get("/{case_id}/documents", response_model=list[DocumentRead])
async def list_documents(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:
    """Список документов по делу."""
    result = await db.execute(select(Document).where(Document.case_id == case_id))
    return list(result.scalars().all())