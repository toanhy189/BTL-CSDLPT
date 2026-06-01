-- Cap nhat du lieu lop hoc phan hien co sang hoc ky 2, nam hoc 2026.
-- Cac bang bi anh huong:
--   1. LopHocPhan: luu hoc ky va nam hoc cua lop hoc phan.
--   2. LichHoc: ngay hoc phai khop voi tuan/thu cua hoc ky moi.
-- Bang DangKy khong luu hoc ky/nam hoc, nen khong can cap nhat.

BEGIN;

UPDATE LopHocPhan
SET semester = 2,
    school_year = 2026;

-- Quy uoc tuan 1 cua hoc ky 2 nam 2026 bat dau tu Thu 2 ngay 20/04/2026.
-- day_of_week trong CSDL: 2 = Thu 2, ..., 8 = Chu nhat.
UPDATE LichHoc
SET study_date =
        DATE '2026-04-20'
        + ((COALESCE(week_number, 1) - 1) * 7)
        + (day_of_week - 2);

COMMIT;
