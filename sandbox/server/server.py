# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import traceback
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sandbox.database import get_databases
from sandbox.server.online_judge_api import oj_router
from sandbox.server.sandbox_api import sandbox_router
from sandbox.utils.logging import configure_logging

configure_logging()
logger = structlog.stdlib.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    datalake, sqlite = await get_databases()
    logger.info(f'database initialized')
    yield
    await datalake.disconnect()
    await sqlite.disconnect()


app = FastAPI(lifespan=lifespan)
app.mount('/playground',
          StaticFiles(directory=os.path.abspath(os.path.join(__file__, '../../pages')), html=True),
          name='playground')

app = FastAPI(lifespan=lifespan)
app.mount('/SandboxFusion',
          StaticFiles(directory=os.path.abspath(os.path.join(__file__, '../../../docs/build')), html=True),
          name='doc-site')


@app.get("/")
async def root():
    return RedirectResponse(url="./SandboxFusion", status_code=302)


@app.exception_handler(Exception)
async def base_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'detail': str(exc), 'traceback': traceback.format_exc().split('\n')})


app.include_router(sandbox_router, tags=['sandbox'])
app.include_router(oj_router, tags=['datasets'])


@app.get("/v1/ping")
async def index():
    return "pong"
