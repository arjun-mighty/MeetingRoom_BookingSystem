from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class BookingBase(BaseModel):
    room_id: int
    start_time: datetime = Field(..., description="Booking start datetime")
    end_time: datetime = Field(..., description="Booking end datetime")
    purpose: str | None = None

class BookingCreate(BookingBase):
    """Create Booking"""
    pass

class BookingRead(BookingBase):
    """Booking response"""
    id: int
    user_id: str

    model_config = ConfigDict(from_attributes=True)

