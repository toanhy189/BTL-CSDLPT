"""Trang Streamlit cho nghiệp vụ trang quản lý dữ liệu của quản trị viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, metric_card, page_title, records_count, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu site select trước khi hiển thị hoặc xử lý.
def _site_select(label, key):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu site select trước khi hiển thị hoặc xử lý."""
    return st.selectbox(label, SITE_CODES, key=key, format_func=lambda code: SITE_LABELS.get(code, code))


# Xử lý bước nghiệp vụ result trong module này.
def _result(res):
    """Xử lý bước nghiệp vụ result trong module này."""
    if res.get("_error") or res.get("success") is False:
        st.error(res.get("message", "Thao tác thất bại"))
    else:
        st.success(res.get("message", "Thao tác thành công"))


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu toolbar trước khi hiển thị hoặc xử lý.
def _toolbar(label, key):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu toolbar trước khi hiển thị hoặc xử lý."""
    c1, c2, c3, c4 = st.columns([0.16, 0.12, 0.12, 0.14])
    with c1:
        st.button(f"Thêm {label}", use_container_width=True, key=f"{key}_add")
    with c2:
        st.button("Sửa", use_container_width=True, key=f"{key}_edit")
    with c3:
        st.button("Xóa", use_container_width=True, key=f"{key}_delete")
    with c4:
        st.button("Xuất Excel", use_container_width=True, key=f"{key}_export")


# Vẽ màn hình/khối giao diện admin quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_admin_management(token):
    """Vẽ màn hình/khối giao diện admin quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("Quản lý dữ liệu", "Quản trị dữ liệu cục bộ và dữ liệu dùng chung.")
    tabs = st.tabs(["Sinh viên", "Giảng viên", "Học phần", "Lớp học phần", "Phòng học", "Lịch học"])

    with tabs[0]:
        site = _site_select("Cơ sở đào tạo", "admin_student_site")
        students = api_get("/admin/students", token=token, params={"site_code": site})
        cols = st.columns(3)
        with cols[0]:
            metric_card(f"Tổng sinh viên ({SITE_LABELS.get(site, site)})", records_count(students), icon="◌", accent="red", red_value=True)
        with cols[1]:
            metric_card("Số khoa", "-", icon="▥", accent="blue")
        with cols[2]:
            metric_card("Số lớp hành chính", "-", icon="▤", accent="green")
        _toolbar("sinh viên", "student_toolbar")
        section_title("Danh sách sinh viên")
        html_table(
            students,
            [
                ("id", "Mã SV"),
                ("name_student", "Họ tên"),
                ("date_of_birth", "Ngày sinh"),
                ("formal_class", "Lớp"),
                ("id_department", "Khoa"),
                ("id_headquarter", "Cơ sở"),
                ("phone_student", "SĐT"),
            ],
            limit=10,
        )
        with st.expander("Thêm sinh viên", expanded=False):
            with st.form("add_student"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    sid = st.text_input("Mã sinh viên")
                    name = st.text_input("Họ tên")
                    dob = st.text_input("Ngày sinh", placeholder="YYYY-MM-DD")
                with c2:
                    address = st.text_input("Địa chỉ")
                    formal_class = st.text_input("Lớp")
                    year = st.number_input("Năm nhập học", 2000, 2100, 2024)
                with c3:
                    phone = st.text_input("SĐT")
                    dept = st.text_input("Khoa", value="CNTT")
                    hq = st.text_input("Cơ sở", value=site)
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/students",
                            token=token,
                            json={
                                "site_code": site,
                                "id": sid,
                                "name_student": name,
                                "date_of_birth": dob,
                                "address_student": address,
                                "formal_class": formal_class,
                                "year_of_admission": int(year),
                                "phone_student": phone,
                                "id_department": dept,
                                "id_headquarter": hq,
                            },
                        )
                    )

    with tabs[1]:
        site = _site_select("Cơ sở đào tạo", "admin_teacher_site")
        teachers = api_get("/admin/teachers", token=token, params={"site_code": site})
        metric_card(f"Tổng giảng viên ({SITE_LABELS.get(site, site)})", records_count(teachers), icon="◌", accent="red", red_value=True)
        _toolbar("giảng viên", "teacher_toolbar")
        section_title("Danh sách giảng viên")
        html_table(
            teachers,
            [
                ("id", "Mã GV"),
                ("name_teacher", "Họ tên"),
                ("degree", "Học vị"),
                ("id_department", "Khoa"),
                ("id_headquarter", "Cơ sở"),
                ("phone_teacher", "SĐT"),
            ],
            limit=10,
        )
        with st.expander("Thêm giảng viên", expanded=False):
            with st.form("add_teacher"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    tid = st.text_input("Mã giảng viên")
                    name = st.text_input("Họ tên")
                with c2:
                    address = st.text_input("Địa chỉ")
                    degree = st.text_input("Học vị")
                with c3:
                    phone = st.text_input("SĐT")
                    dept = st.text_input("Khoa", value="CNTT")
                    hq = st.text_input("Cơ sở", value=site)
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/teachers",
                            token=token,
                            json={
                                "site_code": site,
                                "id": tid,
                                "name_teacher": name,
                                "address_teacher": address,
                                "degree": degree,
                                "phone_teacher": phone,
                                "id_department": dept,
                                "id_headquarter": hq,
                            },
                        )
                    )

    with tabs[2]:
        courses = api_get("/admin/courses", token=token)
        metric_card("Tổng học phần dùng chung", records_count(courses), icon="▤", accent="red", red_value=True)
        _toolbar("học phần", "course_toolbar")
        section_title("Danh sách học phần")
        html_table(
            courses,
            [
                ("id", "Mã học phần"),
                ("name_subject", "Tên học phần"),
                ("number_of_credit", "Số tín chỉ"),
                ("id_department", "Khoa"),
            ],
            limit=10,
        )
        with st.expander("Thêm học phần vào cả 5 site", expanded=False):
            with st.form("add_course"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    cid = st.text_input("Mã học phần")
                with c2:
                    name = st.text_input("Tên học phần")
                    credits = st.number_input("Số tín chỉ", 1, 10, 3)
                with c3:
                    dept = st.text_input("Khoa", value="CNTT")
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/courses",
                            token=token,
                            json={
                                "id": cid,
                                "name_subject": name,
                                "number_of_credit": int(credits),
                                "id_department": dept,
                            },
                        )
                    )

    with tabs[3]:
        site = _site_select("Cơ sở mở lớp", "admin_class_site")
        classes = api_get("/admin/class-sections", token=token, params={"site_code": site})
        metric_card(f"Tổng lớp học phần ({SITE_LABELS.get(site, site)})", records_count(classes), icon="▤", accent="red", red_value=True)
        _toolbar("lớp học phần", "class_toolbar")
        section_title("Danh sách lớp học phần")
        html_table(
            classes,
            [
                ("id", "Mã lớp"),
                ("name_subject", "Học phần"),
                ("name_teacher", "Giảng viên"),
                ("semester", "Học kỳ"),
                ("school_year", "Năm học"),
                ("number_of_student", "Sĩ số"),
                ("max_student", "Tối đa"),
                ("id_rooms", "Phòng"),
            ],
            limit=10,
        )
        with st.expander("Thêm lớp học phần", expanded=False):
            with st.form("add_class"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    class_id = st.text_input("Mã lớp")
                    semester = st.number_input("Học kỳ", 1, 3, 1)
                    year = st.number_input("Năm học", 2000, 2100, 2024)
                with c2:
                    max_student = st.number_input("Sĩ số tối đa", 1, 300, 50)
                    shift = st.number_input("Ca học", 1, 10, 1)
                    hq = st.text_input("Cơ sở", value=site)
                with c3:
                    subject = st.text_input("Mã học phần")
                    teacher = st.text_input("Mã giảng viên")
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/class-sections",
                            token=token,
                            json={
                                "site_code": site,
                                "id": class_id,
                                "semester": int(semester),
                                "school_year": int(year),
                                "number_of_student": 0,
                                "max_student": int(max_student),
                                "shift": int(shift),
                                "id_subject": subject,
                                "id_teacher": teacher,
                                "id_headquarter": hq,
                            },
                        )
                    )

    with tabs[4]:
        site = _site_select("Cơ sở", "admin_room_site")
        rooms = api_get("/admin/rooms", token=token, params={"site_code": site})
        metric_card(f"Tổng phòng học ({SITE_LABELS.get(site, site)})", records_count(rooms), icon="▥", accent="red", red_value=True)
        _toolbar("phòng học", "room_toolbar")
        section_title("Danh sách phòng học")
        html_table(
            rooms,
            [
                ("id", "Mã phòng"),
                ("name_room", "Tên phòng"),
                ("capacity", "Sức chứa"),
                ("id_headquarter", "Cơ sở"),
            ],
            limit=10,
        )
        with st.expander("Thêm phòng học", expanded=False):
            with st.form("add_room"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    rid = st.text_input("Mã phòng")
                with c2:
                    name = st.text_input("Tên phòng")
                    capacity = st.number_input("Sức chứa", 1, 500, 50)
                with c3:
                    hq = st.text_input("Cơ sở", value=site)
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/rooms",
                            token=token,
                            json={
                                "site_code": site,
                                "id": rid,
                                "name_room": name,
                                "capacity": int(capacity),
                                "id_headquarter": hq,
                            },
                        )
                    )

    with tabs[5]:
        site = _site_select("Cơ sở", "admin_schedule_site")
        schedules = api_get("/admin/schedules", token=token, params={"site_code": site})
        metric_card(f"Tổng lịch học ({SITE_LABELS.get(site, site)})", records_count(schedules), icon="▦", accent="red", red_value=True)
        _toolbar("lịch học", "schedule_toolbar")
        section_title("Danh sách lịch học")
        html_table(
            schedules,
            [
                ("id", "Mã lịch"),
                ("id_class", "Mã lớp"),
                ("name_subject", "Học phần"),
                ("day_of_week", "Thứ"),
                ("start_period", "Tiết bắt đầu"),
                ("end_period", "Tiết kết thúc"),
                ("id_room", "Phòng"),
            ],
            limit=10,
        )
        with st.expander("Thêm lịch học", expanded=False):
            with st.form("add_schedule"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    schedule_id = st.text_input("Mã lịch")
                    class_id = st.text_input("Mã lớp")
                with c2:
                    day = st.number_input("Thứ", 2, 8, 2)
                    start = st.number_input("Tiết bắt đầu", 1, 12, 1)
                    end = st.number_input("Tiết kết thúc", 1, 12, 2)
                with c3:
                    room = st.text_input("Mã phòng")
                if st.form_submit_button("Lưu"):
                    _result(
                        api_post(
                            "/admin/schedules",
                            token=token,
                            json={
                                "site_code": site,
                                "id": schedule_id,
                                "id_class": class_id,
                                "day_of_week": int(day),
                                "start_period": int(start),
                                "end_period": int(end),
                                "id_room": room,
                            },
                        )
                    )
