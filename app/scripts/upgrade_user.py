import asyncio
from sqlalchemy.future import select

from app.db import get_async_session, User  

async def promote_user_to_superuser(email: str):
    async for session in get_async_session():
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"No user found with email: {email}")
            return

        if user.is_superuser:
            print(f"User {email} is already a superuser.")
            return

        user.is_superuser = True
        session.add(user)
        await session.commit()
        print(f"User {email} promoted to superuser.")


if __name__ == "__main__":
    email_to_promote = input("Enter user email to promote: ").strip()
    asyncio.run(promote_user_to_superuser(email_to_promote))

