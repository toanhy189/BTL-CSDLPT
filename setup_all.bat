@echo off
setlocal

echo --- SETUP TOAN BO DATABASE ---

echo.
echo [1/5] Khoi dong PostgreSQL containers...
docker compose up -d
if errorlevel 1 goto :error

echo.
echo [2/5] Cho PostgreSQL san sang...
call :wait_for_db postgres_hoalac
if errorlevel 1 goto :error
call :wait_for_db postgres_ngoctruc
if errorlevel 1 goto :error
call :wait_for_db postgres_hadong
if errorlevel 1 goto :error
call :wait_for_db postgres_caugiay
if errorlevel 1 goto :error
call :wait_for_db postgres_hcm
if errorlevel 1 goto :error

echo.
echo [3/5] Tao schema va trigger...
call run_sql.bat nopause
if errorlevel 1 goto :error

echo.
echo [4/5] Sinh du lieu mau...
python seed_data.py
if errorlevel 1 goto :error

echo.
echo [5/5] Cau hinh logical replication du lieu dung chung...
call setup_replication.bat nopause
if errorlevel 1 goto :error

echo.
echo --- SETUP HOAN THANH ---
pause
exit /b 0

:wait_for_db
set "container=%~1"
set /a tries=0
:wait_loop
set /a tries+=1
docker exec %container% pg_isready -U postgres >nul 2>nul
if not errorlevel 1 (
    echo   %container% da san sang.
    exit /b 0
)
if %tries% GEQ 30 (
    echo   Loi: %container% chua san sang sau thoi gian cho.
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto :wait_loop

:error
echo.
echo --- SETUP THAT BAI ---
pause
exit /b 1
