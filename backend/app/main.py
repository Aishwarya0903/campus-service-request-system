"""
FastAPI application for the AI-Powered Campus Service Request System.
"""

from __future__ import annotations

import os
import threading
import time
import uuid

from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import jwt

from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from passlib.context import CryptContext

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
    select,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


# =========================================================
# CONFIGURATION
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./campus.db",
)

SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "change-me-in-production",
)

ALGORITHM = "HS256"
ACCESS_MINUTES = 480


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
    if DATABASE_URL.startswith("sqlite")
    else {},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


auth_scheme = HTTPBearer()


# =========================================================
# DATABASE BASE
# =========================================================

class Base(DeclarativeBase):
    pass


# =========================================================
# ENUMS
# =========================================================

class Role(str, Enum):
    STUDENT = "STUDENT"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class Status(str, Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


# =========================================================
# DATABASE MODELS
# =========================================================

class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default=Role.STUDENT.value,
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


class Ticket(Base):

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    location: Mapped[str] = mapped_column(
        String(160)
    )

    attachment_path: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(50)
    )

    priority: Mapped[str] = mapped_column(
        String(20)
    )

    department: Mapped[str] = mapped_column(
        String(50)
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=Status.OPEN.value,
        index=True,
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    assigned_staff_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="LOW",
    )

    high_risk_since: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    escalated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resolution_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    student = relationship(
        "User",
        foreign_keys=[student_id],
    )

    assigned_staff = relationship(
        "User",
        foreign_keys=[assigned_staff_id],
    )


class Notification(Base):

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    ticket_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tickets.id"),
        nullable=True,
    )

    message: Mapped[str] = mapped_column(
        String(300)
    )

    kind: Mapped[str] = mapped_column(
        String(30)
    )

    read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class SlaRule(Base):

    __tablename__ = "sla_rules"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    category: Mapped[str] = mapped_column(
        String(50),
        unique=True,
    )

    hours: Mapped[int] = mapped_column(
        Integer,
        default=48,
    )

    risk_threshold: Mapped[float] = mapped_column(
        Float,
        default=0.7,
    )

    grace_hours: Mapped[int] = mapped_column(
        Integer,
        default=6,
    )


class History(Base):

    __tablename__ = "ticket_status_history"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id")
    )

    status: Mapped[str] = mapped_column(
        String(20)
    )

    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    changed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class ModelVersion(Base):

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    version: Mapped[str] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


# =========================================================
# PYDANTIC SCHEMAS
# =========================================================

class Register(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(
        min_length=8
    )


class Login(BaseModel):
    email: str
    password: str


class TicketCreate(BaseModel):
    description: str = Field(
        min_length=10,
        max_length=3000,
    )

    location: str = Field(
        min_length=2,
        max_length=160,
    )


class TicketPatch(BaseModel):

    status: Optional[Status] = None

    resolution_notes: Optional[str] = None

    assigned_staff_id: Optional[int] = None


class RulePatch(BaseModel):

    hours: int = Field(
        ge=1,
        le=720,
    )

    risk_threshold: float = Field(
        ge=0.01,
        le=0.99,
    )

    grace_hours: int = Field(
        ge=1,
        le=168,
    )


class UserPatch(BaseModel):

    name: Optional[str] = None

    role: Optional[str] = None

    department: Optional[str] = None

    active: Optional[bool] = None


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def db():

    session = SessionLocal()

    try:
        yield session

    finally:
        session.close()


# =========================================================
# AUTHENTICATION
# =========================================================

def token_for(user):

    return jwt.encode(
        {
            "sub": str(user.id),
            "role": user.role,
            "exp": (
                datetime.now(timezone.utc)
                + timedelta(
                    minutes=ACCESS_MINUTES
                )
            ),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def me(
    credentials: HTTPAuthorizationCredentials = Depends(
        auth_scheme
    ),
    s: Session = Depends(db),
):

    try:

        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(
            payload["sub"]
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        )


    user = s.get(
        User,
        user_id,
    )


    if not user or not user.active:

        raise HTTPException(
            status_code=401,
            detail="Account unavailable",
        )


    return user


def require(*roles):

    def dependency(
        user=Depends(me),
    ):

        if user.role not in roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "This role is not permitted "
                    "to perform that action"
                ),
            )

        return user

    return dependency


# =========================================================
# HELPERS
# =========================================================

def notify(
    s,
    user_id,
    ticket_id,
    message,
    kind,
):

    s.add(
        Notification(
            user_id=user_id,
            ticket_id=ticket_id,
            message=message,
            kind=kind,
        )
    )


def ticket_out(
    ticket: Ticket,
):

    return {
        "id": ticket.id,

        "description":
            ticket.description,

        "location":
            ticket.location,

        "category":
            ticket.category,

        "priority":
            ticket.priority,

        "department":
            ticket.department,

        "status":
            ticket.status,

        "student":
            ticket.student.name
            if ticket.student
            else None,

        "assigned_staff":
            ticket.assigned_staff.name
            if ticket.assigned_staff
            else None,

        "deadline":
            ticket.deadline,

        "risk_score":
            round(
                ticket.risk_score,
                3,
            ),

        "risk_level":
            ticket.risk_level,

        "created_at":
            ticket.created_at,

        "resolution_notes":
            ticket.resolution_notes,
    }


# =========================================================
# ML CATEGORY / PRIORITY PREDICTION
# =========================================================

def classify(text):

    import joblib

    model_path = (
        ROOT
        / "ml"
        / "models"
        / "classifier.joblib"
    )


    if not model_path.exists():

        raise HTTPException(
            status_code=503,
            detail=(
                "ML artifacts not found. "
                "Run: python ml/training/train_models.py"
            ),
        )


    artifact = joblib.load(
        model_path
    )


    category = artifact[
        "category"
    ].predict(
        [text]
    )[0]


    priority = artifact[
        "priority"
    ].predict(
        [text]
    )[0]


    return category, priority


# =========================================================
# SLA RISK PREDICTION
# =========================================================

def sla_score(
    s,
    ticket,
):

    import joblib
    import pandas as pd


    created_at = (
        ticket.created_at
    )

    if created_at.tzinfo is None:

        created_at = created_at.replace(
            tzinfo=timezone.utc
        )


    elapsed = max(
        0,
        (
            datetime.now(timezone.utc)
            - created_at
        ).total_seconds()
        / 3600,
    )


    workload = (
        s.scalar(
            select(
                func.count(
                    Ticket.id
                )
            ).where(
                Ticket.department
                == ticket.department,

                Ticket.status.in_(
                    [
                        Status.OPEN.value,
                        Status.ASSIGNED.value,
                        Status.IN_PROGRESS.value,
                    ]
                ),
            )
        )
        or 0
    )


    model_path = (
        ROOT
        / "ml"
        / "models"
        / "sla.joblib"
    )


    if not model_path.exists():

        raise HTTPException(
            status_code=503,
            detail=(
                "SLA ML artifact not found. "
                "Run: python ml/training/train_models.py"
            ),
        )


    features = pd.DataFrame(
        [
            {
                "elapsed_hours":
                    elapsed,

                "category":
                    ticket.category,

                "priority":
                    ticket.priority,

                "hour":
                    created_at.hour,

                "day_of_week":
                    created_at.weekday(),

                "workload":
                    workload,
            }
        ]
    )


    model = joblib.load(
        model_path
    )


    return float(
        model.predict_proba(
            features
        )[0][1]
    )


# =========================================================
# SLA RE-EVALUATION
# =========================================================

def reevaluate(s):

    now = datetime.now(
        timezone.utc
    )


    open_states = [
        Status.OPEN.value,
        Status.ASSIGNED.value,
        Status.IN_PROGRESS.value,
    ]


    tickets = s.scalars(
        select(Ticket).where(
            Ticket.status.in_(
                open_states
            )
        )
    ).all()


    for ticket in tickets:

        rule = s.scalar(
            select(SlaRule).where(
                SlaRule.category
                == ticket.category
            )
        )


        if not rule:
            continue


        score = sla_score(
            s,
            ticket,
        )


        ticket.risk_score = score


        if score >= rule.risk_threshold:

            ticket.risk_level = "HIGH"

        elif score >= (
            rule.risk_threshold * 0.65
        ):

            ticket.risk_level = "MEDIUM"

        else:

            ticket.risk_level = "LOW"


        if ticket.risk_level == "HIGH":

            if not ticket.high_risk_since:

                ticket.high_risk_since = now


                recipients = s.scalars(
                    select(User).where(
                        (
                            User.department
                            == ticket.department
                        )
                        |
                        (
                            User.role
                            == Role.ADMIN.value
                        )
                    )
                ).all()


                for user in recipients:

                    notify(
                        s,
                        user.id,
                        ticket.id,
                        (
                            f"Ticket #{ticket.id} "
                            "is high SLA risk."
                        ),
                        "SLA_RISK",
                    )


            elif (
                now
                - ticket.high_risk_since
                >= timedelta(
                    hours=rule.grace_hours
                )
                and not ticket.escalated_at
            ):

                ticket.status = (
                    Status.ESCALATED.value
                )

                ticket.escalated_at = now


                admins = s.scalars(
                    select(User).where(
                        User.role
                        == Role.ADMIN.value
                    )
                ).all()


                for admin in admins:

                    notify(
                        s,
                        admin.id,
                        ticket.id,
                        (
                            f"Ticket #{ticket.id} "
                            "was escalated after "
                            "the SLA grace period."
                        ),
                        "ESCALATED",
                    )

        else:

            ticket.high_risk_since = None


    s.commit()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title=(
        "AI-Powered Campus "
        "Service Request System"
    ),
    version="0.8.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173",
    ).split(","),

    allow_methods=["*"],

    allow_headers=["*"],

    allow_credentials=True,
)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup():

    Base.metadata.create_all(
        engine
    )


    def loop():

        while True:

            time.sleep(
                int(
                    os.getenv(
                        "SLA_EVALUATION_MINUTES",
                        "5",
                    )
                )
                * 60
            )


            session = SessionLocal()


            try:

                reevaluate(
                    session
                )

            except Exception as exc:

                print(
                    "SLA evaluation failed:",
                    exc,
                )

            finally:

                session.close()


    threading.Thread(
        target=loop,
        daemon=True,
        name="sla-evaluator",
    ).start()


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# AUTH - REGISTER
# =========================================================

@app.post("/auth/register")
def register(
    data: Register,
    s: Session = Depends(db),
):

    existing = s.scalar(
        select(User).where(
            User.email == data.email
        )
    )


    if existing:

        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )


    user = User(
        name=data.name,
        email=data.email,
        password_hash=pwd.hash(
            data.password
        ),
    )


    s.add(user)
    s.commit()
    s.refresh(user)


    return {
        "access_token":
            token_for(user),

        "id":
            user.id,

        "name":
            user.name,

        "email":
            user.email,

        "role":
            user.role,

        "department":
            user.department,
    }


# =========================================================
# AUTH - LOGIN
# =========================================================

@app.post("/auth/login")
def login(
    data: Login,
    s: Session = Depends(db),
):

    user = s.scalar(
        select(User).where(
            User.email == data.email
        )
    )


    if (
        not user
        or not pwd.verify(
            data.password,
            user.password_hash,
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )


    if not user.active:

        raise HTTPException(
            status_code=403,
            detail=(
                "Your account has been "
                "deactivated. Please contact "
                "the administrator."
            ),
        )


    return {
        "access_token":
            token_for(user),

        "id":
            user.id,

        "name":
            user.name,

        "email":
            user.email,

        "role":
            user.role,

        "department":
            user.department,
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/users/me")
def current_user(
    user=Depends(me),
):

    return {
        "id":
            user.id,

        "name":
            user.name,

        "email":
            user.email,

        "role":
            user.role,

        "department":
            user.department,
    }


# =========================================================
# CREATE TICKET
# =========================================================

@app.post("/tickets")
def create_ticket(
    data: TicketCreate,

    user=Depends(
        require(
            Role.STUDENT.value
        )
    ),

    s: Session = Depends(db),
):

    category, priority = classify(
        data.description
    )


    rule = s.scalar(
        select(SlaRule).where(
            SlaRule.category
            == category
        )
    )


    if not rule:

        raise HTTPException(
            status_code=500,
            detail=(
                f"No SLA rule configured "
                f"for category {category}"
            ),
        )


    ticket = Ticket(
        description=data.description,

        location=data.location,

        category=category,

        priority=priority,

        department=category,

        student_id=user.id,

        deadline=(
            datetime.now(timezone.utc)
            + timedelta(
                hours=rule.hours
            )
        ),
    )


    s.add(ticket)
    s.flush()


    s.add(
        History(
            ticket_id=ticket.id,

            status=Status.OPEN.value,

            changed_by=user.id,

            note=(
                "Ticket submitted "
                "and classified"
            ),
        )
    )


    notify(
        s,
        user.id,
        ticket.id,
        (
            f"Ticket #{ticket.id} submitted. "
            f"Predicted category: {category}; "
            f"priority: {priority}."
        ),
        "SUBMITTED",
    )


    s.commit()
    s.refresh(ticket)


    return ticket_out(
        ticket
    )


# =========================================================
# ATTACHMENT
# =========================================================

@app.post(
    "/tickets/{ticket_id}/attachment"
)
async def upload_attachment(
    ticket_id: int,

    file: UploadFile = File(...),

    user=Depends(
        require(
            Role.STUDENT.value
        )
    ),

    s: Session = Depends(db),
):

    ticket = s.get(
        Ticket,
        ticket_id,
    )


    if (
        not ticket
        or ticket.student_id != user.id
    ):

        raise HTTPException(
            status_code=404,
            detail="Your ticket was not found",
        )


    if file.content_type not in {
        "image/jpeg",
        "image/png",
    }:

        raise HTTPException(
            status_code=415,
            detail=(
                "Only JPEG and PNG "
                "images are accepted"
            ),
        )


    content = await file.read()


    if len(content) > 5 * 1024 * 1024:

        raise HTTPException(
            status_code=413,
            detail=(
                "Image must be "
                "5 MB or smaller"
            ),
        )


    folder = ROOT / "uploads"

    folder.mkdir(
        exist_ok=True
    )


    if "." in file.filename:

        extension = (
            file.filename
            .rsplit(".", 1)[-1]
            .lower()
        )

    else:

        extension = "jpg"


    filename = (
        f"{ticket_id}-"
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )


    path = folder / filename

    path.write_bytes(
        content
    )


    ticket.attachment_path = (
        str(filename)
    )


    s.commit()


    return {
        "filename":
            filename
    }


# =========================================================
# GET TICKETS
# =========================================================

@app.get("/tickets")
def tickets(
    user=Depends(me),
    s: Session = Depends(db),
):

    query = select(
        Ticket
    )


    if user.role == Role.STUDENT.value:

        query = query.where(
            Ticket.student_id
            == user.id
        )


    elif user.role == Role.STAFF.value:

        query = query.where(
            Ticket.department
            == user.department
        )


    ticket_list = s.scalars(
        query.order_by(
            Ticket.created_at.desc()
        )
    ).all()


    return [
        ticket_out(ticket)
        for ticket in ticket_list
    ]


# =========================================================
# GET SINGLE TICKET
# =========================================================

@app.get(
    "/tickets/{ticket_id}"
)
def one_ticket(
    ticket_id: int,

    user=Depends(me),

    s: Session = Depends(db),
):

    ticket = s.get(
        Ticket,
        ticket_id,
    )


    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )


    if (
        user.role
        == Role.STUDENT.value
        and ticket.student_id
        != user.id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You can only view "
                "your own tickets"
            ),
        )


    if (
        user.role
        == Role.STAFF.value
        and ticket.department
        != user.department
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Ticket is outside "
                "your department"
            ),
        )


    history = s.scalars(
        select(History)
        .where(
            History.ticket_id
            == ticket.id
        )
        .order_by(
            History.changed_at
        )
    ).all()


    return {
        **ticket_out(ticket),

        "history": [
            {
                "status":
                    item.status,

                "note":
                    item.note,

                "changed_at":
                    item.changed_at,
            }

            for item in history
        ],
    }


# =========================================================
# UPDATE TICKET
# =========================================================

@app.patch(
    "/tickets/{ticket_id}"
)
def patch_ticket(
    ticket_id: int,

    data: TicketPatch,

    user=Depends(
        require(
            Role.STAFF.value,
            Role.ADMIN.value,
        )
    ),

    s: Session = Depends(db),
):

    ticket = s.get(
        Ticket,
        ticket_id,
    )


    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )


    if (
        user.role
        == Role.STAFF.value
        and ticket.department
        != user.department
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Ticket is outside "
                "your department"
            ),
        )


    if data.assigned_staff_id is not None:

        assigned = s.get(
            User,
            data.assigned_staff_id,
        )


        if not assigned:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Assigned staff member "
                    "not found"
                ),
            )


        if assigned.role not in {
            Role.STAFF.value,
            Role.ADMIN.value,
        }:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Ticket can only be "
                    "assigned to staff "
                    "or admin users"
                ),
            )


        ticket.assigned_staff_id = (
            data.assigned_staff_id
        )


    if data.resolution_notes is not None:

        ticket.resolution_notes = (
            data.resolution_notes
        )


    if data.status is not None:

        ticket.status = (
            data.status.value
        )


        s.add(
            History(
                ticket_id=ticket.id,

                status=ticket.status,

                changed_by=user.id,

                note=data.resolution_notes,
            )
        )


        notify(
            s,
            ticket.student_id,
            ticket.id,
            (
                f"Ticket #{ticket.id} "
                f"status changed to "
                f"{ticket.status}."
            ),
            "STATUS",
        )


    ticket.updated_at = (
        datetime.now(timezone.utc)
    )


    s.commit()
    s.refresh(ticket)


    return ticket_out(
        ticket
    )


# =========================================================
# ESCALATE TICKET
# =========================================================

@app.post(
    "/tickets/{ticket_id}/escalate"
)
def escalate(
    ticket_id: int,

    user=Depends(
        require(
            Role.STAFF.value,
            Role.ADMIN.value,
        )
    ),

    s: Session = Depends(db),
):

    ticket = s.get(
        Ticket,
        ticket_id,
    )


    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )


    if (
        user.role
        == Role.STAFF.value
        and ticket.department
        != user.department
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Ticket is outside "
                "your department"
            ),
        )


    ticket.status = (
        Status.ESCALATED.value
    )


    ticket.escalated_at = (
        datetime.now(timezone.utc)
    )


    notify(
        s,
        ticket.student_id,
        ticket.id,
        (
            f"Ticket #{ticket.id} "
            "has been escalated."
        ),
        "ESCALATED",
    )


    s.commit()


    return ticket_out(
        ticket
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.get("/notifications")
def notifications(
    user=Depends(me),
    s: Session = Depends(db),
):

    items = s.scalars(
        select(Notification)
        .where(
            Notification.user_id
            == user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
    ).all()


    return [
        {
            "id":
                item.id,

            "message":
                item.message,

            "kind":
                item.kind,

            "read":
                item.read,

            "created_at":
                item.created_at,
        }

        for item in items
    ]


@app.patch(
    "/notifications/{notification_id}/read"
)
def read_notification(
    notification_id: int,

    user=Depends(me),

    s: Session = Depends(db),
):

    notification = s.get(
        Notification,
        notification_id,
    )


    if (
        not notification
        or notification.user_id
        != user.id
    ):

        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )


    notification.read = True

    s.commit()


    return {
        "ok": True
    }


# =========================================================
# SLA RULES
# =========================================================

@app.get("/sla/rules")
def rules(
    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    rules_list = s.scalars(
        select(SlaRule)
        .order_by(
            SlaRule.category
        )
    ).all()


    return [
        {
            "category":
                rule.category,

            "hours":
                rule.hours,

            "risk_threshold":
                rule.risk_threshold,

            "grace_hours":
                rule.grace_hours,
        }

        for rule in rules_list
    ]


@app.put(
    "/sla/rules/{category}"
)
def update_rule(
    category: str,

    data: RulePatch,

    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    rule = s.scalar(
        select(SlaRule).where(
            SlaRule.category
            == category
        )
    )


    if not rule:

        raise HTTPException(
            status_code=404,
            detail="SLA rule not found",
        )


    rule.hours = data.hours

    rule.risk_threshold = (
        data.risk_threshold
    )

    rule.grace_hours = (
        data.grace_hours
    )


    s.commit()


    return {
        "ok": True
    }


@app.post(
    "/sla/evaluate"
)
def evaluate_sla(
    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    reevaluate(
        s
    )


    return {
        "ok": True
    }


# =========================================================
# ANALYTICS
# =========================================================

@app.get(
    "/analytics/overview"
)
def analytics(
    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    all_tickets = s.scalars(
        select(Ticket)
    ).all()


    open_tickets = [
        ticket
        for ticket in all_tickets
        if ticket.status in {
            Status.OPEN.value,
            Status.ASSIGNED.value,
            Status.IN_PROGRESS.value,
        }
    ]


    resolved_tickets = [
        ticket
        for ticket in all_tickets
        if ticket.status in {
            Status.RESOLVED.value,
            Status.CLOSED.value,
        }
    ]


    durations = []


    for ticket in resolved_tickets:

        created = ticket.created_at
        updated = ticket.updated_at

        if created.tzinfo is None:
            created = created.replace(
                tzinfo=timezone.utc
            )

        if updated.tzinfo is None:
            updated = updated.replace(
                tzinfo=timezone.utc
            )

        durations.append(
            (
                updated - created
            ).total_seconds()
            / 3600
        )


    def group_by(attribute):

        values = sorted(
            set(
                getattr(
                    ticket,
                    attribute,
                )
                for ticket in all_tickets
            )
        )


        return {
            value:
                sum(
                    getattr(
                        ticket,
                        attribute,
                    )
                    == value
                    for ticket in all_tickets
                )

            for value in values
        }


    compliant = sum(
        ticket.updated_at
        <= ticket.deadline
        for ticket in resolved_tickets
    )


    sla_rate = (
        round(
            100
            * compliant
            / len(resolved_tickets),
            2,
        )
        if resolved_tickets
        else 0
    )


    departments = [
        "Electrical",
        "Plumbing",
        "IT/Network",
        "Hostel",
    ]


    department_workload = {}


    for department in departments:

        department_workload[
            department
        ] = sum(
            ticket.department
            == department
            and ticket.status in {
                Status.OPEN.value,
                Status.ASSIGNED.value,
                Status.IN_PROGRESS.value,
            }
            for ticket in all_tickets
        )


    return {

        "total":
            len(all_tickets),

        "open":
            len(open_tickets),

        "resolved":
            len(resolved_tickets),

        "escalated":
            sum(
                ticket.status
                == Status.ESCALATED.value
                for ticket in all_tickets
            ),

        "average_resolution_hours":
            round(
                sum(durations)
                / len(durations),
                2,
            )
            if durations
            else 0,

        "sla_compliance_rate":
            sla_rate,

        "by_category":
            group_by("category"),

        "by_priority":
            group_by("priority"),

        "by_status":
            group_by("status"),

        "department_workload":
            department_workload,

        "high_risk": [
            ticket_out(ticket)

            for ticket in all_tickets

            if ticket.risk_level
            == "HIGH"
        ],
    }


# =========================================================
# ADMIN USER MANAGEMENT
# =========================================================

@app.get(
    "/admin/users"
)
def admin_users(
    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    users = s.scalars(
        select(User)
        .order_by(
            User.id
        )
    ).all()


    return [
        {
            "id":
                item.id,

            "name":
                item.name,

            "email":
                item.email,

            "role":
                item.role,

            "department":
                item.department,

            "active":
                item.active,
        }

        for item in users
    ]


@app.patch(
    "/admin/users/{user_id}"
)
def update_admin_user(
    user_id: int,

    data: UserPatch,

    user=Depends(
        require(
            Role.ADMIN.value
        )
    ),

    s: Session = Depends(db),
):

    target = s.get(
        User,
        user_id,
    )


    if not target:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )


    if data.name is not None:

        target.name = data.name


    if data.role is not None:

        if data.role not in {
            Role.STUDENT.value,
            Role.STAFF.value,
            Role.ADMIN.value,
        }:

            raise HTTPException(
                status_code=400,
                detail="Invalid user role",
            )


        target.role = data.role


    if data.department is not None:

        target.department = (
            data.department
        )


    if data.active is not None:

        if (
            target.id == user.id
            and not data.active
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "You cannot deactivate "
                    "your own account"
                ),
            )


        target.active = data.active


    s.commit()
    s.refresh(target)


    return {
        "id":
            target.id,

        "name":
            target.name,

        "email":
            target.email,

        "role":
            target.role,

        "department":
            target.department,

        "active":
            target.active,
    }