"""CCDH Terminology Service: Root of application code"""
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi_redis_cache import FastApiRedisCache
from starlette.responses import RedirectResponse
from tccm_api.db.tccm_graph import TccmGraph

from ccdh.config import get_settings
from ccdh.api.routers import permissible_values, enumerations, models, ccdh_concept_references
# Re-add 'mappings' to 'from ccdh.api.routers import'? Re-add below? - jef 2021/07/29
# from tccm_api.routers import concept_reference


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
    """Route for root of application"""
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup():
    """Start up FastAPI server"""
    app.state.graph = TccmGraph()
    app.state.graph.connect()
    redis_cache = FastApiRedisCache()
    redis_cache.init(host_url=get_settings().redis_url)


@app.on_event("shutdown")
async def shutdown():
    """Shut down FastAPI server"""
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
