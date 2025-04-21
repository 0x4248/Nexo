# SPDX-License-Identifier: GPL-3.0 
# Nexo
# Basic HTTP mailing system
#
# main.py
#
# COPYRIGHT NOTICE
# Copyright (C) 2025 0x4248 and contributors
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the license is not changed.
#
# This software is free and open source. Licensed under the GNU general
# public license version 3.0 as published by the Free Software Foundation.

from fastapi import FastAPI, Request, Header, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse, FileResponse
from typing import Annotated

from asyncio import run
from PIL import Image
import uvicorn
import hashlib
import time
import datetime
import os
import sys
import secrets
from html.parser import HTMLParser

INIT = False
if not os.path.exists("data"):
    os.makedirs("data")
    print("INIT")
    INIT = True

from lib import database

from lib import utils
from lib import sessions_manager
from lib import topics


app = FastAPI()

rate_limit_data = {}
RATE_LIMIT = 20
TIME_WINDOW = 20

from lib.routes import static
from lib.routes import posts
from lib.routes import accounts
from lib.routes import admin

app.include_router(static.router)
app.include_router(posts.router)
app.include_router(accounts.router)
app.include_router(admin.router)

@app.middleware("http")
async def log_request_info(request: Request, call_next):
    # Get client IP (supports reverse proxy if needed)
    client_ip = request.client.host

    current_time = time.time()
    request_log = rate_limit_data.get(client_ip, {"count": 0, "start_time": current_time})

    # Reset if time window expired
    if current_time - request_log["start_time"] > TIME_WINDOW:
        request_log = {"count": 0, "start_time": current_time}

    request_log["count"] += 1

    if request_log["count"] > RATE_LIMIT:
        retry_after = int(TIME_WINDOW - (current_time - request_log["start_time"]))
        return HTMLResponse(
            utils.generate_html(request=request, main_content="<b>SYSTEM:</b> Rate limit exceeded. Please wait " + str(retry_after) + " seconds before retrying."),
            status_code=429,
            headers={"Retry-After": str(retry_after)}
        )

    # Save updated data
    rate_limit_data[client_ip] = request_log

    # Proceed to actual request
    pre_reqtime = current_time
    response = await call_next(request)
    post_reqtime = time.time()
    response.headers["server"] = "NEXO"
    response.headers["NEXO-version"] = "0.1"
    response.headers["compute-time"] = str(post_reqtime - pre_reqtime)
    return response

if __name__ == "__main__":
    if INIT:
        database.generate_databases()
        database.User.Core.create_user("nexo_bot", "null", "admin")
        database.User.Core.create_user("nexo", "null", "admin")
        database.Topics.Core.create_topic("/general/", "General", "General discussion", 'False', 'False', 'False')
        database.Topics.Core.create_topic("/admin/", "Admin", "Admin discussion", 'True', 'False', 'False')
        
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")