@echo off
echo --- CAP NHAT LOP HOC PHAN SANG HOC KY 2 NAM 2026 ---

echo.
echo [1/5] Hoa Lac...
type sql\09_update_term_2_2026.sql | docker exec -i postgres_hoalac psql -U postgres -d site_hoalac

echo.
echo [2/5] Ngoc Truc...
type sql\09_update_term_2_2026.sql | docker exec -i postgres_ngoctruc psql -U postgres -d site_ngoctruc

echo.
echo [3/5] Ha Dong...
type sql\09_update_term_2_2026.sql | docker exec -i postgres_hadong psql -U postgres -d site_hadong

echo.
echo [4/5] Cau Giay...
type sql\09_update_term_2_2026.sql | docker exec -i postgres_caugiay psql -U postgres -d site_caugiay

echo.
echo [5/5] HCM...
type sql\09_update_term_2_2026.sql | docker exec -i postgres_hcm psql -U postgres -d site_hcm

echo.
echo --- HOAN THANH ---
pause
