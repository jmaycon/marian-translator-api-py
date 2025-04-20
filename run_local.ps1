# This script is intended for use on Windows with PowerShell.
# It sets up a virtual environment, installs dependencies,
# downloads MarianMT models, and runs the FastAPI server.

$ErrorActionPreference = "Stop"

Write-Host "============================================================="
Write-Host "Checking virtual environment (win-venv)..."
Write-Host "============================================================="

if (!(Test-Path "win-venv")) {
    Write-Host "Creating virtual environment (win-venv)..."
    python -m venv win-venv
} else {
    Write-Host "Virtual environment already exists. Skipping creation."
}

Write-Host "============================================================="
Write-Host "Activating virtual environment..."
Write-Host "============================================================="
. .\win-venv\Scripts\Activate.ps1

Write-Host "============================================================="
Write-Host "Upgrading pip..."
Write-Host "============================================================="
python -m pip install --upgrade pip

Write-Host "============================================================="
Write-Host "Installing dependencies from requirements.txt..."
Write-Host "============================================================="
pip install -r requirements.txt

Write-Host "============================================================="
Write-Host "Downloading MarianMT models..."
Write-Host "============================================================="
python -c "import translation_models; translation_models.install()"

Write-Host "============================================================="
Write-Host "Starting FastAPI server..."
Write-Host "============================================================="
uvicorn translate_api:app --host 0.0.0.0 --port 30012
