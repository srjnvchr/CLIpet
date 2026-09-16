# start.ps1 - WezTerm + PowerShell launcher for deskbot-pet.
# Splits a pane above the current one and runs the renderer there,
# using WezTerm's own multiplexer instead of tmux (which doesn't run
# natively on Windows). Run this from inside a WezTerm pane.

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$PetPy = Join-Path $ScriptDir "renderer\pet.py"
$PetPaneLines = 34

if (-not (Test-Path $PetPy)) {
    Write-Error "Can't find $PetPy - run this script from the deskbot-pet folder."
    exit 1
}

$PyCmd = $null
foreach ($candidate in @("python3", "python")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $PyCmd = $candidate
        break
    }
}
if (-not $PyCmd) {
    Write-Error "No 'python3' or 'python' found on PATH."
    exit 1
}

if (-not (Get-Command wezterm -ErrorAction SilentlyContinue)) {
    Write-Error "wezterm.exe not found on PATH. Run this from inside a WezTerm pane, and make sure WezTerm's install folder is on PATH."
    exit 1
}

Write-Host "Using '$PyCmd' for the renderer."
wezterm cli split-pane --top --cells $PetPaneLines -- $PyCmd $PetPy

Write-Host "Pet pane launched above. Run 'claude' here in this pane to start your session."
