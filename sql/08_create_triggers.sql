-- Trigger dong bo si so lop hoc phan tu bang DangKy.
-- Backend van khoa LopHocPhan bang SELECT ... FOR UPDATE de kiem soat dong thoi.
-- Trigger chi chiu trach nhiem cap nhat number_of_student va chan lop day.

CREATE OR REPLACE FUNCTION fn_dangky_sync_si_so()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.status = 'DA_DANG_KY' THEN
            IF NEW.ID_registration_period IS NULL THEN
                RAISE EXCEPTION 'Dang ky phai gan voi dot dang ky';
            END IF;

            PERFORM 1
            FROM LopHocPhan lhp
            JOIN DotDangKy ddk ON ddk.ID = NEW.ID_registration_period
            WHERE lhp.ID = NEW.ID_class
              AND lhp.semester = ddk.semester
              AND lhp.school_year = ddk.school_year;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Lop hoc phan khong thuoc dot dang ky';
            END IF;

            UPDATE LopHocPhan
            SET number_of_student = number_of_student + 1
            WHERE ID = NEW.ID_class
              AND number_of_student < max_student;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Lop hoc phan da day, khong the dang ky';
            END IF;
        END IF;

        RETURN NEW;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.status IS DISTINCT FROM 'DA_DANG_KY' AND NEW.status = 'DA_DANG_KY' THEN
            IF NEW.ID_registration_period IS NULL THEN
                RAISE EXCEPTION 'Dang ky phai gan voi dot dang ky';
            END IF;

            PERFORM 1
            FROM LopHocPhan lhp
            JOIN DotDangKy ddk ON ddk.ID = NEW.ID_registration_period
            WHERE lhp.ID = NEW.ID_class
              AND lhp.semester = ddk.semester
              AND lhp.school_year = ddk.school_year;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Lop hoc phan khong thuoc dot dang ky';
            END IF;

            UPDATE LopHocPhan
            SET number_of_student = number_of_student + 1
            WHERE ID = NEW.ID_class
              AND number_of_student < max_student;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'Lop hoc phan da day, khong the dang ky';
            END IF;
        ELSIF OLD.status = 'DA_DANG_KY' AND NEW.status IS DISTINCT FROM 'DA_DANG_KY' THEN
            UPDATE LopHocPhan
            SET number_of_student = number_of_student - 1
            WHERE ID = OLD.ID_class
              AND number_of_student > 0;
        END IF;

        RETURN NEW;
    END IF;

    IF TG_OP = 'DELETE' THEN
        IF OLD.status = 'DA_DANG_KY' THEN
            UPDATE LopHocPhan
            SET number_of_student = number_of_student - 1
            WHERE ID = OLD.ID_class
              AND number_of_student > 0;
        END IF;

        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_dangky_sync_si_so_insert ON DangKy;
DROP TRIGGER IF EXISTS trg_dangky_sync_si_so_update ON DangKy;
DROP TRIGGER IF EXISTS trg_dangky_sync_si_so_delete ON DangKy;

CREATE TRIGGER trg_dangky_sync_si_so_insert
BEFORE INSERT ON DangKy
FOR EACH ROW
EXECUTE FUNCTION fn_dangky_sync_si_so();

CREATE TRIGGER trg_dangky_sync_si_so_update
BEFORE UPDATE OF status ON DangKy
FOR EACH ROW
EXECUTE FUNCTION fn_dangky_sync_si_so();

CREATE TRIGGER trg_dangky_sync_si_so_delete
BEFORE DELETE ON DangKy
FOR EACH ROW
EXECUTE FUNCTION fn_dangky_sync_si_so();
