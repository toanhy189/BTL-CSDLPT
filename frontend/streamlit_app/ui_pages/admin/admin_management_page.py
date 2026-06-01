"""Admin data management page."""

import streamlit as st

from api_client import api_delete, api_get, api_patch, api_post, api_put
from styles import SITE_LABELS, dataframe, metric_card, page_title, records_count, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


def _site_select(label, key):
    return st.selectbox(label, SITE_CODES, key=key, format_func=lambda code: SITE_LABELS.get(code, code))


def _result(res):
    if res.get("_error") or res.get("success") is False:
        st.error(res.get("message", "Thao tác thất bại"))
    else:
        st.success(res.get("message", "Thao tác thành công"))
        st.rerun()


def _rows(data):
    return data if isinstance(data, list) else []


def _distinct_count(rows, field):
    return len({row.get(field) for row in _rows(rows) if row.get(field)})


def _select_record(rows, label, key):
    rows = _rows(rows)
    if not rows:
        st.info("Chưa có dữ liệu để sửa hoặc xóa.")
        return None
    return st.selectbox(label, rows, key=key, format_func=lambda row: str(row.get("id")))


def _select_training_program(rows, label, key):
    rows = _rows(rows)
    if not rows:
        st.info("Chua co du lieu de sua hoac xoa.")
        return None
    return st.selectbox(
        label,
        rows,
        key=key,
        format_func=lambda row: f"{row.get('id_department')} - {row.get('id_subject')}",
    )


def _delete_button(label, path, token, params=None, key=None):
    confirm = st.checkbox(f"Xác nhận {label.lower()}", key=f"confirm_{key or path}")
    if st.button(label, disabled=not confirm, key=key, use_container_width=True):
        _result(api_delete(path, token=token, params=params))


def render_admin_management(token):
    page_title("Quản lý dữ liệu", "Quản trị dữ liệu cục bộ theo cơ sở và dữ liệu dùng chung toàn trường.")
    tabs = st.tabs([
        "Sinh viên",
        "Giảng viên",
        "Học phần",
        "CT đào tạo",
        "Đợt đăng ký",
        "Lớp học phần",
        "Phòng học",
        "Lịch học",
    ])

    with tabs[0]:
        site = _site_select("Cơ sở đào tạo", "admin_student_site")
        students = api_get("/admin/students", token=token, params={"site_code": site})
        cols = st.columns(3)
        with cols[0]:
            metric_card(f"Tổng sinh viên ({SITE_LABELS.get(site, site)})", records_count(students), red_value=True)
        with cols[1]:
            metric_card("Số khoa", _distinct_count(students, "id_department"))
        with cols[2]:
            metric_card("Số lớp hành chính", _distinct_count(students, "formal_class"))
        section_title("Danh sách sinh viên")
        dataframe(students, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _student_form(token, site, mode="create")
        with update_tab:
            selected = _select_record(students, "Chọn sinh viên", "edit_student")
            if selected:
                _student_form(token, site, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(students, "Chọn sinh viên", "delete_student")
            if selected:
                _delete_button("Xóa sinh viên", f"/admin/students/{selected.get('id')}", token, {"site_code": site}, "delete_student_btn")

    with tabs[1]:
        site = _site_select("Cơ sở đào tạo", "admin_teacher_site")
        teachers = api_get("/admin/teachers", token=token, params={"site_code": site})
        cols = st.columns(2)
        with cols[0]:
            metric_card(f"Tổng giảng viên ({SITE_LABELS.get(site, site)})", records_count(teachers), red_value=True)
        with cols[1]:
            metric_card("Số khoa", _distinct_count(teachers, "id_department"))
        section_title("Danh sách giảng viên")
        dataframe(teachers, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _teacher_form(token, site, mode="create")
        with update_tab:
            selected = _select_record(teachers, "Chọn giảng viên", "edit_teacher")
            if selected:
                _teacher_form(token, site, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(teachers, "Chọn giảng viên", "delete_teacher")
            if selected:
                _delete_button("Xóa giảng viên", f"/admin/teachers/{selected.get('id')}", token, {"site_code": site}, "delete_teacher_btn")

    with tabs[2]:
        courses = api_get("/admin/courses", token=token)
        cols = st.columns(2)
        with cols[0]:
            metric_card("Tổng học phần dùng chung", records_count(courses), red_value=True)
        with cols[1]:
            metric_card("Số khoa phụ trách", _distinct_count(courses, "id_department"))
        section_title("Danh sách học phần")
        dataframe(courses, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _course_form(token, mode="create")
        with update_tab:
            selected = _select_record(courses, "Chọn học phần", "edit_course")
            if selected:
                _course_form(token, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(courses, "Chọn học phần", "delete_course")
            if selected:
                st.warning("Học phần dùng chung được xóa trên cả 5 site. Nếu đang có lớp học phần tham chiếu, database sẽ từ chối.")
                _delete_button("Xóa học phần", f"/admin/courses/{selected.get('id')}", token, key="delete_course_btn")

    with tabs[3]:
        programs = api_get("/admin/training-programs", token=token)
        metric_card("Tổng dòng chương trình đào tạo", records_count(programs), red_value=True)
        section_title("Chương trình đào tạo")
        dataframe(programs, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _training_program_form(token, mode="create")
        with update_tab:
            selected = _select_training_program(programs, "Chọn dòng CTĐT", "edit_training_program")
            if selected:
                _training_program_form(token, mode="update", current=selected)
        with delete_tab:
            selected = _select_training_program(programs, "Chọn dòng CTĐT", "delete_training_program")
            if selected:
                _delete_button(
                    "Xóa dòng CTĐT",
                    f"/admin/training-programs/{selected.get('id_department')}/{selected.get('id_subject')}",
                    token,
                    key="delete_training_program_btn",
                )

    with tabs[4]:
        periods = api_get("/admin/registration-periods", token=token)
        metric_card("Tổng đợt đăng ký", records_count(periods), red_value=True)
        section_title("Đợt đăng ký học phần")
        dataframe(periods, height=520)

        create_tab, update_tab, status_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Mở/Đóng", "Xóa"])
        with create_tab:
            _registration_period_form(token, mode="create")
        with update_tab:
            selected = _select_record(periods, "Chọn đợt đăng ký", "edit_registration_period")
            if selected:
                _registration_period_form(token, mode="update", current=selected)
        with status_tab:
            selected = _select_record(periods, "Chọn đợt đăng ký", "toggle_registration_period")
            if selected:
                is_open = bool(selected.get("is_open"))
                status_label = "đang mở" if is_open else "đang đóng"
                next_label = "Đóng đợt đăng ký" if is_open else "Mở đợt đăng ký"
                st.info(f"Đợt {selected.get('id')} hiện {status_label}.")
                if st.button(next_label, key="toggle_registration_period_btn"):
                    _result(
                        api_patch(
                            f"/admin/registration-periods/{selected.get('id')}/status",
                            token=token,
                            json={"is_open": not is_open},
                        )
                    )
        with delete_tab:
            selected = _select_record(periods, "Chọn đợt đăng ký", "delete_registration_period")
            if selected:
                st.warning("Chỉ xóa đợt đăng ký khi chưa có bản ghi DangKy tham chiếu.")
                _delete_button("Xóa đợt đăng ký", f"/admin/registration-periods/{selected.get('id')}", token, key="delete_registration_period_btn")

    with tabs[5]:
        site = _site_select("Cơ sở mở lớp", "admin_class_site")
        classes = api_get("/admin/class-sections", token=token, params={"site_code": site})
        metric_card(f"Tổng lớp học phần ({SITE_LABELS.get(site, site)})", records_count(classes), red_value=True)
        section_title("Danh sách lớp học phần")
        dataframe(classes, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _class_form(token, site, mode="create")
        with update_tab:
            selected = _select_record(classes, "Chọn lớp học phần", "edit_class")
            if selected:
                _class_form(token, site, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(classes, "Chọn lớp học phần", "delete_class")
            if selected:
                st.warning("Chỉ xóa lớp khi chưa có đăng ký hoặc lịch học liên quan.")
                _delete_button("Xóa lớp học phần", f"/admin/class-sections/{selected.get('id')}", token, {"site_code": site}, "delete_class_btn")

    with tabs[6]:
        site = _site_select("Cơ sở", "admin_room_site")
        rooms = api_get("/admin/rooms", token=token, params={"site_code": site})
        metric_card(f"Tổng phòng học ({SITE_LABELS.get(site, site)})", records_count(rooms), red_value=True)
        section_title("Danh sách phòng học")
        dataframe(rooms, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _room_form(token, site, mode="create")
        with update_tab:
            selected = _select_record(rooms, "Chọn phòng học", "edit_room")
            if selected:
                _room_form(token, site, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(rooms, "Chọn phòng học", "delete_room")
            if selected:
                _delete_button("Xóa phòng học", f"/admin/rooms/{selected.get('id')}", token, {"site_code": site}, "delete_room_btn")

    with tabs[7]:
        site = _site_select("Cơ sở", "admin_schedule_site")
        schedules = api_get("/admin/schedules", token=token, params={"site_code": site})
        metric_card(f"Tổng lịch học ({SITE_LABELS.get(site, site)})", records_count(schedules), red_value=True)
        section_title("Danh sách lịch học")
        dataframe(schedules, height=520)

        create_tab, update_tab, delete_tab = st.tabs(["Thêm", "Sửa", "Xóa"])
        with create_tab:
            _schedule_form(token, site, mode="create")
        with update_tab:
            selected = _select_record(schedules, "Chọn lịch học", "edit_schedule")
            if selected:
                _schedule_form(token, site, mode="update", current=selected)
        with delete_tab:
            selected = _select_record(schedules, "Chọn lịch học", "delete_schedule")
            if selected:
                _delete_button("Xóa lịch học", f"/admin/schedules/{selected.get('id')}", token, {"site_code": site}, "delete_schedule_btn")


def _student_form(token, site, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_student"):
        c1, c2, c3 = st.columns(3)
        with c1:
            sid = st.text_input("Mã sinh viên", value=current.get("id", ""), disabled=mode == "update")
            name = st.text_input("Họ tên", value=current.get("name_student", ""))
            dob = st.text_input("Ngày sinh", value=str(current.get("date_of_birth") or ""), placeholder="YYYY-MM-DD")
        with c2:
            address = st.text_input("Địa chỉ", value=current.get("address_student", ""))
            formal_class = st.text_input("Lớp", value=current.get("formal_class", ""))
            year = st.number_input("Năm nhập học", 2000, 2100, int(current.get("year_of_admission") or 2024))
        with c3:
            phone = st.text_input("SĐT", value=current.get("phone_student", ""))
            dept = st.text_input("Khoa", value=current.get("id_department", "CNTT"))
            hq = st.text_input("Cơ sở", value=current.get("id_headquarter", site))
        if st.form_submit_button("Lưu"):
            payload = {
                "site_code": site,
                "id": sid or current.get("id"),
                "name_student": name,
                "date_of_birth": dob or None,
                "address_student": address,
                "formal_class": formal_class,
                "year_of_admission": int(year),
                "phone_student": phone,
                "id_department": dept,
                "id_headquarter": hq,
            }
            path = "/admin/students" if mode == "create" else f"/admin/students/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))


def _teacher_form(token, site, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_teacher"):
        c1, c2, c3 = st.columns(3)
        with c1:
            tid = st.text_input("Mã giảng viên", value=current.get("id", ""), disabled=mode == "update")
            name = st.text_input("Họ tên", value=current.get("name_teacher", ""))
        with c2:
            address = st.text_input("Địa chỉ", value=current.get("address_teacher", ""))
            degree = st.text_input("Học vị", value=current.get("degree", ""))
        with c3:
            phone = st.text_input("SĐT", value=current.get("phone_teacher", ""))
            dept = st.text_input("Khoa", value=current.get("id_department", "CNTT"))
            hq = st.text_input("Cơ sở", value=current.get("id_headquarter", site))
        if st.form_submit_button("Lưu"):
            payload = {
                "site_code": site,
                "id": tid or current.get("id"),
                "name_teacher": name,
                "address_teacher": address,
                "degree": degree,
                "phone_teacher": phone,
                "id_department": dept,
                "id_headquarter": hq,
            }
            path = "/admin/teachers" if mode == "create" else f"/admin/teachers/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))


def _course_form(token, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_course"):
        c1, c2, c3 = st.columns(3)
        with c1:
            cid = st.text_input("Mã học phần", value=current.get("id", ""), disabled=mode == "update")
        with c2:
            name = st.text_input("Tên học phần", value=current.get("name_subject", ""))
            credits = st.number_input("Số tín chỉ", 1, 10, int(current.get("number_of_credit") or 3))
        with c3:
            dept = st.text_input("Khoa", value=current.get("id_department", "CNTT"))
        if st.form_submit_button("Lưu"):
            payload = {"id": cid or current.get("id"), "name_subject": name, "number_of_credit": int(credits), "id_department": dept}
            path = "/admin/courses" if mode == "create" else f"/admin/courses/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))


def _training_program_form(token, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_training_program"):
        c1, c2, c3 = st.columns(3)
        with c1:
            dept = st.text_input("Khoa/nganh", value=current.get("id_department", "CNTT"), disabled=mode == "update")
        with c2:
            subject = st.text_input("Ma hoc phan", value=current.get("id_subject", ""), disabled=mode == "update")
            semester = st.number_input(
                "Hoc ky goi y",
                1,
                12,
                int(current.get("suggested_semester") or 1),
            )
        with c3:
            required = st.checkbox("Bat buoc", value=bool(current.get("is_required", True)))
        if st.form_submit_button("Luu"):
            payload = {
                "id_department": dept or current.get("id_department"),
                "id_subject": subject or current.get("id_subject"),
                "suggested_semester": int(semester),
                "is_required": required,
            }
            if mode == "create":
                _result(api_post("/admin/training-programs", token=token, json=payload))
            else:
                path = f"/admin/training-programs/{current.get('id_department')}/{current.get('id_subject')}"
                _result(api_put(path, token=token, json=payload))


def _registration_period_form(token, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_registration_period"):
        c1, c2, c3 = st.columns(3)
        with c1:
            period_id = st.text_input("Ma dot", value=current.get("id", ""), disabled=mode == "update")
            semester = st.number_input("Hoc ky", 1, 3, int(current.get("semester") or 2))
            school_year = st.number_input("Nam hoc", 2000, 2100, int(current.get("school_year") or 2026))
        with c2:
            dept = st.text_input("Khoa/nganh", value=current.get("id_department", "CNTT"))
            admission_year_value = current.get("admission_year")
            admission_year = st.number_input(
                "Khoa tuyen sinh",
                2000,
                2100,
                int(admission_year_value or 2024),
            )
            all_years = st.checkbox("Ap dung moi khoa", value=admission_year_value is None)
        with c3:
            start_time = st.text_input(
                "Bat dau",
                value=str(current.get("start_time") or "2026-01-01 00:00:00"),
                placeholder="YYYY-MM-DD HH:MM:SS",
            )
            end_time = st.text_input(
                "Ket thuc",
                value=str(current.get("end_time") or "2026-12-31 23:59:59"),
                placeholder="YYYY-MM-DD HH:MM:SS",
            )
            is_open = st.checkbox("Dang mo", value=bool(current.get("is_open", True)))
        description = st.text_input("Mo ta", value=current.get("description", ""))
        if st.form_submit_button("Luu"):
            payload = {
                "id": period_id or current.get("id"),
                "semester": int(semester),
                "school_year": int(school_year),
                "id_department": dept,
                "admission_year": None if all_years else int(admission_year),
                "start_time": start_time,
                "end_time": end_time,
                "is_open": is_open,
                "description": description or None,
            }
            if mode == "create":
                _result(api_post("/admin/registration-periods", token=token, json=payload))
            else:
                _result(api_put(f"/admin/registration-periods/{current.get('id')}", token=token, json=payload))


def _class_form(token, site, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_class"):
        c1, c2, c3 = st.columns(3)
        with c1:
            class_id = st.text_input("Mã lớp", value=current.get("id", ""), disabled=mode == "update")
            semester = st.number_input("Học kỳ", 1, 3, int(current.get("semester") or 2))
            year = st.number_input("Năm học", 2000, 2100, int(current.get("school_year") or 2026))
        with c2:
            max_student = st.number_input("Sĩ số tối đa", 1, 300, int(current.get("max_student") or 50))
            hq = st.text_input("Cơ sở", value=current.get("id_headquarter", site))
        with c3:
            subject = st.text_input("Mã học phần", value=current.get("id_subject", ""))
            teacher = st.text_input("Mã giảng viên", value=current.get("id_teacher", ""))
        if st.form_submit_button("Lưu"):
            payload = {
                "site_code": site,
                "id": class_id or current.get("id"),
                "semester": int(semester),
                "school_year": int(year),
                "number_of_student": int(current.get("number_of_student") or 0),
                "max_student": int(max_student),
                "id_subject": subject,
                "id_teacher": teacher,
                "id_headquarter": hq,
            }
            path = "/admin/class-sections" if mode == "create" else f"/admin/class-sections/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))


def _room_form(token, site, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_room"):
        c1, c2, c3 = st.columns(3)
        with c1:
            rid = st.text_input("Mã phòng", value=current.get("id", ""), disabled=mode == "update")
        with c2:
            name = st.text_input("Tên phòng", value=current.get("name_room", ""))
            capacity = st.number_input("Sức chứa", 1, 500, int(current.get("capacity") or 50))
        with c3:
            hq = st.text_input("Cơ sở", value=current.get("id_headquarter", site))
        if st.form_submit_button("Lưu"):
            payload = {"site_code": site, "id": rid or current.get("id"), "name_room": name, "capacity": int(capacity), "id_headquarter": hq}
            path = "/admin/rooms" if mode == "create" else f"/admin/rooms/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))


def _schedule_form(token, site, mode, current=None):
    current = current or {}
    with st.form(f"{mode}_schedule"):
        c1, c2, c3 = st.columns(3)
        with c1:
            schedule_id = st.text_input("Mã lịch", value=current.get("id", ""), disabled=mode == "update")
            class_id = st.text_input("Mã lớp", value=current.get("id_class", ""))
        with c2:
            study_date = st.text_input("Ngày học", value=str(current.get("study_date") or ""), placeholder="YYYY-MM-DD")
            week_number = st.number_input("Tuần học", 1, 60, int(current.get("week_number") or 1))
            day = st.number_input("Thứ", 2, 8, int(current.get("day_of_week") or 2))
            start = st.number_input("Tiết bắt đầu", 1, 12, int(current.get("start_period") or 1))
            end = st.number_input("Tiết kết thúc", 1, 12, int(current.get("end_period") or 2))
        with c3:
            start_time = st.text_input("Giờ bắt đầu", value=str(current.get("start_time") or "07:00"))
            end_time = st.text_input("Giờ kết thúc", value=str(current.get("end_time") or "08:50"))
            room = st.text_input("Mã phòng", value=current.get("id_room", ""))
        if st.form_submit_button("Lưu"):
            payload = {
                "site_code": site,
                "id": schedule_id or current.get("id"),
                "id_class": class_id,
                "study_date": study_date,
                "week_number": int(week_number),
                "day_of_week": int(day),
                "start_period": int(start),
                "end_period": int(end),
                "start_time": start_time,
                "end_time": end_time,
                "id_room": room,
            }
            path = "/admin/schedules" if mode == "create" else f"/admin/schedules/{current.get('id')}"
            _result(api_post(path, token=token, json=payload) if mode == "create" else api_put(path, token=token, json=payload))
