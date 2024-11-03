from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import async_session, engine
from models import Pizza, Admin , User, PizzaCreate, PizzaResponse, UserCreate , AdminCreate, AdminResponse, verify_password
from database import async_session, engine
from authetication import create_access_token, hash_password , get_current_admin, get_current_user, get_db
from sqlalchemy.orm import Session
from fastapi import Path


app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Pizza.metadata.create_all)

@app.post("/register/")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the username already exists
    existing_user = await db.execute(select(User).filter(User.username == user.username))
    if existing_user.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    return {"msg": "User created successfully"}

@app.post("/admin/register")
async def register_admin(username: str, password: str, db: AsyncSession = Depends(get_db)):
    existing_admin = await db.execute(select(Admin).filter(Admin.username == username))
    if existing_admin.scalars().first():
        raise HTTPException(status_code=400, detail="Admin username already exists")

    hashed_password = hash_password(password)
    new_admin = Admin(username=username, hashed_password=hashed_password)
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return {"msg": "Admin created successfully"}

@app.post("/login/")
async def login_admin(admin: AdminCreate, db: AsyncSession = Depends(get_db)):
    db_admin = await db.execute(select(Admin).filter(Admin.username == admin.username))
    db_admin = db_admin.scalars().first()
    
    # Check if admin exists and verify password
    if not db_admin or not verify_password(admin.password, db_admin.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

# User Login
@app.post("/login/")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await db.execute(select(User).filter(User.username == user.username))
    db_user = db_user.scalars().first()
    
    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/pizzas/", response_model=PizzaResponse)
async def create_pizza(pizza_data: PizzaCreate, db: AsyncSession = Depends(get_db), 
                       admin: Admin = Depends(get_current_admin)):
    new_pizza = Pizza(**pizza.dict())
    db.add(new_pizza)
    await db.commit()
    await db.refresh(new_pizza)
    return new_pizza

@app.get("/pizzas/", response_model=list[PizzaResponse])
async def get_pizzas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pizza))
    pizzas = result.scalars().all()
    return pizzas

@app.put("/pizzas/{pizza_id}", response_model=PizzaResponse)
async def update_pizza(
    pizza_id: int, pizza: PizzaCreate, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)
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

@app.delete("/pizzas/{pizza_id}")
async def delete_pizza(
    pizza_id: int, db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)
):
    db_pizza = await db.execute(select(Pizza).filter(Pizza.id == pizza_id))
    db_pizza = db_pizza.scalars().first()
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    
    await db.delete(db_pizza)
    await db.commit()
    return {"detail": "Pizza deleted successfully"}