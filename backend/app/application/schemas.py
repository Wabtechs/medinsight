from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Generic, TypeVar, Any
import uuid

from app.domain.enums import UserRole, OutcomeStatus, FacilityType

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int


# --- Facility ---
class FacilityCreate(BaseModel):
    name: str
    code: str
    facility_type: FacilityType = FacilityType.HOSPITAL
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None


class FacilityUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    facility_type: FacilityType | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None


class FacilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    facility_type: FacilityType
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- User ---
class UserCreate(BaseModel):
    facility_id: uuid.UUID
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.DOCTOR


class UserUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    facility_id: uuid.UUID | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    facility_id: uuid.UUID
    firstname: str
    lastname: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- Patient ---
class PatientCreate(BaseModel):
    facility_id: uuid.UUID
    sex: str
    age: int
    blood_group: str | None = None
    medical_history_json: dict | None = None


class PatientUpdate(BaseModel):
    sex: str | None = None
    age: int | None = None
    blood_group: str | None = None
    medical_history_json: dict | None = None
    is_active: bool | None = None


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    facility_id: uuid.UUID
    patient_uuid: uuid.UUID
    sex: str
    age: int
    blood_group: str | None = None
    medical_history_json: dict | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- Clinical Case ---
class ClinicalCaseCreate(BaseModel):
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    symptoms_json: dict
    provisional_diagnosis: str
    treatment: str | None = None
    treatment_duration: str | None = None
    outcome_status: OutcomeStatus = OutcomeStatus.PENDING
    outcome_notes: str | None = None
    tags_json: dict | None = None


class ClinicalCaseUpdate(BaseModel):
    symptoms_json: dict | None = None
    provisional_diagnosis: str | None = None
    treatment: str | None = None
    treatment_duration: str | None = None
    outcome_status: OutcomeStatus | None = None
    outcome_notes: str | None = None
    tags_json: dict | None = None
    is_synced: bool | None = None


class ClinicalCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    facility_id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    symptoms_json: dict
    provisional_diagnosis: str
    treatment: str | None = None
    treatment_duration: str | None = None
    outcome_status: OutcomeStatus
    outcome_notes: str | None = None
    tags_json: dict | None = None
    is_synced: bool
    created_at: datetime
    updated_at: datetime


# --- Audit Log ---
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None = None
    facility_id: uuid.UUID | None = None
    action: str
    resource: str
    resource_id: str | None = None
    details: dict | None = None
    ip_address: str | None = None
    timestamp: datetime


# --- Sync ---
class SyncPayload(BaseModel):
    items: list[dict[str, Any]]


class SyncResponse(BaseModel):
    synced: int
    failed: int
    conflicts: list[dict[str, Any]] = []
