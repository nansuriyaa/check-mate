from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from api.auth import get_current_user_from_cookie
from api.models import User
import os

router = APIRouter(tags=["frontend"])

# Assuming templates folder is at root relative to where app is run
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: User | None = Depends(get_current_user_from_cookie)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: User | None = Depends(get_current_user_from_cookie)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user: User | None = Depends(get_current_user_from_cookie)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@router.get("/", response_class=HTMLResponse)
async def root_page(request: Request, user: User | None = Depends(get_current_user_from_cookie)):
    if user:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")
