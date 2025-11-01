from pydantic import BaseModel, ConfigDict

class RoomBase(BaseModel):
    name: str
    capacity: int

class RoomCreate(RoomBase):
    """Schema for creating room"""
    pass

class RoomRead(RoomBase):
    """Schema for returning room"""
    id: int

    model_config = ConfigDict(from_attributes=True)


