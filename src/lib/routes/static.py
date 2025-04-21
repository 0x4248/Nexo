from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File, Form, Response, APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
import time
import datetime
import os
import sys

from lib import utils
from lib import sessions_manager


router = APIRouter()

@router.get("/")
async def root(request: Request):
    file = open("src/static/index.html", "r")
    content = file.read()
    # content += utils.get_stats()
    file.close()
    return HTMLResponse(utils.generate_html(request=request, title="Nexo System", main_content=content))


@router.get("/style")
async def style(request: Request):
    color = open("src/static/css/custom/color/catppuccin-mocha.css", "r").read()
    style = open("src/static/css/main.css", "r").read()
    content = style + "\n" + color
    return PlainTextResponse(content, media_type="text/css")

@router.get("/docs/{path:path}")
async def style(request: Request, path: str):
    file = open("docs/" + path, "rb")
    content = file.read()
    file.close()
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Documentation", main_content=content.decode("utf-8")))

@router.get("/status")
async def status(request: Request):
    main_content = "ok"
    return HTMLResponse(utils.generate_html(request=request, main_content=main_content))
