# SPDX-License-Identifier: GPL-3.0 
# Nexo
# A textboard with the kitchen sink included
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
import os

INIT = False
if not os.path.exists("data"):
    os.makedirs("data")
    print("INIT")
    INIT = True

from lib import database
from lib import utils
from lib import logger as nexo_logger

import logging
app = FastAPI(title="Nexo", docs_url=None, redoc_url=None, openapi_url=None)

# Dissable Uvicorn's default logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger('uvicorn')
logger.setLevel(logging.CRITICAL)

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
    client_ip = hashlib.sha256((request.client.host).encode()).hexdigest()
    current_time = time.time()
    request_log = rate_limit_data.get(client_ip, {"count": 0, "start_time": current_time})

    if current_time - request_log["start_time"] > TIME_WINDOW:
        request_log = {"count": 0, "start_time": current_time}

    request_log["count"] += 1

    if request_log["count"] > RATE_LIMIT:
        retry_after = int(TIME_WINDOW - (current_time - request_log["start_time"]))

        nexo_logger.log_warning("main.dosprevention", f"Rate limit exceeded for {client_ip}. Count: {request_log['count']}")
        return HTMLResponse(
            utils.generate_html(request=request, main_content=f"<b>SYSTEM:</b> Rate limit exceeded for ip {client_ip}. Please try again later.", footer_content="Error code: 429"),
            status_code=429,
            headers={"Retry-After": str(retry_after)}
        )

    rate_limit_data[client_ip] = request_log

    response = await call_next(request)

    if response.status_code == 200:
        nexo_logger.log("main", f"Request: {request.method} {request.url} - {response.status_code}")
    elif response.status_code == 500:
        nexo_logger.log_error("main", f"INTERNAL SERVER ERROR: {request.method} {request.url} - {response.status_code}")
        return HTMLResponse(
            utils.generate_html(request=request, main_content="Nexo had a internal error. Please try again later or report this error to the developers.", footer_content="Error code: 500"),
            status_code=500
        )
    else:
        nexo_logger.log_warning("main", f"Request: {request.method} {request.url} - {response.status_code}")
    return response
if __name__ == "__main__":
    if INIT:
        database.generate_databases()
        database.User.Core.create_user("nexo_bot", "null", "admin")
        database.User.Core.create_user("nexo", "null", "admin")
        database.Topics.Core.create_topic("/general/", "General", "General discussion", 'False', 'False', 'False')
        database.Topics.Core.create_topic("/admin/", "Admin", "Admin discussion", 'True', 'False', 'False')
        
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")