from datetime import datetime
import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from pydantic import BaseModel
import html
from app.common import loghandle as logger

user_router = APIRouter(
    tags=['gist-user-ops'],
    responses={404: {'description': 'Not Found'}}
)


class RateLimitBreach(Exception):
    pass


class ForbiddenRequestError(Exception):
    pass


class Github404(Exception):
    pass


# Declare response model schema which is based on GitHub schema for pagination to work
class GistsOut(BaseModel):
    url: str
    forks_url: str
    commits_url: str
    id: str
    node_id: str
    git_pull_url: str
    git_push_url: str
    html_url: str
    files: dict
    public: bool
    created_at: datetime
    updated_at: datetime
    description: str | None
    comments: int
    user: None
    comments_url: str
    owner: dict
    truncated: bool
    

def call_github(url, response_list) -> list:
    """
    Function to capture paginated results coming from GitHub API
    The function will call itself recursively till the last page
    :param url: str, the URL for endpoint queried
    :param response_list: list, list of responses received from API
    """
    try:
        headers = {'Accept': 'application/vnd.github+json',
                    'X-GitHub-Api-Version': '2022-11-28'}
        response = requests.get(url=url, headers=headers)

        # raise if response statuscode is not one of success status codes
        response.raise_for_status()

        # appending new entries to existing list
        response_list.extend(response.json())

        # Check for links header in response
        # if link header is not empty recursive function calls will be made
        if response.links:
            if 'next' in response.links:
                call_github(response.links['next']['url'], response_list)
        return response_list
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            # Checking for rate limiting from GitHub to inform user about the cooldown period
            if 'rate limit' in str(e.response.text).lower():
                raise RateLimitBreach('Rate Limit for GitHub API has been exceeded please try after 1 hour')
            else:
                raise ForbiddenRequestError('Operation not allowed in GitHub')
        elif e.response.status_code == 404:
            raise Github404('User/Resource not found or permissions are missing')
    except Exception as e:
        raise e


@user_router.get('/{username}', name='Get publicly available gists for given user',
                 response_model=Page[GistsOut])
# @cache
def get_public_gist(username: str):
    """
    FastAPI router function to get public gists for queried user
    """

    # Initiating an empty list to store gist entries
    response_list = []
    try:
        # Sanitize input user and validate username
        username = html.escape(username)
        logger.debug(f'Received username {username}')

        # Setting up GitHub api url to fetch user gists
        github_api_url = f'https://api.github.com/users/{username}/gists?per_page=100'
        response = call_github(github_api_url, response_list)

        # Return response in paginated manner
        # Caching is currently not implemented
        logger.info(f'Sending response data')
        logger.info(f'Found {str(len(response))} gists for user {username}')
        return paginate(response)

    # Return 403 status for rate limit applies from GitHub
    except RateLimitBreach as e:
        logger.error(e)
        return JSONResponse(content={'message': str(e)}, status_code=403)

    # Return 403 status for operations not allowed
    except ForbiddenRequestError as e:
        logger.error(e)
        return JSONResponse(content={'message': str(e)}, status_code=403)

    # Return 404 if user/link is not found
    except Github404 as e:
        logger.error(e)
        return JSONResponse(content={'message': str(e)}, status_code=404)

    # Return 503 if there was an error connecting to the remote server
    # This will encapsulate most of the generic connection errors like MaxRetriesExceed etc.
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        return JSONResponse(content={'message': str(e)}, status_code=503)

    # Return 504 if request was timed out while connecting to the remote server
    except requests.exceptions.Timeout as e:
        logger.error(e)
        return JSONResponse(content={'message': str(e)}, status_code=504)
