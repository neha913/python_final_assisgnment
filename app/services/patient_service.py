from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime
from app.repositories.user_repository import UserRepository
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.models import User, Availability, Appointment
from app.schemas import AppointmentCreate


class PatientService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.availability_repo = AvailabilityRepository(session)
        self.appointment_repo = AppointmentRepository(session)

    async def list_doctors(self) -> List[User]:
        return await self.user_repo.get_doctors()

    async def get_doctor_availability(self, doctor_id: int) -> List[Availability]:
        # Verify doctor exists
        doctor = await self.user_repo.get_by_id(doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        return await self.availability_repo.get_by_doctor_id(doctor_id)

    async def book_appointment(self, patient_id: int, appointment_data: AppointmentCreate) -> Appointment:
        # Verify doctor exists
        doctor = await self.user_repo.get_by_id(appointment_data.doctor_id)
        if not doctor:
            raise ValueError("Doctor not found")

        # Verify availability exists and is available
        availability = await self.availability_repo.get_by_id(appointment_data.availability_id)
        if not availability:
            raise ValueError("Availability not found")

        if not availability.is_available:
            raise ValueError("This time slot is no longer available")

        if availability.doctor_id != appointment_data.doctor_id:
            raise ValueError("Availability does not belong to this doctor")

        # Check if appointment time is within availability window
        if not (availability.start_time <= appointment_data.appointment_time <= availability.end_time):
            raise ValueError("Appointment time must be within availability window")

        # Check for double-booking
        has_conflict = await self.appointment_repo.check_conflict(
            appointment_data.doctor_id,
            appointment_data.appointment_time,
            appointment_data.availability_id
        )
        if has_conflict:
            raise ValueError("This time slot is already booked")

        # Create appointment and mark availability as unavailable
        appointment = await self.appointment_repo.create(
            doctor_id=appointment_data.doctor_id,
            patient_id=patient_id,
            availability_id=appointment_data.availability_id,
            appointment_time=appointment_data.appointment_time
        )

        # Mark availability as unavailable
        await self.availability_repo.mark_unavailable(appointment_data.availability_id)

        return appointment

    async def cancel_appointment(self, appointment_id: int, patient_id: int) -> Appointment:
        appointment = await self.appointment_repo.cancel(appointment_id, patient_id, "Patient")
        if not appointment:
            raise ValueError("Appointment not found or you don't have permission to cancel it")

        # Mark availability as available again
        await self.availability_repo.mark_available(appointment.availability_id)

        return appointment

