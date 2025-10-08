from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os

from linguist import db_helpers, auth

router = APIRouter(prefix="/linguist", tags=["linguist"])

# Get absolute path to templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Auth routes
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, response: Response, email: str = Form(...), password: str = Form(...)):
    """Handle login"""
    result = await auth.login_user(email, password)

    if result["success"]:
        # Set session cookie
        resp = RedirectResponse(url="/linguist/projects", status_code=303)
        resp.set_cookie(
            key="access_token",
            value=result["session"].access_token,
            httponly=True,
            max_age=result["session"].expires_in,
            samesite="lax"
        )
        return resp
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": result.get("error", "Login failed")
        })

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Show signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup", response_class=HTMLResponse)
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    phone: Optional[str] = Form(None)
):
    """Handle signup"""
    result = await auth.create_user_account(email, password, phone)

    if result["success"]:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": None,
            "success": "Account created! Please log in."
        })
    else:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": result.get("error", "Signup failed")
        })

@router.get("/logout")
async def logout():
    """Logout user"""
    resp = RedirectResponse(url="/linguist/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp

@router.get("/auth/google")
async def google_login():
    """Initiate Google OAuth login"""
    url = await auth.get_google_oauth_url()
    if url:
        return {"url": url}
    else:
        return {"error": "Failed to get Google OAuth URL"}

@router.get("/auth/callback")
async def oauth_callback(code: str = None):
    """Handle OAuth callback"""
    if not code:
        return RedirectResponse(url="/linguist/login?error=no_code", status_code=303)

    result = await auth.handle_oauth_callback(code)

    if result["success"]:
        resp = RedirectResponse(url="/linguist/projects", status_code=303)
        resp.set_cookie(
            key="access_token",
            value=result["session"].access_token,
            httponly=True,
            max_age=result["session"].expires_in,
            samesite="lax"
        )
        return resp
    else:
        return RedirectResponse(
            url=f"/linguist/login?error={result.get('error', 'oauth_failed')}",
            status_code=303
        )

@router.get("/", response_class=HTMLResponse)
async def linguist_home(request: Request):
    """Redirect to projects page"""
    user = await auth.get_current_user(request)
    redirect = auth.redirect_if_not_authenticated(user)
    if redirect:
        return redirect
    return RedirectResponse(url="/linguist/projects")

@router.get("/projects", response_class=HTMLResponse)
async def list_projects(request: Request):
    """List all projects"""
    user = await auth.get_current_user(request)
    redirect = auth.redirect_if_not_authenticated(user)
    if redirect:
        return redirect

    try:
        projects = await db_helpers.get_all_projects()
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": projects,
            "user": user
        })
    except Exception as e:
        print(f"Error in list_projects: {e}")
        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": [],
            "error": str(e),
            "user": user
        })

@router.post("/projects", response_class=HTMLResponse)
async def create_project(
    request: Request,
    title: str = Form(...),
    ui_language: str = Form(...),
    target_language: str = Form(...)
):
    """Create new project and return HTMX partial"""
    user = await auth.get_current_user(request)
    if not user:
        return '<tr><td colspan="5" style="color: red;">Not authenticated</td></tr>'

    try:
        project = await db_helpers.create_project(title, ui_language, target_language, user['id'])
        return f"""
        <tr>
            <td>{project.get('id', 'N/A')}</td>
            <td>{project.get('title', '')}</td>
            <td>{project.get('ui_language', '')}</td>
            <td>{project.get('target_language', '')}</td>
            <td>{project.get('created_at', '')[:10] if project.get('created_at') else 'N/A'}</td>
        </tr>
        """
    except Exception as e:
        print(f"Error creating project: {e}")
        return f'<tr><td colspan="5" style="color: red;">Error: {str(e)}</td></tr>'

@router.get("/campaigns", response_class=HTMLResponse)
async def list_campaigns(request: Request):
    """List all campaigns"""
    user = await auth.get_current_user(request)
    redirect = auth.redirect_if_not_authenticated(user)
    if redirect:
        return redirect

    try:
        campaigns = await db_helpers.get_all_campaigns()
        return templates.TemplateResponse("campaigns.html", {
            "request": request,
            "campaigns": campaigns,
            "user": user
        })
    except Exception as e:
        print(f"Error in list_campaigns: {e}")
        return templates.TemplateResponse("campaigns.html", {
            "request": request,
            "campaigns": [],
            "error": str(e),
            "user": user
        })

@router.get("/questions", response_class=HTMLResponse)
async def list_questions(request: Request):
    """List all questions"""
    user = await auth.get_current_user(request)
    redirect = auth.redirect_if_not_authenticated(user)
    if redirect:
        return redirect

    return templates.TemplateResponse("questions.html", {
        "request": request,
        "questions": [],
        "user": user
    })

@router.get("/responses", response_class=HTMLResponse)
async def list_responses(request: Request):
    """List all responses"""
    user = await auth.get_current_user(request)
    redirect = auth.redirect_if_not_authenticated(user)
    if redirect:
        return redirect

    try:
        responses = await db_helpers.get_all_responses()
        return templates.TemplateResponse("responses.html", {
            "request": request,
            "responses": responses,
            "user": user
        })
    except Exception as e:
        print(f"Error in list_responses: {e}")
        return templates.TemplateResponse("responses.html", {
            "request": request,
            "responses": [],
            "error": str(e),
            "user": user
        })
