from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models import UserRole


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


# User Schemas
class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Availability Schemas
class AvailabilityCreate(BaseModel):
    start_time: datetime
    end_time: datetime


class AvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


# Appointment Schemas
class AppointmentCreate(BaseModel):
    doctor_id: int
    availability_id: int
    appointment_time: datetime


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    availability_id: int
    appointment_time: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AppointmentWithDetails(AppointmentResponse):
    doctor: UserResponse
    patient: UserResponse


# Doctor Schemas
class DoctorResponse(UserResponse):
    pass


class DoctorAvailabilityResponse(BaseModel):
    doctor: DoctorResponse
    availabilities: List[AvailabilityResponse]

