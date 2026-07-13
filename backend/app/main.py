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
    """Seed default data if DB is empty."""
    from app.domain.models import Facility, User, Patient, ClinicalCase
    from app.domain.enums import UserRole, FacilityType
    from app.infrastructure.security import get_password_hash
    import uuid

    async with async_session_factory() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        # ── Facilities ──
        facilities = []
        fac_data = [
            ("CHU Mustapha", "CHU-MUSTAPHA-ALG", FacilityType.HOSPITAL,
             "1, Place Lieutenant Turki", "Alger", "+213 21 50 00 00", "contact@chumustapha.dz"),
            ("Hôpital Bab El Oued", "HOP-BAB-EL-OUED", FacilityType.HOSPITAL,
             "45, Rue de Tripoli", "Alger", "+213 21 80 00 00", "contact@hopbab-el-oued.dz"),
            ("Clinique El Fath", "CLIN-EL-FATH", FacilityType.CLINIC,
             "22, Rue des Frères Abbas", "Alger", "+213 21 90 00 00", "info@cliniquefath.dz"),
            ("Hôpital Parnet", "HOP-PARNET", FacilityType.HOSPITAL,
             "10, Route de Zeralda", "Alger", "+213 21 40 00 00", "contact@hop-parnet.dz"),
            ("Centre Médical Hydra", "CM-HYDRA", FacilityType.LABORATORY,
             "7, Rue Amirouche", "Alger", "+213 21 60 00 00", "contact@cm-hydra.dz"),
        ]
        for name, code, ftype, addr, city, phone, email in fac_data:
            f = Facility(id=uuid.uuid4(), name=name, code=code, facility_type=ftype,
                         address=addr, city=city, phone=phone, email=email, is_active=True)
            facilities.append(f)
            db.add(f)
        await db.flush()

        f = facilities[0]  # primary facility

        # ── Users ──
        users = [
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Admin", lastname="MedInsight",
                 email="admin@medinsight.dz", password_hash=get_password_hash("admin123"),
                 role=UserRole.ADMIN, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Sara", lastname="Boudiaf",
                 email="sara.admin@medinsight.dz", password_hash=get_password_hash("admin123"),
                 role=UserRole.ADMIN, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Sarah", lastname="Benali",
                 email="dr.benali@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Fatima", lastname="Zerhouni",
                 email="dr.zerhouni@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Karim", lastname="Mansouri",
                 email="dr.mansouri@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Amine", lastname="Slimani",
                 email="dr.aitahmed@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Omar", lastname="Taleb",
                 email="dr.taleb@medinsight.dz", password_hash=get_password_hash("doctor123"),
                 role=UserRole.DOCTOR, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Nadia", lastname="Bouzid",
                 email="researcher@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Rachid", lastname="Bouzid",
                 email="rachid.research@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
            User(id=uuid.uuid4(), facility_id=f.id, firstname="Nadia", lastname="Cherif",
                 email="nadia.research@medinsight.dz", password_hash=get_password_hash("researcher123"),
                 role=UserRole.RESEARCHER, is_active=True),
        ]
        db.add_all(users)
        await db.flush()
        doctors = [u for u in users if u.role == UserRole.DOCTOR]

        # ── Patients ──
        patients = []
        patient_data = [
            ("Aïcha", "Boudiaf", "F", 66, "A+", {"allergies": ["Pénicilline", "Arachides"]}),
            ("Rachid", "Mebarki", "M", 50, "O+", {"allergies": ["Iode"]}),
            ("Lydia", "Zeroual", "F", 43, "B-", {"allergies": ["Aspirine", "Latex"]}),
            ("Omar", "Taleb", "M", 59, "AB+", {"allergies": []}),
            ("Souad", "Benmalek", "F", 35, "O-", {"allergies": ["Sulfamides"]}),
            ("Djamel", "Kharchi", "M", 72, "A-", {"allergies": ["Morphine", "Pollens"]}),
            ("Meriem", "Ait Ahmed", "F", 37, "B+", {"allergies": ["Produits laitiers"]}),
            ("Samir", "Boucherit", "M", 53, "O+", {"allergies": []}),
            ("Dalila", "Mansouri", "F", 61, "A+", {"allergies": ["Cacahuètes"]}),
            ("Farid", "Guermazi", "M", 30, "AB-", {"allergies": ["Ibuprofène"]}),
            ("Naima", "Charef", "F", 45, "O+", {"allergies": ["Codeïne"]}),
            ("Abdelkader", "Rebiai", "M", 68, "B+", {"allergies": ["Pénicilline"]}),
            ("Sabrina", "Djaballah", "F", 27, "A+", {"allergies": []}),
            ("Youcef", "Hadj", "M", 41, "O-", {"allergies": ["Latex"]}),
            ("Amina", "Touati", "F", 33, "B-", {"allergies": ["Arachides"]}),
        ]
        for fn, ln, sex, age, bg, hist in patient_data:
            p = Patient(
                id=uuid.uuid4(), facility_id=f.id,
                sex=sex, age=age, blood_group=bg,
                medical_history_json=hist, is_active=True,
            )
            patients.append(p)
            db.add(p)
        await db.flush()

        # ── Clinical Cases ──
        cases_data = [
            ("Migraine chronique", "Céphalées persistantes, nausées, photophobie",
             "Paracétamol 1g/jour + triptans", "3 mois", "SUCCESS"),
            ("Diabète type 2", "Polyurie, polydipsie, fatigue, perte de poids",
             "Metformine 850mg 2x/jour", "6 mois", "IN_PROGRESS"),
            ("Hypertension artérielle", "Pression artérielle 160/100, maux de tête",
             "Lisinopril 10mg/jour", "4 mois", "PENDING"),
            ("Asthme persistant", "Dyspnée sifflante, toux nocturne",
             "Salbutamol inhalateur PRN + Budesonide", "2 mois", "SUCCESS"),
            ("Arthrose du genou", "Douleur mécanique, raideur matinale",
             "Physiothérapie + Paracétamol", "5 mois", "IN_PROGRESS"),
            ("Insuffisance rénale chronique", "Œdèmes, fatigue, créatinine élevée",
             "Dialyse 3x/semaine + régime hyposodé", "12 mois", "FAILURE"),
            ("Pneumonie bactérienne", "Fièvre, toux productive, dyspnée",
             "Amoxicilline 1g 3x/jour", "2 semaines", "SUCCESS"),
            ("Gastrite chronique", "Douleurs épigastriques, brûlures",
             "Oméprazole 20mg/jour", "1 mois", "PENDING"),
            ("Anémie ferriprive", "Pâleur, fatigue, essoufflement",
             "Sulfate ferreux 200mg 3x/jour", "3 mois", "SUCCESS"),
            ("Dépression majeure", "Tristesse persistante, insomnie, anhédonie",
             "Sertraline 50mg/jour", "6 mois", "IN_PROGRESS"),
            ("Cardiopathie ischémique", "Douleur thoracique à l'effort",
             "Aspirine 75mg + Atorvastatine 20mg", "8 mois", "IN_PROGRESS"),
            ("Bronchopneumonie", "Fièvre élevée, expectoration purulente",
             "Ceftriaxone 1g IV + Azithromycine", "3 semaines", "SUCCESS"),
            ("Cirrhose hépatique", "Ascite, ictère, hépatomégalie",
             "Spironolactone 100mg + régime sans sel", "12 mois", "FAILURE"),
            ("Polyarthrite rhumatoïde", "Raideur matinale, douleurs articulaires bilatérales",
             "Méthotrexate 15mg/semaine", "10 mois", "IN_PROGRESS"),
            ("AVC ischémique", "Hémiplégie droite, troubles du langage",
             "Plavix 75mg + rééducation", "4 mois", "PENDING"),
            ("Ulcère gastrique", "Douleur épigastrique post-prandiale",
             "Pantoprazole 40mg + Hp. pylori eradication", "2 mois", "SUCCESS"),
            ("Kyste ovarien", "Douleur pelvienne, métrorragies",
             "Surveillance échographique + Antalgie", "3 mois", "PENDING"),
            ("Lombalgie chronique", "Douleur lombaire irradiante",
             "Diclofenac + Kinésithérapie", "6 mois", "IN_PROGRESS"),
            ("Diabète gestationnel", "Hyperglycémie au 2e trimestre",
             "Régime + Insuline NPH", "4 mois", "SUCCESS"),
            ("Tuberculose pulmonaire", "Toux chronique, sueurs nocturnes, Amaigrissement",
             "Quadrithérapie 2RHZE/4RH", "6 mois", "IN_PROGRESS"),
        ]
        for i, (diag, symptoms, treat, dur, status) in enumerate(cases_data, 1):
            db.add(ClinicalCase(
                id=uuid.uuid4(), facility_id=f.id,
                patient_id=patients[i % len(patients)].id,
                doctor_id=doctors[i % len(doctors)].id,
                symptoms_json={"primary": diag, "description": symptoms, "severity": "moderate"},
                provisional_diagnosis=diag, treatment=treat,
                treatment_duration=dur, outcome_status=status,
                outcome_notes=f"Suivi du cas {i}", tags_json={"tags": []}, is_synced=True,
            ))

        await db.commit()
        print(f"Seed done: {len(facilities)} facilities, {len(users)} users, {len(patients)} patients, {len(cases_data)} cases")


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
