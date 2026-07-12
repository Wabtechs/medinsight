from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domain.models import User, ClinicalCase, AuditLog
from app.domain.enums import UserRole, OutcomeStatus
from app.application.schemas import ClinicalCaseCreate, ClinicalCaseUpdate, ClinicalCaseResponse, PaginatedResponse
from app.infrastructure.repositories import ClinicalCaseRepository, AuditLogRepository
from app.deps import get_current_user, require_role, get_facility_scope
from app.application.exceptions import NotFoundException

router = APIRouter(prefix="/clinical-cases", tags=["Clinical Cases"])


@router.get("/stats")
async def get_stats(
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)
    stats = await case_repo.get_stats(facility_scope)
    return stats


@router.get("", response_model=PaginatedResponse[ClinicalCaseResponse])
async def list_clinical_cases(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    outcome_status: OutcomeStatus | None = None,
    doctor_id: UUID | None = None,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)

    if facility_scope:
        items, total = await case_repo.get_by_facility(
            facility_scope, page=page, size=size,
            outcome_status=outcome_status.value if outcome_status else None,
            doctor_id=doctor_id,
        )
    elif current_user.role == UserRole.DOCTOR:
        items, total = await case_repo.get_by_doctor(current_user.id, page=page, size=size)
    else:
        items, total = await case_repo.get_all(page=page, size=size)

    pages = (total + size - 1) // size

    return PaginatedResponse(
        items=[ClinicalCaseResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.post("", response_model=ClinicalCaseResponse, status_code=201)
async def create_clinical_case(
    data: ClinicalCaseCreate,
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)
    case = await case_repo.create(
        facility_id=current_user.facility_id,
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        symptoms_json=data.symptoms_json,
        provisional_diagnosis=data.provisional_diagnosis,
        treatment=data.treatment,
        treatment_duration=data.treatment_duration,
        outcome_status=data.outcome_status,
        outcome_notes=data.outcome_notes,
        tags_json=data.tags_json,
    )

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="CREATE",
        resource="clinical_case",
        resource_id=str(case.id),
    )

    return case


@router.get("/{case_id}", response_model=ClinicalCaseResponse)
async def get_clinical_case(
    case_id: UUID,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)
    case = await case_repo.get_by_id(case_id)

    if not case:
        raise NotFoundException("Clinical case not found")

    if facility_scope and case.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this case")

    return case


@router.put("/{case_id}", response_model=ClinicalCaseResponse)
async def update_clinical_case(
    case_id: UUID,
    data: ClinicalCaseUpdate,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)
    case = await case_repo.get_by_id(case_id)

    if not case:
        raise NotFoundException("Clinical case not found")

    if facility_scope and case.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this case")

    updated = await case_repo.update(case_id, **data.model_dump(exclude_unset=True))

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="UPDATE",
        resource="clinical_case",
        resource_id=str(case_id),
    )

    return updated


@router.delete("/{case_id}")
async def delete_clinical_case(
    case_id: UUID,
    facility_scope: UUID | None = Depends(get_facility_scope),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    case_repo = ClinicalCaseRepository(ClinicalCase, db)
    case = await case_repo.get_by_id(case_id)

    if not case:
        raise NotFoundException("Clinical case not found")

    if facility_scope and case.facility_id != facility_scope:
        from app.application.exceptions import ForbiddenException
        raise ForbiddenException("Access denied to this case")

    await case_repo.delete(case_id)

    audit_repo = AuditLogRepository(AuditLog, db)
    await audit_repo.create(
        user_id=current_user.id,
        facility_id=current_user.facility_id,
        action="DELETE",
        resource="clinical_case",
        resource_id=str(case_id),
    )

    return {"message": "Clinical case deleted successfully"}
