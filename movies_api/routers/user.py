from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.jwt_manager import create_token
from schemas.user import User

user_router = APIRouter()


@user_router.post('/login', tags=["auth"])
def login(user:User):
    token = False
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
    
    if not token:
        return JSONResponse(status_code=404, content="No encontrado")
           
    return JSONResponse(status_code=200, content=token)