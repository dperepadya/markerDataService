from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

import crud
from crud import get_exchanges
from database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_exchange_symbols_list(exchange_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    symbols = await crud.get_exchange_symbols(db, exchange_id)
    return templates.TemplateResponse(request=request, name="symbols.html", context={"symbols": symbols})

@router.get("/add", response_class=HTMLResponse)
async def add_exchange_symbol_form(request: Request, error: str = Query(None)):
    return templates.TemplateResponse(request=request, name="symbol_add.html", context={"error": error})

@router.post("/", response_class=HTMLResponse)
async def add_exchange_symbol(request: Request, db: AsyncSession = Depends(get_db)):
    form_data = await request.form()
    symbol_data = form_data.get("symbol")
    await crud.add_exchange_symbol(db, symbol_data)

@router.post("/{symbol_id}", response_class=HTMLResponse)
async def get_exchange_symbol(exchange_id: int, symbol_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    symbol = crud.get_exchange_symbol_by_id(db, exchange_id, symbol_id)
    return templates.TemplateResponse(request=request, name="symbol.html", context={"symbol": symbol})

@router.post("/{symbol_id}/delete", response_class=HTMLResponse)
async def get_exchange_symbol(exchange_id: int, symbol_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    symbol = crud.delete_exchange_symbol(db, exchange_id, symbol_id)
    return RedirectResponse(url=f"/exchanges/{exchange_id}symbols", status_code=303)
