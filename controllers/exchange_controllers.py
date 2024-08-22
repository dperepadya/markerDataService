from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates
from models import Exchange
import crud
from database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_exchanges_list(request: Request, db: AsyncSession = Depends(get_db)):
    exchanges = await crud.get_exchanges(db)
    return templates.TemplateResponse(request=request, name="exchanges.html", context={"exchanges": exchanges})

@router.get("/add/", response_class=HTMLResponse)
async def add_exchange_form(request: Request):
    return templates.TemplateResponse(request=request, name="exchange_add.html", context={})

@router.post("/add/", response_class=HTMLResponse)
async def add_exchange(request: Request, db: AsyncSession = Depends(get_db)):
    form_data = await request.form()
    exchange_data = dict(form_data)
    await crud.add_exchange(db, exchange_data)
    return RedirectResponse("/exchanges/", status_code=303)

@router.get("/{exchange_id}/", response_class=HTMLResponse)
async def get_exchange_by_id(request: Request, exchange_id: int, db: AsyncSession = Depends(get_db)):
    exchange = await crud.get_exchange_by_id(db, exchange_id)
    return templates.TemplateResponse(request=request, name="exchange.html", context={"exchange": exchange})

@router.post("/{exchange_id}/delete/", response_class=HTMLResponse)
async def delete_exchange(request: Request, exchange_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_exchange(db, exchange_id)
    return RedirectResponse("/exchanges/", status_code=303)




