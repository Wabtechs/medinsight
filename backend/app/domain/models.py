import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, Integer, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain.enums import UserRole, OutcomeStatus, FacilityType


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    facility_type: Mapped[FacilityType] = mapped_column(String(50), default=FacilityType.HOSPITAL)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    users: Mapped[list["User"]] = relationship(back_populates="facility", lazy="selectin")
    patients: Mapped[list["Patient"]] = relationship(back_populates="facility", lazy="selectin")
    clinical_cases: Mapped[list["ClinicalCase"]] = relationship(back_populates="facility", lazy="selectin")

    __table_args__ = (
        Index("ix_facilities_city", "city"),
        Index("ix_facilities_type", "facility_type"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True)
    firstname: Mapped[str] = mapped_column(String(100))
    lastname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(String(50), default=UserRole.DOCTOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    facility: Mapped["Facility"] = relationship(back_populates="users", lazy="selectin")
    clinical_cases: Mapped[list["ClinicalCase"]] = relationship(back_populates="doctor", lazy="selectin")

    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_facility_email", "facility_id", "email"),
    )


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True)
    patient_uuid: Mapped[uuid.UUID] = mapped_column(unique=True, index=True, default=uuid.uuid4)
    sex: Mapped[str] = mapped_column(String(1))
    age: Mapped[int] = mapped_column(Integer)
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)
    medical_history_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    facility: Mapped["Facility"] = relationship(back_populates="patients", lazy="selectin")
    clinical_cases: Mapped[list["ClinicalCase"]] = relationship(back_populates="patient", lazy="selectin")

    __table_args__ = (
        Index("ix_patients_sex", "sex"),
        Index("ix_patients_blood_group", "blood_group"),
        Index("ix_patients_facility_active", "facility_id", "is_active"),
    )


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id"), index=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    symptoms_json: Mapped[dict] = mapped_column(JSON)
    provisional_diagnosis: Mapped[str] = mapped_column(Text)
    treatment: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatment_duration: Mapped[str | None] = mapped_column(String, nullable=True)
    outcome_status: Mapped[OutcomeStatus] = mapped_column(String(50), default=OutcomeStatus.PENDING)
    outcome_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    facility: Mapped["Facility"] = relationship(back_populates="clinical_cases", lazy="selectin")
    patient: Mapped["Patient"] = relationship(back_populates="clinical_cases", lazy="selectin")
    doctor: Mapped["User"] = relationship(back_populates="clinical_cases", lazy="selectin")

    __table_args__ = (
        Index("ix_cases_outcome", "outcome_status"),
        Index("ix_cases_facility_doctor", "facility_id", "doctor_id"),
        Index("ix_cases_created_at", "created_at"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    facility_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("facilities.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100))
    resource: Mapped[str] = mapped_column(String(100))
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user: Mapped["User | None"] = relationship(lazy="selectin")
    facility: Mapped["Facility | None"] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_audit_action", "action"),
        Index("ix_audit_resource", "resource"),
        Index("ix_audit_timestamp", "timestamp"),
        Index("ix_audit_user_action", "user_id", "action"),
    )


class SyncQueue(Base):
    __tablename__ = "sync_queue"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(20))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(lazy="selectin")

    __table_args__ = (
        Index("ix_sync_status_created", "status", "created_at"),
        Index("ix_sync_user_entity", "user_id", "entity_type"),
    )
