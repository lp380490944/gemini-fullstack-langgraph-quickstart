# mypy: disable - error - code = "no-untyped-def,misc"
import os
import base64
import pathlib
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

# Define the FastAPI app
app = FastAPI()


class BasicAuthMiddleware(BaseHTTPMiddleware):
    """Protect selected path prefixes with HTTP Basic Auth.

    Enable by setting env vars APP_BASIC_AUTH_USER and APP_BASIC_AUTH_PASS.
    Only requests whose path starts with any of the provided prefixes are challenged.
    """

    def __init__(self, app, username: str, password: str, protect_prefixes: tuple[str, ...]):
        super().__init__(app)
        self._username = username
        self._password = password
        self._protect_prefixes = protect_prefixes

    async def dispatch(self, request, call_next):
        path = request.url.path
        if any(path.startswith(prefix) for prefix in self._protect_prefixes):
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Basic "):
                return StarletteResponse(
                    status_code=401,
                    content="Unauthorized",
                    headers={"WWW-Authenticate": "Basic realm=\"Restricted\""},
                    media_type="text/plain",
                )
            try:
                decoded = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8")
            except Exception:
                return StarletteResponse(
                    status_code=400,
                    content="Invalid Authorization header",
                    media_type="text/plain",
                )
            username, _, password = decoded.partition(":")
            if username != self._username or password != self._password:
                return StarletteResponse(
                    status_code=401,
                    content="Unauthorized",
                    headers={"WWW-Authenticate": "Basic realm=\"Restricted\""},
                    media_type="text/plain",
                )
        return await call_next(request)


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Optionally enable Basic Auth for the frontend static site under /app
_basic_user = os.getenv("APP_BASIC_AUTH_USER")
_basic_pass = os.getenv("APP_BASIC_AUTH_PASS")
if _basic_user and _basic_pass:
    # Protect only the frontend; extend tuple to include "/api" if you also want to guard APIs.
    app.add_middleware(BasicAuthMiddleware, username=_basic_user, password=_basic_pass, protect_prefixes=("/app",))

# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
