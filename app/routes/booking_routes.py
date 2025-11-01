from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db import get_async_session
from app.models.room import Room
from app.models.booking import Booking
from app.schemas.booking_schemas import BookingCreate, BookingRead
from app.models.users import current_active_user

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingRead)
async def create_booking(
    booking: BookingCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """
    Create a booking for room.
    """

    # Make sure start time is greater than or equal to current time
    current_time = datetime.now(timezone.utc)
    if booking.start_time < current_time:
        raise HTTPException(
            status_code=400, detail="Start time must be greater than current time"
        )

    # Make sure end time is greater than start time
    if booking.start_time >= booking.end_time:
        raise HTTPException(
            status_code=400, detail="Start time must be before end time."
        )

    # Make sure max room duration is 4hrs
    delta = booking.end_time - booking.start_time
    if  delta.total_seconds() > 4*60*60:
        raise HTTPException(
            status_code=400, detail="Exceeds the Max duration for a single booking (4 hours)."
        )

    # Check if room exists
    result = await session.execute(select(Room).where(Room.id == booking.room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    # Check for overlapping bookings
    overlap_query = select(Booking).where(
        and_(
            Booking.room_id == booking.room_id,
            Booking.start_time < booking.end_time,
            Booking.end_time > booking.start_time,
        )
    )
    result = await session.execute(overlap_query)
    overlapping = result.scalar_one_or_none()
    if overlapping:
        raise HTTPException(
            status_code=400, detail="Room is already booked for that time range."
        )

    new_booking = Booking(
        room_id=booking.room_id,
        user_id=str(user.id),
        start_time=booking.start_time,
        end_time=booking.end_time,
        purpose=booking.purpose,
    )

    session.add(new_booking)
    await session.commit()
    await session.refresh(new_booking)
    return new_booking


@router.get("/", response_model=list[BookingRead])
async def list_bookings(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    query = select(Booking)
    result = await session.execute(query)
    return result.scalars().all()


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """Delete a booking"""

    # Fetch existing record
    result = await session.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    # Make sure it's not empty
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Make sure either superuser or original user 
    if (not user.is_superuser) and booking.user_id != str(user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking.")

    await session.delete(booking)
    await session.commit()
    return None

