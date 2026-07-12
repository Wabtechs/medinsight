from typing import Any
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories import BaseRepository
from app.domain.models import Facility, User, Patient, ClinicalCase, AuditLog, SyncQueue


class FacilityRepository(BaseRepository[Facility]):
    async def get_by_code(self, code: str) -> Facility | None:
        result = await self.session.execute(select(Facility).where(Facility.code == code))
        return result.scalar_one_or_none()

    async def get_with_stats(self, facility_id: UUID) -> dict | None:
        facility = await self.get_by_id(facility_id)
        if not facility:
            return None

        patients_count = await self.session.execute(
            select(func.count()).select_from(Patient).where(Patient.facility_id == facility_id, Patient.is_active == True)
        )
        doctors_count = await self.session.execute(
            select(func.count()).select_from(User).where(User.facility_id == facility_id, User.role == "DOCTOR", User.is_active == True)
        )
        cases_count = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(ClinicalCase.facility_id == facility_id)
        )

        return {
            "facility": facility,
            "stats": {
                "patients_count": patients_count.scalar_one(),
                "doctors_count": doctors_count.scalar_one(),
                "cases_count": cases_count.scalar_one(),
            }
        }


class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


class PatientRepository(BaseRepository[Patient]):
    async def get_by_patient_uuid(self, patient_uuid: UUID) -> Patient | None:
        result = await self.session.execute(select(Patient).where(Patient.patient_uuid == patient_uuid))
        return result.scalar_one_or_none()


class ClinicalCaseRepository(BaseRepository[ClinicalCase]):
    async def get_by_facility(
        self, facility_id: UUID, page: int = 1, size: int = 20,
        outcome_status: str | None = None, doctor_id: UUID | None = None
    ) -> tuple[list[ClinicalCase], int]:
        query = select(ClinicalCase).where(ClinicalCase.facility_id == facility_id)
        count_query = select(func.count()).select_from(ClinicalCase).where(ClinicalCase.facility_id == facility_id)

        if outcome_status:
            query = query.where(ClinicalCase.outcome_status == outcome_status)
            count_query = count_query.where(ClinicalCase.outcome_status == outcome_status)
        if doctor_id:
            query = query.where(ClinicalCase.doctor_id == doctor_id)
            count_query = count_query.where(ClinicalCase.doctor_id == doctor_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(desc(ClinicalCase.created_at)).offset(offset).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_doctor(self, doctor_id: UUID, page: int = 1, size: int = 20) -> tuple[list[ClinicalCase], int]:
        query = select(ClinicalCase).where(ClinicalCase.doctor_id == doctor_id)
        count_query = select(func.count()).select_from(ClinicalCase).where(ClinicalCase.doctor_id == doctor_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(desc(ClinicalCase.created_at)).offset(offset).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_patient(self, patient_id: UUID, page: int = 1, size: int = 20) -> tuple[list[ClinicalCase], int]:
        query = select(ClinicalCase).where(ClinicalCase.patient_id == patient_id)
        count_query = select(func.count()).select_from(ClinicalCase).where(ClinicalCase.patient_id == patient_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(desc(ClinicalCase.created_at)).offset(offset).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_stats(self, facility_id: UUID | None = None) -> dict:
        base_filter = ClinicalCase.facility_id == facility_id if facility_id else True

        total = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(base_filter)
        )
        pending = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(base_filter, ClinicalCase.outcome_status == "PENDING")
        )
        in_progress = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(base_filter, ClinicalCase.outcome_status == "IN_PROGRESS")
        )
        success = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(base_filter, ClinicalCase.outcome_status == "SUCCESS")
        )
        failure = await self.session.execute(
            select(func.count()).select_from(ClinicalCase).where(base_filter, ClinicalCase.outcome_status == "FAILURE")
        )

        return {
            "total": total.scalar_one(),
            "pending": pending.scalar_one(),
            "in_progress": in_progress.scalar_one(),
            "success": success.scalar_one(),
            "failure": failure.scalar_one(),
        }


class AuditLogRepository(BaseRepository[AuditLog]):
    async def get_by_user(self, user_id: UUID, page: int = 1, size: int = 20) -> tuple[list[AuditLog], int]:
        query = select(AuditLog).where(AuditLog.user_id == user_id)
        count_query = select(func.count()).select_from(AuditLog).where(AuditLog.user_id == user_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_resource(self, resource: str, page: int = 1, size: int = 20) -> tuple[list[AuditLog], int]:
        query = select(AuditLog).where(AuditLog.resource == resource)
        count_query = select(func.count()).select_from(AuditLog).where(AuditLog.resource == resource)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * size
        query = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(size)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_stats(self, facility_id: UUID | None = None) -> dict:
        base_filter = AuditLog.facility_id == facility_id if facility_id else True

        total = await self.session.execute(
            select(func.count()).select_from(AuditLog).where(base_filter)
        )
        actions = await self.session.execute(
            select(AuditLog.action, func.count()).where(base_filter).group_by(AuditLog.action)
        )

        return {
            "total": total.scalar_one(),
            "by_action": {row[0]: row[1] for row in actions.all()},
        }


class SyncQueueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_pending(self, user_id: UUID, limit: int = 100) -> list[SyncQueue]:
        result = await self.session.execute(
            select(SyncQueue)
            .where(SyncQueue.user_id == user_id, SyncQueue.status == "pending")
            .order_by(SyncQueue.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> SyncQueue:
        instance = SyncQueue(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def mark_synced(self, id: UUID) -> None:
        item = await self.session.execute(select(SyncQueue).where(SyncQueue.id == id))
        instance = item.scalar_one_or_none()
        if instance:
            instance.status = "synced"
            instance.synced_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def mark_failed(self, id: UUID, error_message: str) -> None:
        item = await self.session.execute(select(SyncQueue).where(SyncQueue.id == id))
        instance = item.scalar_one_or_none()
        if instance:
            instance.status = "failed"
            instance.error_message = error_message
            await self.session.flush()

    async def clear_synced(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(SyncQueue).where(SyncQueue.user_id == user_id, SyncQueue.status == "synced")
        )
        items = result.scalars().all()
        count = len(items)
        for item in items:
            await self.session.delete(item)
        await self.session.flush()
        return count
