@echo off
echo --- BAT DAU TAO BANG TREN 5 SERVER ---

echo.
echo [1/5] Dang chay tren server Hoa Lac (postgres_hoalac)...
type sql\01_create_tables.sql | docker exec -i postgres_hoalac psql -U postgres -d site_hoalac
type sql\08_create_triggers.sql | docker exec -i postgres_hoalac psql -U postgres -d site_hoalac

echo.
echo [2/5] Dang chay tren server Ngoc Truc (postgres_ngoctruc)...
type sql\01_create_tables.sql | docker exec -i postgres_ngoctruc psql -U postgres -d site_ngoctruc
type sql\08_create_triggers.sql | docker exec -i postgres_ngoctruc psql -U postgres -d site_ngoctruc

echo.
echo [3/5] Dang chay tren server Ha Dong (postgres_hadong)...
type sql\01_create_tables.sql | docker exec -i postgres_hadong psql -U postgres -d site_hadong
type sql\08_create_triggers.sql | docker exec -i postgres_hadong psql -U postgres -d site_hadong

echo.
echo [4/5] Dang chay tren server Cau Giay (postgres_caugiay)...
type sql\01_create_tables.sql | docker exec -i postgres_caugiay psql -U postgres -d site_caugiay
type sql\08_create_triggers.sql | docker exec -i postgres_caugiay psql -U postgres -d site_caugiay

echo.
echo [5/5] Dang chay tren server HCM (postgres_hcm)...
type sql\01_create_tables.sql | docker exec -i postgres_hcm psql -U postgres -d site_hcm
type sql\08_create_triggers.sql | docker exec -i postgres_hcm psql -U postgres -d site_hcm

echo.
echo --- HOAN THANH ---
pause
