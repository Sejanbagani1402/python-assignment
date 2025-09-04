# Lead Form → Zoho CRM (FastAPI)

A simple browser app built with **FastAPI + Jinja2** that captures lead details from a form and creates a **Lead** in **Zoho CRM** using the v2 API. OAuth is handled with a **refresh token**, so the app auto-fetches a fresh access token when needed.

---

## ✨ Features
- Clean HTML form (`/form`) with:
  - **Company** (required)
  - **First Name** (required)
  - **Last Name** (required)
  - Email
  - Mobile
  - **Industry** (dropdown)
  - Description
- Creates a **Lead** in Zoho CRM via `/create-lead`
- **Auto token refresh** using `refresh_token`
- Templated UI with Jinja2: `templates/lead_form.html` and `templates/result.html`
- Modular code:
  - `crm.py` → Zoho CRM API calls
  - `auth.py` → OAuth token refresh
  - `main.py` → FastAPI routes

---

## 🧱 Project Structure

```
app/
├─ main.py
├─ crm.py
├─ auth.py
├─ templates/
│  ├─ lead_form.html
│  └─ result.html
└─ .env
```

> If your `main.py` is at the project root instead of under `app/`, update commands accordingly (e.g., `uvicorn main:app --reload`) and set `Jinja2Templates(directory="templates")` instead of `app/templates`.

---

## ✅ Prerequisites
- Python **3.10+** (tested with 3.12)
- A **Zoho** account with **CRM** access
- A Zoho **OAuth client** (created in [Zoho API Console](https://api-console.zoho.com/))

---

## ⚙️ Setup

### 1) Clone & create a virtual environment
```bash
git clone <your-repo-url>
cd <project-folder>

# Windows (PowerShell)
python -m venv venv
venv\Scriptsctivate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt  # if present
# or
pip install fastapi uvicorn jinja2 python-dotenv httpx requests
```

### 2) Create your Zoho OAuth client
In **Zoho API Console → Self Client / Server-based Client**:

- **Homepage URL**: `http://localhost:8000`
- **Authorized Redirect URI**: `http://localhost:8000/callback`  
  (Exact match; no trailing slash)

**Scopes** (minimum):
```
ZohoCRM.modules.leads.CREATE
ZohoCRM.modules.leads.READ
```
> If your org uses a non-US data center, adjust accounts domain: `.in`, `.eu`, etc.

### 3) Generate a refresh token (one-time)
You need a **refresh token** to let the app auto-refresh access tokens.

**Option A — Use this app’s temporary `/callback` route**  
Add this temporary endpoint to `main.py`:
```python
from fastapi import Request
import httpx, os

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")

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
        r = await client.post(token_url, data=data)
    return r.json()
```
Start the server then open this URL (adjust client_id and region):
```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.leads.CREATE,ZohoCRM.modules.leads.READ&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=http://localhost:8000/callback
```
After login + consent, you’ll be redirected to `/callback` and see JSON with both `access_token` and **`refresh_token`**. Save the `refresh_token`, then you can remove `/callback` from your code.

**Option B — Use cURL (Self-Client grant code)**  
In API Console, generate a **Grant Token** for the scopes above, then exchange it:
```bash
curl -X POST "https://accounts.zoho.com/oauth/v2/token"   -d "grant_type=authorization_code"   -d "client_id=YOUR_CLIENT_ID"   -d "client_secret=YOUR_CLIENT_SECRET"   -d "redirect_uri=http://localhost:8000/callback"   -d "code=GRANT_TOKEN_FROM_CONSOLE"
```
Copy the `refresh_token` from the response.

### 4) Create `.env`
Create an `.env` file in the **app** folder with:
```env
ZOHO_CLIENT_ID=your_client_id_here
ZOHO_CLIENT_SECRET=your_client_secret_here
ZOHO_REDIRECT_URI=http://localhost:8000/callback
ZOHO_REFRESH_TOKEN=your_refresh_token_here

# optional overrides
# ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
# ZOHO_API_DOMAIN=https://www.zohoapis.com
```

### 5) Run the app
If your entrypoint is `app/main.py`:
```bash
uvicorn app.main:app --reload
```
Open: <http://127.0.0.1:8000/form>

---

## 🧩 How it Works

- `auth.py`  
  Refreshes the access token using the long-lived **refresh token** and caches it in memory.
- `crm.py`  
  Builds the payload and calls `POST https://www.zohoapis.com/crm/v2/Leads` with the OAuth header.
- `main.py`  
  - `GET /form` → serves `lead_form.html`
  - `POST /create-lead` → validates inputs, calls `create_lead()`, and renders `result.html`

### Industry dropdown values
```
-None-
ASP (Application Service Provider)
Data/Telecom OEM
ERP (Enterprise Resource Planning)
Government/Military
Large Enterprise
Management ISV
MSP (Management Service Provider)
Network Equipment Enterprise
Non-management ISV
Optical Networking
Service Provider
Small/Medium Enterprise
Storage Equipment
Storage Service Provider
Systems Integrator
Wireless Industry
```

> Zoho standard fields used: `Company`, `First_Name`, `Last_Name`, `Email`, `Phone`, `Industry`, `Description`.

---

## 🧪 Testing
1. Start the app.
2. Open **/form**, fill out the fields, and submit.
3. You should see a **success** page with key details.
4. Verify the new Lead appears in Zoho CRM (Leads module).

---

## 🚑 Troubleshooting

- **`invalid_redirect_uri`**  
  Ensure the redirect URI in **Zoho API Console** matches **exactly** `http://localhost:8000/callback` (no trailing slash).

- **`invalid_code`**  
  Auth codes are single-use and expire quickly. Generate a **new** code and retry. Ensure the **accounts domain** matches your region (`accounts.zoho.com`, `.in`, `.eu`).

- **`INVALID_TOKEN`**  
  Access tokens expire in ~1 hour. Ensure you’re using the **refresh token flow** (this project does). Double-check `.env` values and region.

- **`TemplateNotFound: 'result.html'`**  
  Place `result.html` inside the folder you configured in `Jinja2Templates(directory=...)`.

- **Nothing at `http://localhost:8000/form`**  
  Check your run command matches your layout (e.g., `uvicorn app.main:app --reload`).

---

## 📦 Packaging for Assignment Submission

1. **Create GitHub repo** (private or public).  
2. Add a proper `.gitignore` (Python) to avoid committing:
   - `venv/`
   - `__pycache__/`
   - `.env`
3. Commit your code:
   ```bash
   git add .
   git commit -m "Lead Form → Zoho CRM (FastAPI)"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
4. **README**  
   Ensure this README is at repo root and up-to-date.
5. **Demo evidence** (recommended):
   - Add screenshots or a short screen recording (`/form` submission + Zoho Leads view).
   - Include a sample JSON response (success) in the repo under `docs/`.
6. **Share** the GitHub link as your submission, along with any test credentials or notes your reviewer needs.

---

## 🔐 Security Notes
- **Never commit `.env`** (contains secrets).
- Rotate client secrets if they were ever exposed.
- Limit scopes to what you actually need.

---

## 🙋‍♂️ Maintainer
- **Sejan Bagani** — @Sejanbagani1402
