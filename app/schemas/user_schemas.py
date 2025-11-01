import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for returning user"""
    pass


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating user"""
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user"""
    pass
