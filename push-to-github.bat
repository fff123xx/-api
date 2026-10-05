@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   TVBox config - push to GitHub
echo   repo: https://github.com/2905273808qq-hue/-api
echo   branch: main
echo ============================================
echo.

if not exist ".git" (
  echo [ERROR] Not a git repo. Please run this file inside tvbox-config folder.
  pause
  exit /b 1
)

echo [1/3] git commit local changes
git add -A
git commit -m "update iptv config" >nul 2>&1
if %errorlevel% equ 0 (
  echo       committed
) else (
  echo       nothing to commit - fine
)
echo.

echo [2/3] GitHub Personal Access Token
echo   Get your token here:
echo     https://github.com/settings/tokens?type=classic
echo   - click "Generate new token ^(classic^)"
echo   - Expiration: No expiration
echo   - check these two boxes:  repo        workflow
echo   - click "Generate token", then copy it
echo.
echo   The token you paste below will NOT be shown on screen.
echo   If GitHub asks for a password, that password IS this token.
echo.

powershell -NoProfile -Command "$s=Read-Host 'Paste token here' -AsSecureString; $t=[Runtime.InteropServices.Marshal]::PtrToStringBSTR([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)); $u='https://2905273808qq-hue:'+$t+'@github.com/2905273808qq-hue/-api.git'; git push $u main"

echo.
echo --------------------------------------------
echo [3/3] pushed. Verify at:
echo   https://github.com/2905273808qq-hue/-api
echo.
echo THEN open GitHub Pages ^(one time only^):
echo   repo  -^>  Settings  -^>  Pages
echo   -^>  "Create with GitHub Actions"  (or Source ^= Deploy from a branch)
echo   -^>  branch:  main        folder:  /root        Save
echo   wait 1-2 min, then check:
echo   https://2905273808qq-hue.github.io/-api/tvbox.json
echo.
echo If that URL does not open in China, use jsDelivr instead:
echo   https://cdn.jsdelivr.net/gh/2905273808qq-hue/-api@main/tvbox.json
echo.
pause
