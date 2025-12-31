from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from app.models import Availability


class AvailabilityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, doctor_id: int, start_time: datetime, end_time: datetime) -> Availability:
        availability = Availability(
            doctor_id=doctor_id,
            start_time=start_time,
            end_time=end_time,
            is_available=True
        )
        self.session.add(availability)
        await self.session.commit()
        await self.session.refresh(availability)
        return availability

    async def get_by_doctor_id(self, doctor_id: int) -> List[Availability]:
        result = await self.session.execute(
            select(Availability)
            .where(Availability.doctor_id == doctor_id)
            .where(Availability.is_available == True)
        )
        return list(result.scalars().all())

    async def get_by_id(self, availability_id: int) -> Optional[Availability]:
        result = await self.session.execute(
            select(Availability).where(Availability.id == availability_id)
        )
        return result.scalar_one_or_none()

    async def mark_unavailable(self, availability_id: int) -> None:
        result = await self.session.execute(
            select(Availability).where(Availability.id == availability_id)
        )
        availability = result.scalar_one_or_none()
        if availability:
            availability.is_available = False
            await self.session.commit()

    async def mark_available(self, availability_id: int) -> None:
        result = await self.session.execute(
            select(Availability).where(Availability.id == availability_id)
        )
        availability = result.scalar_one_or_none()
        if availability:
            availability.is_available = True
            await self.session.commit()

    async def check_overlap(
        self, doctor_id: int, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None
    ) -> bool:
        query = select(Availability).where(
            and_(
                Availability.doctor_id == doctor_id,
                Availability.is_available == True,
                Availability.start_time < end_time,
                Availability.end_time > start_time
            )
        )
        if exclude_id:
            query = query.where(Availability.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

