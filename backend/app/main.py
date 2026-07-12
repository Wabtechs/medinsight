from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select
from app.config import get_settings
from app.database import init_db, async_session_factory
from app.application.exceptions import AppException

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


async def seed_default_data():
    """Seed default users, facility, patients, and cases if DB is empty."""
    from app.domain.models import Facility, User, Patient, ClinicalCase
    from app.domain.enums import UserRole, OutcomeStatus, FacilityType
    from app.infrastructure.security import get_password_hash
    import uuid

    async with async_session_factory() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return

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

        users = [
            User(
                id=uuid.uuid4(), facility_id=facility.id,
                firstname="Admin", lastname="MedInsight",
                email="admin@medinsight.dz",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN, is_active=True,
            ),
            User(
                id=uuid.uuid4(), facility_id=facility.id,
                firstname="Youcef", lastname="Benali",
                email="dr.benali@medinsight.dz",
                password_hash=get_password_hash("doctor123"),
                role=UserRole.DOCTOR, is_active=True,
            ),
            User(
                id=uuid.uuid4(), facility_id=facility.id,
                firstname="Amina", lastname="Khelifi",
                email="researcher@medinsight.dz",
                password_hash=get_password_hash("researcher123"),
                role=UserRole.RESEARCHER, is_active=True,
            ),
        ]
        db.add_all(users)
        await db.flush()

        doctor = users[1]
        patients = []
        for sex, age, bg in [("M", 45, "A+"), ("F", 32, "O+"), ("M", 67, "B-"), ("F", 28, "AB+"), ("M", 55, "A-")]:
            patients.append(Patient(
                id=uuid.uuid4(), facility_id=facility.id,
                sex=sex, age=age, blood_group=bg,
                medical_history_json={"conditions": [], "allergies": []},
                is_active=True,
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
        ]
        for i, (diag, treatment, status) in enumerate(cases_data, 1):
            db.add(ClinicalCase(
                id=uuid.uuid4(), facility_id=facility.id,
                patient_id=patients[i % len(patients)].id,
                doctor_id=doctor.id,
                symptoms_json={"primary": diag, "severity": "moderate"},
                provisional_diagnosis=diag, treatment=treatment,
                treatment_duration=f"{i} mois", outcome_status=status,
                outcome_notes=f"Suivi du cas {i}",
                tags_json={"tags": []}, is_synced=True,
            ))

        await db.commit()
        print("Default data seeded: 3 users, 5 patients, 10 cases")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_default_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MedInsight - Medical SaaS Platform API for clinical case management and health data analytics",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


from app.presentation.router_auth import router as auth_router
from app.presentation.router_users import router as users_router
from app.presentation.router_facilities import router as facilities_router
from app.presentation.router_patients import router as patients_router
from app.presentation.router_clinical_cases import router as clinical_cases_router
from app.presentation.router_audit import router as audit_router
from app.presentation.router_sync import router as sync_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(facilities_router, prefix="/api/v1")
app.include_router(patients_router, prefix="/api/v1")
app.include_router(clinical_cases_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(sync_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
