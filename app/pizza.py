from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import async_session
from .models import Pizza, Admin
from .authentication import get_current_admin
from .schema import PizzaCreate, PizzaResponse

router = APIRouter()

@router.post("/pizzas/", response_model=PizzaResponse)
async def create_pizza(pizza: PizzaCreate, db: AsyncSession = Depends(async_session), admin: Admin = Depends(get_current_admin)):
    new_pizza = Pizza(**pizza.dict())
    db.add(new_pizza)
    await db.commit()
    await db.refresh(new_pizza)
    return new_pizza

@router.get("/pizzas/", response_model=list[PizzaResponse])
async def get_pizzas(db: AsyncSession = Depends(async_session)):
    result = await db.execute(select(Pizza))
    pizzas = result.scalars().all()
    return pizzas

@router.put("/pizzas/{pizza_id}", response_model=PizzaResponse)
async def update_pizza(
    pizza_id: int, pizza: PizzaCreate, db: AsyncSession = Depends(async_session), admin: Admin = Depends(get_current_admin)
):
    db_pizza = await db.execute(select(Pizza).filter(Pizza.id == pizza_id))
    db_pizza = db_pizza.scalars().first()
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    
    for key, value in pizza.dict().items():
        setattr(db_pizza, key, value)
    await db.commit()
    await db.refresh(db_pizza)
    return db_pizza

@router.delete("/pizzas/{pizza_id}")
async def delete_pizza(
    pizza_id: int, db: AsyncSession = Depends(async_session), admin: Admin = Depends(get_current_admin)
):
    db_pizza = await db.execute(select(Pizza).filter(Pizza.id == pizza_id))
    db_pizza = db_pizza.scalars().first()
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    
    await db.delete(db_pizza)
    await db.commit()
    return {"detail": "Pizza deleted successfully"}
