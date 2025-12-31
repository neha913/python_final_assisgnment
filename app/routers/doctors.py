from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.patient_service import PatientService
from app.services.doctor_service import DoctorService
from app.schemas import DoctorResponse, DoctorAvailabilityResponse, AvailabilityResponse, AvailabilityCreate
from app.middleware.auth_middleware import get_current_user, require_role
from app.models import UserRole

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=List[DoctorResponse])
async def list_doctors(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all available doctors"""
    patient_service = PatientService(db)
    doctors = await patient_service.list_doctors()
    return doctors


@router.get("/{doctor_id}/availability", response_model=List[AvailabilityResponse])
async def get_doctor_availability(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get availability for a specific doctor"""
    patient_service = PatientService(db)
    try:
        availabilities = await patient_service.get_doctor_availability(doctor_id)
        return availabilities
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/availability", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
async def set_availability(
    availability: AvailabilityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.DOCTOR]))
):
    """Set availability (Doctor only)"""
    doctor_service = DoctorService(db)
    try:
        new_availability = await doctor_service.set_availability(
            current_user["user_id"],
            availability
        )
        return new_availability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/appointments/upcoming", response_model=List[dict])
async def get_upcoming_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.DOCTOR]))
):
    """Get upcoming appointments (Doctor only)"""
    doctor_service = DoctorService(db)
    appointments = await doctor_service.get_upcoming_appointments(current_user["user_id"])
    return [
        {
            "id": apt.id,
            "patient_id": apt.patient_id,
            "appointment_time": apt.appointment_time,
            "status": apt.status
        }
        for apt in appointments
    ]

