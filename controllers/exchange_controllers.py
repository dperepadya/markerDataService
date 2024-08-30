import crud
from database import get_db
from api_data_manager import data_manager
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

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
async def delete_exchange(exchange_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_exchange(db, exchange_id)
    return RedirectResponse("/exchanges/", status_code=303)

@router.get("/{exchange_id}/symbols/", response_class=HTMLResponse)
async def get_exchange_symbols_list(exchange_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    symbols = await crud.get_exchange_symbols(db, exchange_id)
    # print(symbols)
    return templates.TemplateResponse(request=request, name="symbols.html", context={"symbols": symbols,
                                                                                     "exchange_id": exchange_id})
@router.get("/{exchange_id}/symbols/add/", response_class=HTMLResponse)
async def add_exchange_symbol_form(request: Request, exchange_id: int, error: str = Query(None),
                                   db: AsyncSession = Depends(get_db)):
    db_symbols = await crud.get_exchange_symbols(db, exchange_id)
    symbols = data_manager.get_exchange_symbols(exchange_id)
    db_symbols_names = {symbol.name for symbol in db_symbols}
    new_symbols = [s for s in symbols if s['name'] not in db_symbols_names]
    new_symbols.sort(key=lambda x: x['name'])
    # print(new_symbols)
    return templates.TemplateResponse(request=request, name="symbol_add.html",
                                      context={"symbols": new_symbols, "exchange_id": exchange_id, "error": error})

@router.post("/{exchange_id}/symbols/add/", response_class=HTMLResponse)
async def add_exchange_symbol(request: Request, db: AsyncSession = Depends(get_db)):
    form_data = await request.form()
    symbol_name = form_data.get("symbol_name")
    exchange_id = int(form_data.get("exchange_id"))
    symbol_data = data_manager.get_exchange_symbol_by_id(exchange_id, symbol_name)
    # print(symbol_data)
    await crud.add_exchange_symbol(db, symbol_data)
    return RedirectResponse(url=f"/exchanges/{exchange_id}/symbols", status_code=303)

@router.get("/{exchange_id}/symbols/{symbol_id}/", response_class=HTMLResponse)
async def get_exchange_symbol(exchange_id: int, symbol_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    symbol = await crud.get_exchange_symbol_by_id(db, exchange_id, symbol_id)
    print('symbol', symbol)
    return templates.TemplateResponse(request=request, name="symbol.html", context={"symbol": symbol})

@router.post("/{exchange_id}/symbols/{symbol_id}/delete/", response_class=HTMLResponse)
async def get_exchange_symbol(exchange_id: int, symbol_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    await crud.delete_exchange_symbol(db, exchange_id, symbol_id)
    return RedirectResponse(url=f"/exchanges/{exchange_id}/symbols", status_code=303)
