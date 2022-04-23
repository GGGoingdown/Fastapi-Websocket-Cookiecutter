from loguru import logger

# Application
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


view_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_router.get("/dashboard")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
