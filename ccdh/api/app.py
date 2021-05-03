from fastapi import FastAPI
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from ccdh.api.routers import data_element_concepts, data_elements, mappings, value_meanings, permissible_values

app = FastAPI(title='CCDH Tereminology Harmonization API')

app.include_router(data_element_concepts.router)
app.include_router(data_elements.router)
app.include_router(permissible_values.router)
app.include_router(value_meanings.router)
app.include_router(mappings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")
