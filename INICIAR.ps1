Set-Location $PSScriptRoot
if (Test-Path '.\venv\Scripts\python.exe') {
    & '.\venv\Scripts\python.exe' manage.py runserver 127.0.0.1:8001
} else {
    python manage.py runserver 127.0.0.1:8001
}
