$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path $bundledPython) {
        & $bundledPython -m venv .venv
    } else {
        python -m venv .venv
    }
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 first, then run this script again.' }
    & ./.venv/Scripts/python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
if (!(Test-Path 'data/bank.db')) {
    & ./.venv/Scripts/python.exe -m bankwise.data
    if ($LASTEXITCODE -ne 0) { throw 'Data preparation failed.' }
}
& ./.venv/Scripts/python.exe -m streamlit run app.py
