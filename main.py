from fastapi import (
    FastAPI,
    Request,
    Form,
    status,
    File,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic
from starlette.middleware.sessions import SessionMiddleware
import os
from config import *
from utils.judge import test_code
from testcase import test_cases

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def check_id(id: str):
    return len(id) == size and id.startswith(prefix) and id.isnumeric()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
    request: Request,
    id: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    if password == "admin" and check_id(id) and id in ids:
        request.session["id"] = id
        request.session["role"] = role
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "用户名或密码错误"},
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


@app.get("/home")
async def home(request: Request):
    if not (role := request.session.get("role", None)) or not (
        id := request.session.get("id", None)
    ):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    message = request.session.pop("message", None)
    message_type = request.session.pop("message_type", "info")

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "id": id,
            "role": role,
            "message": message,
            "message_type": message_type,
        },
    )


@app.get("/download/{file}")
async def download(file: str, request: Request):
    if not request.session.get("id"):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    file_name = f"{file}.zip" if file != "instruction" else "instruction.pdf"
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        request.session["message"] = "题目文件不存在"
        request.session["message_type"] = "danger"
        return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

    return FileResponse(file_path, filename=file_name)


@app.post("/upload-file")
async def upload_file(
    request: Request, file: UploadFile = File(...), question: str = Form(...)
):
    if not (id := request.session.get("id")) or not (
        role := request.session.get("role")
    ):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Create user directory if not exists
    user_dir = os.path.join(UPLOAD_DIR, role, id[3:7], id[7:])
    os.makedirs(user_dir, exist_ok=True)

    question += (
        os.path.splitext(file.filename)[1]
        if role == roles[0]
        else ".py" if role == roles[1] else ".c"
    )
    save_path = os.path.join(user_dir, question)

    try:
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
        request.session["message"] = "文件上传成功"
        request.session["message_type"] = "success"
    except Exception as e:
        request.session["message"] = f"文件上传失败: {str(e)}"
        request.session["message_type"] = "danger"

    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/upload-code")
async def upload_code(request: Request, code: str = Form(...)):
    if not (id := request.session.get("id")) or not (
        role := request.session.get("role")
    ):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    # Create user directory if not exists
    user_dir = os.path.join(UPLOAD_DIR, role, id[3:7], id[7:])
    os.makedirs(user_dir, exist_ok=True)

    code_file = os.path.join(user_dir, f"{role}_code.txt")

    try:
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        request.session["message"] = "代码提交成功"
        request.session["message_type"] = "success"
    except Exception as e:
        request.session["message"] = f"代码提交失败: {str(e)}"
        request.session["message_type"] = "danger"

    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/test-code")
async def test_submitted_code(
    request: Request,
    code: str = Form(...),
    question: str = Form(...),
    language: str = Form(...),
):
    if not request.session.get("id"):
        return {"status": "error", "message": "未登录"}

    if question not in test_cases:
        return {"status": "error", "message": "题目不存在"}

    if language not in roles:
        return {"status": "error", "message": "不支持的语言"}

    test_case = test_cases[question]
    results = test_code(code, language, test_case["test_cases"])

    return {"status": "success", "results": results, "question_name": test_case["name"]}


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("id", None)
    request.session.pop("role", None)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
