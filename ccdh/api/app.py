from fastapi import FastAPI
import uvicorn

from ccdh.api.routers import data_element_concepts, data_elements, mappings

app = FastAPI(title='CCDH Tereminology Harmonization API')

app.include_router(data_element_concepts.router)
app.include_router(data_elements.router)
app.include_router(mappings.router)


# @app.get('/')
# async def root():
#     return {'message': 'Hello Harmonization!'}
