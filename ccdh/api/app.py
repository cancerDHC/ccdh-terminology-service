from fastapi import FastAPI

from ccdh.api.routers import data_element_concepts, data_elements, mappings, value_meanings

app = FastAPI(title='CCDH Tereminology Harmonization API')

app.include_router(data_element_concepts.router)
app.include_router(data_elements.router)
app.include_router(value_meanings.router)
app.include_router(mappings.router)
