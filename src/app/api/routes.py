from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session

router = APIRouter()


async def get_db():
    async with async_session() as session:
        yield session


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/users")
async def create_user(payload: dict, db: AsyncSession = Depends(get_db)):
    # simple example endpoint creating a user record
    from app.models.user import User

    if "name" not in payload:
        raise HTTPException(status_code=400, detail="name is required")

    user = User(name=payload.get("name"), email=payload.get("email"))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}
