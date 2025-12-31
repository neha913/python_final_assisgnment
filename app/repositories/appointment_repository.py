from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
from app.models import Appointment


class AppointmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, doctor_id: int, patient_id: int, availability_id: int, appointment_time: datetime
    ) -> Appointment:
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            availability_id=availability_id,
            appointment_time=appointment_time,
            status="scheduled"
        )
        self.session.add(appointment)
        await self.session.commit()
        await self.session.refresh(appointment)
        return appointment

    async def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        result = await self.session.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_patient_id(self, patient_id: int) -> List[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .where(Appointment.status == "scheduled")
            .order_by(Appointment.appointment_time)
        )
        return list(result.scalars().all())

    async def get_by_doctor_id(self, doctor_id: int) -> List[Appointment]:
        result = await self.session.execute(
            select(Appointment)
            .where(Appointment.doctor_id == doctor_id)
            .where(Appointment.status == "scheduled")
            .order_by(Appointment.appointment_time)
        )
        return list(result.scalars().all())

    async def check_conflict(
        self, doctor_id: int, appointment_time: datetime, availability_id: int
    ) -> bool:
        result = await self.session.execute(
            select(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.availability_id == availability_id,
                    Appointment.status == "scheduled"
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def cancel(self, appointment_id: int, user_id: int, user_role: str) -> Optional[Appointment]:
        appointment = await self.get_by_id(appointment_id)
        if not appointment:
            return None

       
        if user_role == "Patient" and appointment.patient_id != user_id:
            return None

        appointment.status = "cancelled"
        await self.session.commit()
        await self.session.refresh(appointment)
        return appointment

