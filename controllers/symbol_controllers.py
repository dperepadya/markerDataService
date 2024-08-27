from fastapi import APIRouter, Depends, Request, Form, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

import crud
from cache import symbols_cache
from crud import get_exchanges
from database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")



