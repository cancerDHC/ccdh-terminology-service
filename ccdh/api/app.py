from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from tccm_api.db.tccm_graph import TccmGraph

from ccdh.api.routers import mappings, permissible_values, enumerations, models, ccdh_concept_references
from tccm_api.routers import concept_reference

app = FastAPI(title='CCDH Terminology Service API')

app.include_router(models.router)
app.include_router(enumerations.router)
app.include_router(permissible_values.router)
app.include_router(ccdh_concept_references.router)

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


def use_route_names_as_operation_ids(fastapi_app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in fastapi_app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


use_route_names_as_operation_ids(app)
