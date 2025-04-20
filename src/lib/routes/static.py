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
    content += utils.get_stats()
    file.close()
    return HTMLResponse(utils.generate_html(request=request, title="Nexo System", main_content=content))


@router.get("/style")
async def style(request: Request):
    style = open("src/static/css/main.css", "r")
    content = style.read()
    style.close()
    
    # get userame
    username = sessions_manager.get_current_user(request)
    
    if username:
        try:
            theme_file_name = open("data/users/" + username + "/theme.txt", "r")
            theme_file_name = theme_file_name.read()
            theme = open("src/static/css/custom/theme/" + theme_file_name, "r")
            content += theme.read()
            theme.close()
        except FileNotFoundError:
            content += open("src/static/css/custom/theme/blank.css", "r").read()
        try:
            color_file_name = open("data/users/" + username + "/color.txt", "r")
            color_file_name = color_file_name.read()
            color = open("src/static/css/custom/color/" + color_file_name, "r")
            content += color.read()
            color.close()
        except FileNotFoundError:
            content += open("src/static/css/custom/color/none.css", "r").read()
    else:
        return PlainTextResponse(content, media_type="text/css")
    return PlainTextResponse(content, media_type="text/css")

@router.get("/docs/{path:path}")
async def style(request: Request, path: str):
    file = open("docs/" + path, "rb")
    content = file.read()
    file.close()
    return HTMLResponse(utils.generate_html(request=request, title="Nexo Documentation", main_content=content.decode("utf-8")))

@router.get("/status")
async def status(request: Request):
    main_content = "<style>@keyframes rainbow { 0% { color: #ff0000; } 25% { color: #00ff00; } 50% { color: #0000ff; } 75% { color: #ffff00; } 100% { color: #ff00ff; } }</style>"
    main_content += "<img src=\"https://avatars.githubusercontent.com/u/60709927?v=4\" alt=\"IMAGE\" style=\"width: 100px; height: 100px;\"><br>"
    main_content += "<b style=\"animation: rainbow 5s infinite;\">Server status</b><br>"
    main_content += "<b>Server time:</b> " + str(datetime.datetime.now()) + "<br>"
    main_content += "<b>Server uptime:</b> " + str(datetime.timedelta(seconds=int(time.time() - os.path.getmtime("src/main.py")))) + "<br>"
    main_content += "<b>Server version:</b> 0.1<br>"
    main_content += "<b>Server name:</b> NEXO SYSTEM<br>"
    main_content += str(sys.modules.keys())
    return HTMLResponse(utils.generate_html(request=request, main_content=main_content))
