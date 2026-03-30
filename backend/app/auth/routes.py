from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test")
async def test_auth():
    return {"status": "auth working"}

from fastapi import APIRouter

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/test")
async def test_auth():
    return {"status": "auth working"}
