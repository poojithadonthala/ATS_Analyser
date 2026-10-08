# HireX ATS — local setup

HireX is a modular ATS screening module with a FastAPI API and React/Vite client. SQLite is used by default; SQLAlchemy models can be moved to PostgreSQL by changing `DB_URL` in `backend/app/database.py` to a PostgreSQL SQLAlchemy URL and installing a PostgreSQL driver.

## Run the API

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:HIREX_SECRET = 'replace-with-a-long-random-secret'
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` for the REST API.

Public signup always creates a student. To provision a recruiter, first register an account, stop the server, then run:

```powershell
python -m app.bootstrap_admin recruiter@example.com
```

Restart the API and sign in with that account. The role comes from the database; there is no role selector in registration or login.

## Run the web client

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` if the API is not at `http://localhost:8000`.

## Notes

Resume parsing supports text-based PDF and DOCX (8 MB maximum). Scanned PDF OCR is not implemented. Screening evidence is extracted from the uploaded file and is stored once per application. The baseline scoring uses explicit skill evidence, job-description lexical overlap, and transparent section/action-verb heuristics; it is not an embedding model or grammar checker. Education and experience comparisons are deliberately advisory and must be reviewed by a recruiter. PDF and DOCX exports are generated from stored analysis. Upload storage is local for development and should be replaced with private object storage in a deployed system. For PostgreSQL deployments, configure TLS, secrets, migrations, CORS, and private file storage before exposure.
