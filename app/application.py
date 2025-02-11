import fastapi.responses
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi_pagination import add_pagination


def create_app():
    """
    Configurations and setup for FastAPI app
    """

    # Import router
    from app import user_router

    # appi declaration
    appi = FastAPI()

    # Router declarations
    appi.include_router(user_router)

    # customizations and configurations
    # Apply custom openapi configuration to generated swaggerdoc
    custom_openapi_configuration(appi)
    # Apply FastAPI pagination to the responses
    add_pagination(appi)

    # default route for appi index
    @appi.get('/')
    async def index():
        return fastapi.responses.Response('Welcome to gist interface API, Please provide an Username to get gists eg. /octocat')

    return appi


def custom_openapi_configuration(appi):
    """
    Custom configuration for the generation of OpenAPI spec.
    see https://fastapi.tiangolo.com/how-to/extending-openapi/
    """
    if appi.openapi_schema:
        return appi.openapi_schema
    openapi_schema = get_openapi(
        title='gist interface API',
        description='An API that interacts with GitHub gists',
        summary='',
        version='0.0.1',
        routes=appi.routes
    )
    appi.openapi_schema = openapi_schema
    return appi.openapi_schema


APP = create_app()
