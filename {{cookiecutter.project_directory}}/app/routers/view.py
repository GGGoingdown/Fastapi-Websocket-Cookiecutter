# Application
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


view_router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@view_router.get("/long-trip")
def long_trip_dashboard(request: Request):
    return templates.TemplateResponse("long_trip.html", {"request": request})


@view_router.get("/interval-info")
def interval_info_dashboard(request: Request):
    return templates.TemplateResponse("interval_info.html", {"request": request})
