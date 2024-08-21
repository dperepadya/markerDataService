from signal import Handlers

from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from crud import get_exchanges
from database import SessionLocal, get_db

router = APIRouter()
handlers = Handlers()
templates = Jinja2Templates(directory="templates")

@router.get("/exchanges/", response_class=HTMLResponse)
async def get_exchanges_list(request: Request, db: SessionLocal = Depends(get_db)):
    exchanges = await get_exchanges(db)
    return templates.TemplateResponse(request=request, name="exchanges.html", context={"exchanges": exchanges})

@router.post("/", response_class=HTMLResponse)
async def index(request: Request):
