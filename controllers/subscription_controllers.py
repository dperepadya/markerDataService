import logging

from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

from api_data_manager import data_manager
from db_models import Exchange
import crud
from database import get_db

logging.basicConfig(level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_subscriptions_list(request: Request, db: AsyncSession = Depends(get_db)):
    subscriptions = await crud.get_subscriptions(db)
    return templates.TemplateResponse(request=request, name="subscriptions.html",
                                      context={"subscriptions": subscriptions})

@router.get("/add/", response_class=HTMLResponse)
async def select_exchange_form(request: Request, db: AsyncSession = Depends(get_db)):
    exchanges = await crud.get_exchanges(db)
    # print('exchanges', exchanges)
    return templates.TemplateResponse(request=request, name="select_exchange.html", context={"exchanges": exchanges})

@router.post("/add/", response_class=HTMLResponse)
async def add_subscription(request: Request, name: str = Form(...), type: str = Form(...), symbol_id: int = Form(...),
                           exchange_id: int = Form(...), db: AsyncSession = Depends(get_db)):
    subscription_data = {"name": name, "type": type, "exchange_id": exchange_id, "symbol_id": symbol_id,
                         "is_active": False}
    print('subscription data', subscription_data)
    await crud.add_subscription(db, subscription_data)
    return RedirectResponse("/subscriptions/", status_code=303)

@router.get("/select_symbol/", response_class=HTMLResponse)
async def select_symbol_form(request: Request, db: AsyncSession = Depends(get_db)):
    exchange_id = int(request.query_params.get("exchange_id"))
    print('subscription add exchange id', exchange_id)
    symbols = await crud.get_exchange_symbols(db, exchange_id)
    types = {'trades', 'order_book'}
    return templates.TemplateResponse(request=request, name="select_symbol.html",
                                      context={"symbols": symbols, "types": types, "exchange_id": exchange_id})

@router.get("/unsubscribe/", response_class=HTMLResponse)
async def unsubscribe(request: Request, db: AsyncSession = Depends(get_db)):
    await data_manager.unsubscribe_all(db)
    return RedirectResponse("/subscriptions/", status_code=303)

@router.get("/{subscription_id}/", response_class=HTMLResponse)
async def get_subscription_by_id(request: Request, subscription_id: int, db: AsyncSession = Depends(get_db)):
    subscription = await crud.get_subscription_by_id(db, subscription_id)
    return templates.TemplateResponse(request=request, name="subscription.html", context={"subscription": subscription})

@router.post("/{subscription_id}/subscribe/", response_class=HTMLResponse)
async def subscribe(subscription_id: int, db: AsyncSession = Depends(get_db)):
    subscription = await crud.get_subscription_by_id(db, subscription_id)
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    status = subscription.is_active
    # print('status', status)
    if not status:
        await data_manager.subscribe(subscription.exchange.name, subscription.symbol.name, subscription.type)
        logging.info(f'Subscription for {subscription.exchange.name} {subscription.symbol.name} {subscription.type} was started')
    else:
        await data_manager.unsubscribe(subscription.exchange.name, subscription.symbol.name, subscription.type)
        logging.info(f'Subscription for {subscription.exchange.name} {subscription.symbol.name} {subscription.type} was stopped')

    status = not status
    await crud.update_status(db, subscription, status)
    return RedirectResponse(f"/subscriptions/{subscription_id}/", status_code=303)


