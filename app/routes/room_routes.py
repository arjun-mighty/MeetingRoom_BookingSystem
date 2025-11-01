from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_async_session
from app.models.room import Room
from app.schemas.room_schemas import RoomCreate, RoomRead
from app.models.users import current_active_user

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room: RoomCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """Create room"""

    # Check if admin or not
    if not user.is_superuser:
        raise HTTPException(status_code=403)

    # Check if room exits or not
    existing = await session.execute(select(Room).where(Room.name == room.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Room with this name already exists.")

    new_room = Room(name=room.name, capacity=room.capacity)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room


@router.get("/", response_model=list[RoomRead])
async def list_rooms(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    result = await session.execute(select(Room))
    return result.scalars().all()


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(
    room_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    result = await session.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")
    return room


@router.put("/{room_id}", response_model=RoomRead)
async def update_room(
    room_id: int,
    updated_room: RoomCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):

    # Check if admin or not
    if not user.is_superuser:
        raise HTTPException(status_code=403)

    # Check if room exits or not
    result = await session.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    # Check if room name is alredy exists
    result1 = await session.execute(select(Room).where(Room.name == updated_room.name))
    if result1.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Room name alredy taken.")

    room.name = updated_room.name
    room.capacity = updated_room.capacity
    session.add(room)
    await session.commit()
    await session.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user),
):
    """
    Delete room
    """

    # Check if admin or not
    if not user.is_superuser:
        raise HTTPException(status_code=403)

    # Check if room exits or not
    result = await session.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    await session.delete(room)
    await session.commit()
    return None

