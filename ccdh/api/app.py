from fastapi import FastAPI
import uvicorn

from ccdh.api.routers import harmonization

app = FastAPI()

app.include_router(harmonization.router)


@app.get('/')
async def root():
    return {'message': 'Hello Harmonization!'}
