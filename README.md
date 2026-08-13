# Task Vault

Task Vault is a deliberately vulnerable Django application created for the
Cyber Security Base course project.

The project uses the OWASP Top 10 2017 list.

## Warning

This application intentionally contains security vulnerabilities for
educational purposes. Run it only locally. Do not deploy it to the internet.

## Installation

### Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Open http://127.0.0.1:8000/ in a browser.