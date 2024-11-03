from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User, Admin, Pizza

async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: User):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_admin(db: AsyncSession, admin: Admin):
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin

async def create_pizza(db: AsyncSession, pizza: Pizza):
    db.add(pizza)
    await db.commit()
    await db.refresh(pizza)
    return pizza

async def get_all_pizzas(db: AsyncSession):
    result = await db.execute(select(Pizza))
    return result.scalars().all()

# Add more CRUD operations as needed
