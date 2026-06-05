@echo off
chcp 65001 >nul
title PROWEB HR — Deploy to Hetzner

echo.
echo ╔══════════════════════════════════════════╗
echo ║   PROWEB HR — Hetzner Deploy             ║
echo ╚══════════════════════════════════════════╝
echo.

:: ─── Server IP ni so'rash ─────────────────────────────────────
set /p SERVER_IP="Hetzner server IP manzilini kiriting: "
if "%SERVER_IP%"=="" (
    echo [XATO] IP manzil kiritilmadi!
    pause
    exit /b 1
)

echo.
echo [1/4] Fayllar siqilmoqda...

:: ─── Fayllarni zip qilish (venv va __pycache__ siz) ──────────
set ZIP_NAME=proweb_hr_deploy.zip
if exist %ZIP_NAME% del %ZIP_NAME%

powershell -Command "Compress-Archive -Path '.' -DestinationPath '%ZIP_NAME%' -Force" >nul 2>&1
if not exist %ZIP_NAME% (
    echo [XATO] Zip yaratib bo'lmadi. PowerShell versiyasini tekshiring.
    pause
    exit /b 1
)
echo [OK] %ZIP_NAME% yaratildi

echo.
echo [2/4] Fayllar serverga yuborilimoqda...
echo     Server: %SERVER_IP%
echo     (SSH parolingizni kiriting)
echo.

:: ─── SCP bilan yuklash ────────────────────────────────────────
scp -o StrictHostKeyChecking=no %ZIP_NAME% root@%SERVER_IP%:/opt/proweb_hr_deploy.zip
if %ERRORLEVEL% neq 0 (
    echo [XATO] Fayllar yuborilmadi. SSH ulangan bolishini tekshiring.
    pause
    exit /b 1
)
echo [OK] Fayllar yuborildi

echo.
echo [3/4] Server sozlanmoqda...
echo     (SSH parolingizni yana kiriting)
echo.

:: ─── Serverda barcha narsani sozlash ─────────────────────────
ssh -o StrictHostKeyChecking=no root@%SERVER_IP% "^
    apt-get install -y unzip -qq 2>/dev/null; ^
    mkdir -p /opt/proweb-hr; ^
    cd /opt && unzip -o proweb_hr_deploy.zip -d proweb-hr-tmp 2>/dev/null; ^
    cp -r proweb-hr-tmp/jobhunter_ai/. proweb-hr/ 2>/dev/null || cp -r proweb-hr-tmp/. proweb-hr/ 2>/dev/null; ^
    rm -rf proweb-hr-tmp proweb_hr_deploy.zip; ^
    cd /opt/proweb-hr && chmod +x setup_server.sh; ^
    echo OK - Fayllar joylashtirildi ^
"
if %ERRORLEVEL% neq 0 (
    echo [XATO] Server sozlanmadi.
    pause
    exit /b 1
)
echo [OK] Fayllar server ichiga joylashtirildi

echo.
echo [4/4] Avtomatik setup ishga tushirilmoqda...
echo     (SSH parolingizni kiriting — setup 3-5 daqiqa davom etadi)
echo.

ssh -o StrictHostKeyChecking=no -t root@%SERVER_IP% "bash /opt/proweb-hr/setup_server.sh"

:: ─── Temp fayl tozalash ───────────────────────────────────────
if exist %ZIP_NAME% del %ZIP_NAME%

echo.
echo ╔══════════════════════════════════════════╗
echo ║   DEPLOY TUGADI!                         ║
echo ║   Sayt: http://%SERVER_IP%               ║
echo ╚══════════════════════════════════════════╝
echo.
pause
