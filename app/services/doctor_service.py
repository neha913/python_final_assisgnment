from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone
from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.user_repository import UserRepository
from app.models import Availability, Appointment
from app.schemas import AvailabilityCreate


class DoctorService:
    def __init__(self, session: AsyncSession):
        self.availability_repo = AvailabilityRepository(session)
        self.appointment_repo = AppointmentRepository(session)
        self.user_repo = UserRepository(session)

    async def set_availability(self, doctor_id: int, availability: AvailabilityCreate) -> Availability:
        # Check for overlapping availabilities
        has_overlap = await self.availability_repo.check_overlap(
            doctor_id, availability.start_time, availability.end_time
        )
        if has_overlap:
            raise ValueError("Availability overlaps with existing time slot")

        if availability.start_time >= availability.end_time:
            raise ValueError("Start time must be before end time")

        if availability.start_time < datetime.now(timezone.utc):
            raise ValueError("Cannot set availability in the past")

        return await self.availability_repo.create(
            doctor_id, availability.start_time, availability.end_time
        )

    async def get_upcoming_appointments(self, doctor_id: int) -> List[Appointment]:
        return await self.appointment_repo.get_by_doctor_id(doctor_id)

