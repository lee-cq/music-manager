from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from apis.router import router as task_router

app = FastAPI()
app.include_router(task_router, prefix="/api")

app.mount("/static", StaticFiles(directory="music_manager/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
<html>
<head>
    <meta charset=utf-8>
    <meta name=viewport content="width=device-width,initial-scale=1">
    <title>音乐标签Web版｜Music Tag Web｜</title>
    <link rel="shortcut icon" href=/static/dist/img/favicon_64.ico type=image/x-icon>
    <link href=./static/dist/css/app.css rel=stylesheet>
</head>
<body>
<script>
    window.siteUrl = "/"
    window.APP_CODE = 'dj-flow';
    window.CSRF_COOKIE_NAME = 'django_vue_cli_csrftoken'
</script>
<div id=app></div>
<script type=text/javascript
        src=./static/dist/js/manifest.9ba6c0d4f4490e9a4f28.js></script>
<script type=text/javascript
        src=./static/dist/js/vendor.051dd49be048f27f51f9.js></script>
<script type=text/javascript
        src=./static/dist/js/app.0a49d5b848fb993c489d.js></script>
</body>
</html>"""


@app.get("/user/info")
def user_info():
    return {
        "result": True,
        "message": "success",
        "data": {"username": "admin", "role": "admin"},
    }


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
