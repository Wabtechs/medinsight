import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.database import Base
from app.domain.models import Facility, User, Patient, ClinicalCase
from app.domain.enums import UserRole, FacilityType
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
            id=uuid.uuid4(), name="CHU Mustapha Algiers", code="CHU-MUSTAPHA-ALG",
            facility_type=FacilityType.HOSPITAL, address="Place du 1er Novembre 1954",
            city="Algiers", phone="+213 21 91 15 15", email="contact@chumustapha.dz", is_active=True,
        )
        db.add(facility)
        await db.flush()

        users = [
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Admin", lastname="MedInsight",
                 email="admin@medinsight.dz", password_hash=get_password_hash("admin123"),
                 role=UserRole.ADMIN, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Sara", lastname="Boudiaf",
                 email="sara.admin@medinsight.dz", password_hash=get_password_hash("admin123"),
                 role=UserRole.ADMIN, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Youcef", lastname="Benali",
                 email="dr.benali@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Fatima", lastname="Zerhouni",
                 email="dr.zerhouni@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Karim", lastname="Mansouri",
                 email="dr.mansouri@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Lydia", lastname="Ait Ahmed",
                 email="dr.aitahmed@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Omar", lastname="Taleb",
                 email="dr.taleb@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Amina", lastname="Khelifi",
                 email="researcher@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Rachid", lastname="Bouzid",
                 email="rachid.research@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
            User(id=uuid.uuid4(), facility_id=facility.id, firstname="Nadia", lastname="Cherif",
                 email="nadia.research@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
        ]
        db.add_all(users)
        await db.flush()

        doctors = [u for u in users if u.role == UserRole.DOCTOR]

        patients = []
        for sex, age, bg in [
            ("M", 45, "A+"), ("F", 32, "O+"), ("M", 67, "B-"), ("F", 28, "AB+"), ("M", 55, "A-"),
            ("F", 41, "O-"), ("M", 23, "A+"), ("F", 70, "B+"), ("M", 38, "AB-"), ("F", 52, "A+"),
            ("M", 61, "O+"), ("F", 29, "B-"), ("M", 48, "A-"), ("F", 35, "AB+"), ("M", 73, "O+"),
        ]:
            patients.append(Patient(
                id=uuid.uuid4(), facility_id=facility.id, sex=sex, age=age, blood_group=bg,
                medical_history_json={"conditions": [], "allergies": []}, is_active=True,
            ))
        db.add_all(patients)
        await db.flush()

        cases_data = [
            ("Migraine chronique", "Paracetamol 1g/jour", "SUCCESS"),
            ("Diabete type 2", "Metformine 850mg", "IN_PROGRESS"),
            ("Hypertension arterielle", "Lisinopril 10mg", "PENDING"),
            ("Asthme persistant", "Salbutamol inhalateur", "SUCCESS"),
            ("Arthrose genou", "Physiotherapie", "IN_PROGRESS"),
            ("Insuffisance renale", "Dialyse", "FAILURE"),
            ("Pneumonie bacterienne", "Amoxicilline 1g", "SUCCESS"),
            ("Gastrite chronique", "Omeprazole 20mg", "PENDING"),
            ("Anemie ferriprive", "Sulfate ferreux", "SUCCESS"),
            ("Depression majeure", "Sertraline 50mg", "IN_PROGRESS"),
            ("Cardiopathie ischemique", "Aspirine 75mg + Atorvastatine", "IN_PROGRESS"),
            ("Bronchopneumonie", "Ceftriaxone 1g IV", "SUCCESS"),
            ("Cirrhose hepatique", "Spironolactone 100mg", "FAILURE"),
            ("Polyarthrite rhumatoide", "Methotrexate 15mg/semaine", "IN_PROGRESS"),
            ("AVC ischemique", "Plavix 75mg + rehabilitation", "PENDING"),
            ("Ulcere gastrique", "Pantoprazole 40mg", "SUCCESS"),
            ("Kyste ovarien", "Surveillance + Antalgie", "PENDING"),
            ("Lombalgie chronique", "Diclofenac + Kinésithérapie", "IN_PROGRESS"),
            ("Diabete gestationnel", "Regime + Insuline", "SUCCESS"),
            ("Tuberculose pulmonaire", "Quadri thérapie 6 mois", "IN_PROGRESS"),
        ]
        for i, (diag, treatment, status) in enumerate(cases_data, 1):
            db.add(ClinicalCase(
                id=uuid.uuid4(), facility_id=facility.id,
                patient_id=patients[i % len(patients)].id,
                doctor_id=doctors[i % len(doctors)].id,
                symptoms_json={"primary": diag, "severity": "moderate"},
                provisional_diagnosis=diag, treatment=treatment,
                treatment_duration=f"{i} mois", outcome_status=status,
                outcome_notes=f"Suivi du cas {i}",
                tags_json={"tags": []}, is_synced=True,
            ))

        await db.commit()
        print(f"Seed done: {len(users)} users, {len(patients)} patients, {len(cases_data)} cases")


if __name__ == "__main__":
    asyncio.run(seed())
