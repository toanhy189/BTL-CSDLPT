@echo off
setlocal

echo --- BAT DAU CAU HINH LOGICAL REPLICATION DU LIEU DUNG CHUNG ---

echo.
echo [1/5] Xoa subscription cu tren cac site nhan neu co...
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_hoalac psql -v ON_ERROR_STOP=1 -U postgres -d site_hoalac
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_ngoctruc psql -v ON_ERROR_STOP=1 -U postgres -d site_ngoctruc
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_caugiay psql -v ON_ERROR_STOP=1 -U postgres -d site_caugiay
if errorlevel 1 goto :error
type sql\10_drop_common_subscriptions.sql | docker exec -i postgres_hcm psql -v ON_ERROR_STOP=1 -U postgres -d site_hcm
if errorlevel 1 goto :error

echo.
echo [2/5] Tao role replicator va publication tren Ha Dong...
type sql\11_setup_common_replication_publisher.sql | docker exec -i postgres_hadong psql -v ON_ERROR_STOP=1 -U postgres -d site_hadong
if errorlevel 1 goto :error

echo.
echo [3/5] Tao subscription Ha Dong -^> Hoa Lac...
type sql\12_subscribe_common_hd_to_hl.sql | docker exec -i postgres_hoalac psql -v ON_ERROR_STOP=1 -U postgres -d site_hoalac
if errorlevel 1 goto :error

echo.
echo [4/5] Tao subscription Ha Dong -^> Ngoc Truc va Cau Giay...
type sql\13_subscribe_common_hd_to_nt.sql | docker exec -i postgres_ngoctruc psql -v ON_ERROR_STOP=1 -U postgres -d site_ngoctruc
if errorlevel 1 goto :error
type sql\14_subscribe_common_hd_to_cg.sql | docker exec -i postgres_caugiay psql -v ON_ERROR_STOP=1 -U postgres -d site_caugiay
if errorlevel 1 goto :error

echo.
echo [5/5] Tao subscription Ha Dong -^> HCM...
type sql\15_subscribe_common_hd_to_hcm.sql | docker exec -i postgres_hcm psql -v ON_ERROR_STOP=1 -U postgres -d site_hcm
if errorlevel 1 goto :error

echo.
echo --- HOAN THANH CAU HINH REPLICATION ---
if /I "%~1" NEQ "nopause" pause
exit /b 0

:error
echo.
echo --- CAU HINH REPLICATION THAT BAI ---
if /I "%~1" NEQ "nopause" pause
exit /b 1
