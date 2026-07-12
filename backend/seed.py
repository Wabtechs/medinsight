import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.database import Base
from app.domain.models import Facility, User, Patient, ClinicalCase, AuditLog
from app.domain.enums import UserRole, OutcomeStatus, FacilityType
from app.infrastructure.security import get_password_hash

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, echo=False)
session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        facility = Facility(
            id=uuid.uuid4(),
            name="CHU Mustapha Algiers",
            code="CHU-MUSTAPHA-ALG",
            facility_type=FacilityType.HOSPITAL,
            address="Place du 1er Novembre 1954",
            city="Algiers",
            phone="+213 21 91 15 15",
            email="contact@chumustapha.dz",
            is_active=True,
        )
        db.add(facility)
        await db.flush()

        admin = User(
            id=uuid.uuid4(),
            facility_id=facility.id,
            firstname="Admin",
            lastname="MedInsight",
            email="admin@medinsight.dz",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        doctor = User(
            id=uuid.uuid4(),
            facility_id=facility.id,
            firstname="Youcef",
            lastname="Benali",
            email="dr.benali@medinsight.dz",
            password_hash=get_password_hash("doctor123"),
            role=UserRole.DOCTOR,
            is_active=True,
        )
        researcher = User(
            id=uuid.uuid4(),
            facility_id=facility.id,
            firstname="Amina",
            lastname="Khelifi",
            email="researcher@medinsight.dz",
            password_hash=get_password_hash("researcher123"),
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        db.add_all([admin, doctor, researcher])
        await db.flush()

        patients = []
        for i, (sex, age, bg) in enumerate([
            ("M", 45, "A+"),
            ("F", 32, "O+"),
            ("M", 67, "B-"),
            ("F", 28, "AB+"),
            ("M", 55, "A-"),
        ], 1):
            p = Patient(
                id=uuid.uuid4(),
                facility_id=facility.id,
                sex=sex,
                age=age,
                blood_group=bg,
                medical_history_json={"conditions": [], "allergies": []},
                is_active=True,
            )
            patients.append(p)
        db.add_all(patients)
        await db.flush()

        cases_data = [
            ("Migraine chronique", "Paracetamol 1g/jour", "SUCCESS", ["neurology"]),
            ("Diabete type 2", "Metformine 850mg", "IN_PROGRESS", ["endocrinology"]),
            ("Hypertension arterielle", "Lisinopril 10mg", "PENDING", ["cardiology"]),
            ("Asthme persistant", "Salbutamol inhalateur", "SUCCESS", ["pulmonology"]),
            ("Arthrose genou", "Physiotherapie", "IN_PROGRESS", ["rheumatology"]),
            ("Insuffisance renale", "Dialyse", "FAILURE", ["nephrology"]),
            ("Pneumonie bacterienne", "Amoxicilline 1g", "SUCCESS", ["pulmonology"]),
            ("Gastrite chronique", "Omeprazole 20mg", "PENDING", ["gastroenterology"]),
            ("Anemie ferriprive", "Sulfate ferreux", "SUCCESS", ["hematology"]),
            ("Depression majeure", "Sertraline 50mg", "IN_PROGRESS", ["psychiatry"]),
        ]

        for i, (diag, treatment, status, tags) in enumerate(cases_data, 1):
            case = ClinicalCase(
                id=uuid.uuid4(),
                facility_id=facility.id,
                patient_id=patients[i % len(patients)].id,
                doctor_id=doctor.id,
                symptoms_json={"primary": diag, "severity": "moderate"},
                provisional_diagnosis=diag,
                treatment=treatment,
                treatment_duration=f"{i} mois",
                outcome_status=status,
                outcome_notes=f"Suivi du cas {i}",
                tags_json={"tags": tags},
                is_synced=True,
            )
            db.add(case)

        await db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
