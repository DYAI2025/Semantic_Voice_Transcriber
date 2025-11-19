# One-Click Starter for Semantic Voice Transcriber (SVT) - Windows PowerShell
# Right-click and select "Run with PowerShell" to start the GUI

# Change to script directory
Set-Location -Path $PSScriptRoot

Write-Host "Starting Semantic Voice Transcriber (SVT)..." -ForegroundColor Cyan

# Start the GUI
python svt.py

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error starting GUI" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
