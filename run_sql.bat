@echo off
echo --- BAT DAU TAO BANG TREN 5 SERVER ---

echo.
echo [0/5] Don subscription replication cu neu co...
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_hoalac psql -v ON_ERROR_STOP=1 -U postgres -d site_hoalac
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_ngoctruc psql -v ON_ERROR_STOP=1 -U postgres -d site_ngoctruc
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_caugiay psql -v ON_ERROR_STOP=1 -U postgres -d site_caugiay
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_hcm psql -v ON_ERROR_STOP=1 -U postgres -d site_hcm
if errorlevel 1 goto :error

echo.
echo [1/5] Dang chay tren server Hoa Lac (postgres_hoalac)...
type sql\01_create_tables.sql | docker exec -i postgres_hoalac psql -v ON_ERROR_STOP=1 -U postgres -d site_hoalac
if errorlevel 1 goto :error
type sql\08_create_triggers.sql | docker exec -i postgres_hoalac psql -v ON_ERROR_STOP=1 -U postgres -d site_hoalac
if errorlevel 1 goto :error

echo.
echo [2/5] Dang chay tren server Ngoc Truc (postgres_ngoctruc)...
type sql\01_create_tables.sql | docker exec -i postgres_ngoctruc psql -v ON_ERROR_STOP=1 -U postgres -d site_ngoctruc
if errorlevel 1 goto :error
type sql\08_create_triggers.sql | docker exec -i postgres_ngoctruc psql -v ON_ERROR_STOP=1 -U postgres -d site_ngoctruc
if errorlevel 1 goto :error

echo.
echo [3/5] Dang chay tren server Ha Dong (postgres_hadong)...
type sql\01_create_tables.sql | docker exec -i postgres_hadong psql -v ON_ERROR_STOP=1 -U postgres -d site_hadong
if errorlevel 1 goto :error
type sql\08_create_triggers.sql | docker exec -i postgres_hadong psql -v ON_ERROR_STOP=1 -U postgres -d site_hadong
if errorlevel 1 goto :error

echo.
echo [4/5] Dang chay tren server Cau Giay (postgres_caugiay)...
type sql\01_create_tables.sql | docker exec -i postgres_caugiay psql -v ON_ERROR_STOP=1 -U postgres -d site_caugiay
if errorlevel 1 goto :error
type sql\08_create_triggers.sql | docker exec -i postgres_caugiay psql -v ON_ERROR_STOP=1 -U postgres -d site_caugiay
if errorlevel 1 goto :error

echo.
echo [5/5] Dang chay tren server HCM (postgres_hcm)...
type sql\01_create_tables.sql | docker exec -i postgres_hcm psql -v ON_ERROR_STOP=1 -U postgres -d site_hcm
if errorlevel 1 goto :error
type sql\08_create_triggers.sql | docker exec -i postgres_hcm psql -v ON_ERROR_STOP=1 -U postgres -d site_hcm
if errorlevel 1 goto :error

echo.
echo --- HOAN THANH ---
if /I "%~1" NEQ "nopause" pause
exit /b 0

:error
echo.
echo --- TAO SCHEMA THAT BAI ---
if /I "%~1" NEQ "nopause" pause
exit /b 1
