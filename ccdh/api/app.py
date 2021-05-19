from fastapi import FastAPI
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from tccm_api.db.tccm_graph import TccmGraph

from ccdh.api.routers import harmonized_attributes, node_attributes, mappings, permissible_values, enumerations
from tccm_api.routers import concept_reference

app = FastAPI(title='CCDH Tereminology Harmonization API')

app.include_router(harmonized_attributes.router)
app.include_router(node_attributes.router)
app.include_router(enumerations.router)
app.include_router(permissible_values.router)
app.include_router(mappings.router)
app.include_router(concept_reference.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup():
    app.state.graph = TccmGraph()
    app.state.graph.connect()


@app.on_event("shutdown")
async def shutdown():
    if app.state.graph:
        app.state.graph.disconnect()
