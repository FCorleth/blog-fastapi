from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import Json
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/", include_in_schema=False)
def home(req: Request):
    return templates.TemplateResponse(req, "home.html", {"posts": posts, "title": "Home"})

@app.get("/post/{post_id}", include_in_schema=False)
def post_page(req: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                req,
                "post.html",
                {
                    "post": post,
                    "title":title
                }
            )
        
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
    )


@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/post/{post_id}")
def get_post(req: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )
    
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(req: Request, exception: StarletteHTTPException):
    message = ( exception.detail if exception.detail else "An error occurred. Pleash check your request and try again." )
    
    if req.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": exception.status_code,
            "title":exception.status_code ,
            "message": message
        },
        status_code=exception.status_code
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(req: Request, exception: RequestValidationError):
    if req.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()}
        )
    
    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your request and try again."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )
