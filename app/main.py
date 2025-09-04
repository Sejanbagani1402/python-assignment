from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
import httpx

from crm import create_lead

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")


@app.get("/form", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("lead_form.html", {"request": request})


@app.post("/create-lead", response_class=HTMLResponse)
def create_lead_endpoint(
    request: Request,
    company: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    industry: str = Form(None),
    description: str = Form(None),
):
    lead_data = {
        "Company": company,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Email": email,
        "Phone": phone,
        "Industry": industry,
        "Description": description,
    }

    result = create_lead(lead_data)

    success = "data" in result and result["data"][0]["status"] == "success"

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "success": success,
            "lead_data": lead_data,
            "result": result,
        },
    )


@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No code received"}

    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

    return response.json()
