from typing import Annotated

from fastapi import APIRouter, Depends
from api.auth import get_current_user
from api.models import User
from api.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
