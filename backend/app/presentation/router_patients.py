from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domain.models import User, Patient, AuditLog
from app.domain.enums import UserRole
from app.application.schemas import PatientCreate, PatientUpdate, PatientResponse, PaginatedResponse
from app.infrastructure.repositories import PatientRepository, AuditLogRepository
from app.deps import get_current_user, require_role, get_facility_scope
from app.application.exceptions import NotFoundException

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=PaginatedResponse[PatientResponse])
async def list_patients(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = PatientRepository(Patient, db)
    filters = {}
    if facility_scope:
        filters["facility_id"] = facility_scope

    items, total = await patient_repo.get_all(page=page, size=size, filters=filters)
    pages = (total + size - 1) // size

    return PaginatedResponse(
        items=[PatientResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreate,
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = PatientRepository(Patient, db)
    patient = await patient_repo.create(**data.model_dump())

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="CREATE",
        resource="patient",
        resource_id=str(patient.id),
    )

    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = PatientRepository(Patient, db)
    patient = await patient_repo.get_by_id(patient_id)

    if not patient:
        raise NotFoundException("Patient not found")

    if facility_scope and patient.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this patient")

    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    data: PatientUpdate,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = PatientRepository(Patient, db)
    patient = await patient_repo.get_by_id(patient_id)

    if not patient:
        raise NotFoundException("Patient not found")

    if facility_scope and patient.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this patient")

    updated = await patient_repo.update(patient_id, **data.model_dump(exclude_unset=True))

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="UPDATE",
        resource="patient",
        resource_id=str(patient_id),
    )

    return updated


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: UUID,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = PatientRepository(Patient, db)
    patient = await patient_repo.get_by_id(patient_id)

    if not patient:
        raise NotFoundException("Patient not found")

    if facility_scope and patient.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this patient")

    await patient_repo.update(patient_id, is_active=False)

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="DELETE",
        resource="patient",
        resource_id=str(patient_id),
    )

    return {"message": "Patient deactivated successfully"}
