@echo off
echo ===================================================
echo               F.R.I.D.A.Y. LAUNCHER (CLOUD MODE)
echo ===================================================
echo.

echo [1/2] Starting F.R.I.D.A.Y. Backend (MCP Server)...
start "MCP Server" cmd /k "uv run friday"
ping 127.0.0.1 -n 4 >nul

echo [2/2] Starting Voice Agent...
start "Voice Agent" cmd /k "uv run friday_voice"

echo.
echo ===================================================
echo ALL SYSTEMS GO!
echo ===================================================
echo.
echo To talk to FRIDAY:
echo 1. Keep this terminal open.
echo 2. Go back to your Brave browser window.
echo 3. Close the "Generated API key" popup (click Close).
echo 4. Click the blue "Start session" button in the Agent Console.
echo.
pause
