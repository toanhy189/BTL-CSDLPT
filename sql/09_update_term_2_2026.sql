-- Cập nhật dữ liệu lớp học phần hiện có sang học kỳ 2, năm học 2026.
-- Các bảng bị ảnh hưởng:
--   1. LopHocPhan: lưu học kỳ và năm học của lớp học phần.
--   2. LichHoc: ngày học phải khớp với tuần/thứ của học kỳ mới.
-- Bảng DangKy không lưu học kỳ/năm học, nên không cần cập nhật.

BEGIN;

UPDATE LopHocPhan
SET semester = 2,
    school_year = 2026;

-- Quy ước tuần 1 của học kỳ 2 năm 2026 bắt đầu từ Thứ 2 ngày 20/04/2026.
-- day_of_week trong CSDL: 2 = Thứ 2, ..., 8 = Chủ nhật.
UPDATE LichHoc
SET study_date =
        DATE '2026-04-20'
        + ((COALESCE(week_number, 1) - 1) * 7)
        + (day_of_week - 2);

COMMIT;
