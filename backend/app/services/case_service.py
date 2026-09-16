"""Сервис дел о банкротстве."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStatus
from app.models.user import User


class CaseService:
    """Бизнес-логика работы с делами."""

    @staticmethod
    async def get_manager_cases(db: AsyncSession, manager_id: uuid.UUID) -> list[Case]:
        result = await db.execute(
            select(Case).where(Case.manager_id == manager_id).order_by(Case.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_case(db: AsyncSession, case_id: uuid.UUID) -> Case | None:
        return await db.get(Case, case_id)

    @staticmethod
    async def create_case(
        db: AsyncSession,
        manager: User,
        court_name: str,
        court_region: str,
        case_number: str | None = None,
    ) -> Case:
        case = Case(
            manager_id=manager.id,
            court_name=court_name,
            court_region=court_region,
            case_number=case_number,
            status=CaseStatus.DRAFT,
        )
        db.add(case)
        await db.flush()
        await db.refresh(case)
        return case

    @staticmethod
    async def start_procedure(db: AsyncSession, case: Case, start_date: date) -> Case:
        """Перевод дела в процедуру."""
        case.status = CaseStatus.IN_PROCEDURE
        case.procedure_start_date = start_date
        await db.flush()
        await db.refresh(case)
        return case