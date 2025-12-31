from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.services.patient_service import PatientService
from app.schemas import AppointmentCreate, AppointmentResponse
from app.middleware.auth_middleware import get_current_user, require_role
from app.models import UserRole

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.PATIENT]))
):
    """Book an appointment (Patient only)"""
    patient_service = PatientService(db)
    try:
        appointment = await patient_service.book_appointment(
            current_user["user_id"],
            appointment_data
        )
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's appointments"""
    from app.repositories.appointment_repository import AppointmentRepository
    
    appointment_repo = AppointmentRepository(db)
    if current_user["role"] == UserRole.DOCTOR.value:
        appointments = await appointment_repo.get_by_doctor_id(current_user["user_id"])
    else:
        appointments = await appointment_repo.get_by_patient_id(current_user["user_id"])
    
    return appointments


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role([UserRole.PATIENT]))
):
    """Cancel an appointment (Patient only)"""
    patient_service = PatientService(db)
    try:
        appointment = await patient_service.cancel_appointment(
            appointment_id,
            current_user["user_id"]
        )
        return appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

