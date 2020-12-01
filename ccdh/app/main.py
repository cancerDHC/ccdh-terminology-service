from fastapi import FastAPI
import uvicorn

from ccdh.app.routers import harmonization

app = FastAPI()

app.include_router(harmonization.router)


@app.get('/')
async def root():
    return {'message': 'Hello Harmonization!'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)