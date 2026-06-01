"""Trang Streamlit cho nghiệp vụ trang quản lý dữ liệu, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from db import queries
from ui_pages._helpers import (
    id_options,
    metric_card,
    page_title,
    section_title,
    select_site,
    selected_id,
    show_dataframe,
    show_result,
)


# Tạo lựa chọn mã bản ghi từ DataFrame, nếu chưa có dữ liệu thì cho nhập tay.
def _pick_id(label, df, id_column="id", label_column=None, key=None):
    """Tạo lựa chọn mã bản ghi từ DataFrame, nếu chưa có dữ liệu thì cho nhập tay."""
    options = id_options(df, id_column, label_column)
    if options:
        return selected_id(st.selectbox(label, options, key=key))
    return st.text_input(label, key=key)


# Vẽ bộ chọn site và hai metric tóm tắt cho từng màn hình quản lý.
def _site_filter_and_metric(label, site_key, df, metric_label):
    """Vẽ bộ chọn site và hai metric tóm tắt cho từng màn hình quản lý."""
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        site_code = select_site("Chọn cơ sở/site", key=site_key)
    with col2:
        metric_card(metric_label, len(df) if df is not None else 0)
    with col3:
        metric_card("Site", site_code)
    return site_code


# Vẽ màn hình/khối giao diện cơ sở đào tạo quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_headquarter_management():
    """Vẽ màn hình/khối giao diện cơ sở đào tạo quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("🏫 Quản lý cơ sở đào tạo", "Danh mục cơ sở được nhân bản trên các site.")
    site_code = select_site("Chọn site để thao tác", key="hq_site")
    df = queries.get_headquarters(site_code)
    metric_card("Số cơ sở tại site", len(df))

    section_title("Danh sách cơ sở")
    show_dataframe(df, height=360)

    with st.expander("➕ Thêm cơ sở đào tạo", expanded=False):
        with st.form("form_add_headquarter"):
            col1, col2 = st.columns(2)
            with col1:
                hq_id = st.text_input("Mã cơ sở", placeholder="VD: HL")
                name = st.text_input("Tên cơ sở", placeholder="VD: Cơ sở Hòa Lạc")
            with col2:
                address = st.text_input("Địa chỉ", placeholder="Nhập địa chỉ cơ sở")
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                show_result(*queries.add_headquarter(site_code, hq_id, name, address))


# Vẽ màn hình/khối giao diện sinh viên quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_student_management():
    """Vẽ màn hình/khối giao diện sinh viên quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("👨‍🎓 Quản lý sinh viên", "Quản lý sinh viên cục bộ theo từng cơ sở.")
    site_code = select_site("Chọn cơ sở/site", key="student_site")
    df = queries.get_students(site_code)
    metric_card("Số sinh viên tại site", len(df))

    section_title("Danh sách sinh viên")
    show_dataframe(df, height=430)

    departments = queries.get_departments(site_code)
    with st.expander("➕ Thêm sinh viên", expanded=False):
        with st.form("form_add_student"):
            col1, col2, col3 = st.columns(3)
            with col1:
                student_id = st.text_input("Mã sinh viên", placeholder="VD: SV-HL-0101")
                name = st.text_input("Họ tên", placeholder="Nguyễn Văn A")
                date_of_birth = st.text_input("Ngày sinh", placeholder="YYYY-MM-DD")
            with col2:
                address = st.text_input("Địa chỉ", placeholder="Nhập địa chỉ")
                formal_class = st.text_input("Lớp niên chế", placeholder="VD: D21CQCN01")
                year = st.number_input("Năm nhập học", min_value=2000, max_value=2100, value=2024)
            with col3:
                phone = st.text_input("Số điện thoại", placeholder="09xxxxxxxx")
                dept = _pick_id("Khoa", departments, "id", "name_department", key="student_dept")
                hq = st.text_input("Cơ sở", value=site_code)
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": student_id,
                    "name_student": name,
                    "date_of_birth": date_of_birth,
                    "address_student": address,
                    "formal_class": formal_class,
                    "year_of_admission": int(year),
                    "phone_student": phone,
                    "id_department": dept,
                    "id_headquarter": hq,
                }
                show_result(*queries.add_student(site_code, data))


# Vẽ màn hình/khối giao diện giảng viên quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_teacher_management():
    """Vẽ màn hình/khối giao diện giảng viên quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("👨‍🏫 Quản lý giảng viên", "Quản lý giảng viên tại từng cơ sở.")
    site_code = select_site("Chọn cơ sở/site", key="teacher_site")
    df = queries.get_teachers(site_code)
    metric_card("Số giảng viên tại site", len(df))

    section_title("Danh sách giảng viên")
    show_dataframe(df, height=430)

    departments = queries.get_departments(site_code)
    with st.expander("➕ Thêm giảng viên", expanded=False):
        with st.form("form_add_teacher"):
            col1, col2, col3 = st.columns(3)
            with col1:
                teacher_id = st.text_input("Mã giảng viên", placeholder="VD: GV-HL-021")
                name = st.text_input("Họ tên", placeholder="Nhập họ tên")
            with col2:
                address = st.text_input("Địa chỉ", placeholder="Nhập địa chỉ")
                degree = st.text_input("Học vị", placeholder="ThS/TS/PGS/GS")
            with col3:
                phone = st.text_input("Số điện thoại", placeholder="09xxxxxxxx")
                dept = _pick_id("Khoa", departments, "id", "name_department", key="teacher_dept")
                hq = st.text_input("Cơ sở", value=site_code)
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": teacher_id,
                    "name_teacher": name,
                    "address_teacher": address,
                    "degree": degree,
                    "phone_teacher": phone,
                    "id_department": dept,
                    "id_headquarter": hq,
                }
                show_result(*queries.add_teacher(site_code, data))


# Vẽ màn hình/khối giao diện học phần quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_course_management():
    """Vẽ màn hình/khối giao diện học phần quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("📚 Quản lý học phần", "Học phần là dữ liệu dùng chung và được ghi vào cả 5 site.")
    site_code = select_site("Site dùng để xem dữ liệu", key="course_site")
    df = queries.get_courses(site_code)
    metric_card("Số học phần", len(df))

    section_title("Danh sách học phần")
    show_dataframe(df, height=430)

    departments = queries.get_departments(site_code)
    with st.expander("➕ Thêm học phần vào cả 5 site", expanded=False):
        with st.form("form_add_course"):
            col1, col2, col3 = st.columns(3)
            with col1:
                course_id = st.text_input("Mã học phần", placeholder="VD: INT105")
            with col2:
                name = st.text_input("Tên học phần", placeholder="Nhập tên học phần")
                credits = st.number_input("Số tín chỉ", min_value=1, max_value=10, value=3)
            with col3:
                dept = _pick_id("Khoa", departments, "id", "name_department", key="course_dept")
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": course_id,
                    "name_subject": name,
                    "number_of_credit": int(credits),
                    "id_department": dept,
                }
                show_result(*queries.add_course_to_all_sites(data))


# Vẽ màn hình/khối giao diện phòng học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_room_management():
    """Vẽ màn hình/khối giao diện phòng học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("🏢 Quản lý phòng học", "Phòng học là dữ liệu cục bộ theo cơ sở.")
    site_code = select_site("Chọn cơ sở/site", key="room_site")
    df = queries.get_rooms(site_code)
    metric_card("Số phòng tại site", len(df))

    section_title("Danh sách phòng học")
    show_dataframe(df, height=380)

    with st.expander("➕ Thêm phòng học", expanded=False):
        with st.form("form_add_room"):
            col1, col2, col3 = st.columns(3)
            with col1:
                room_id = st.text_input("Mã phòng", placeholder="VD: PH-HL-021")
            with col2:
                name = st.text_input("Tên phòng", placeholder="VD: Phòng HL-21")
                capacity = st.number_input("Sức chứa", min_value=1, max_value=500, value=50)
            with col3:
                hq = st.text_input("Cơ sở", value=site_code)
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": room_id,
                    "name_room": name,
                    "capacity": int(capacity),
                    "id_headquarter": hq,
                }
                show_result(*queries.add_room(site_code, data))


# Vẽ màn hình/khối giao diện lớp học phần quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_class_section_management():
    """Vẽ màn hình/khối giao diện lớp học phần quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("🧾 Quản lý lớp học phần", "Mở lớp học phần tại từng cơ sở.")
    site_code = select_site("Chọn cơ sở/site", key="class_site")
    df = queries.get_class_sections(site_code)
    metric_card("Số lớp tại site", len(df))

    section_title("Danh sách lớp học phần")
    show_dataframe(df, height=430)

    subjects = queries.get_subjects(site_code)
    teachers = queries.get_teachers(site_code)
    with st.expander("➕ Thêm lớp học phần", expanded=False):
        with st.form("form_add_class"):
            col1, col2, col3 = st.columns(3)
            with col1:
                class_id = st.text_input("Mã lớp học phần", placeholder="VD: LHP-HL-031")
                semester = st.number_input("Học kỳ", min_value=1, max_value=3, value=1)
                school_year = st.number_input("Năm học", min_value=2000, max_value=2100, value=2024)
            with col2:
                max_student = st.number_input("Sĩ số tối đa", min_value=1, max_value=300, value=50)
                hq = st.text_input("Cơ sở mở lớp", value=site_code)
            with col3:
                subject_id = _pick_id("Học phần", subjects, "id", "name_subject", key="class_subject")
                teacher_id = _pick_id("Giảng viên", teachers, "id", "name_teacher", key="class_teacher")
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": class_id,
                    "semester": int(semester),
                    "school_year": int(school_year),
                    "number_of_student": 0,
                    "max_student": int(max_student),
                    "id_subject": subject_id,
                    "id_teacher": teacher_id,
                    "id_headquarter": hq,
                }
                show_result(*queries.add_class_section(site_code, data))


# Vẽ màn hình/khối giao diện lịch học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_schedule_management():
    """Vẽ màn hình/khối giao diện lịch học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    page_title("🗓️ Quản lý lịch học", "Một lớp học phần có thể học ở nhiều phòng thông qua bảng LichHoc.")
    site_code = select_site("Chọn cơ sở/site", key="schedule_site")
    df = queries.get_schedules(site_code)
    metric_card("Số lịch học tại site", len(df))

    section_title("Danh sách lịch học")
    show_dataframe(df, height=430)

    classes = queries.get_class_sections(site_code)
    rooms = queries.get_rooms(site_code)
    with st.expander("➕ Thêm lịch học", expanded=False):
        with st.form("form_add_schedule"):
            col1, col2, col3 = st.columns(3)
            with col1:
                schedule_id = st.text_input("Mã lịch học", placeholder="VD: LH-HL-031-1")
                class_id = _pick_id("Lớp học phần", classes, "id", "name_subject", key="schedule_class")
            with col2:
                study_date = st.text_input("Ngay hoc", placeholder="YYYY-MM-DD")
                week_number = st.number_input("Tuan hoc", min_value=1, max_value=60, value=1)
                day = st.number_input("Thứ trong tuần", min_value=2, max_value=8, value=2)
                start_period = st.number_input("Tiết bắt đầu", min_value=1, max_value=12, value=1)
                end_period = st.number_input("Tiết kết thúc", min_value=1, max_value=12, value=2)
            with col3:
                start_time = st.text_input("Gio bat dau", value="07:00")
                end_time = st.text_input("Gio ket thuc", value="08:50")
                room_id = _pick_id("Phòng học", rooms, "id", "name_room", key="schedule_room")
            submitted = st.form_submit_button("Thêm mới")
            if submitted:
                data = {
                    "id": schedule_id,
                    "id_class": class_id,
                    "study_date": study_date,
                    "week_number": int(week_number),
                    "day_of_week": int(day),
                    "start_period": int(start_period),
                    "end_period": int(end_period),
                    "start_time": start_time,
                    "end_time": end_time,
                    "id_room": room_id,
                }
                show_result(*queries.add_schedule(site_code, data))


# Vẽ màn hình/khối giao diện phòng học lịch học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_room_schedule_management():
    """Vẽ màn hình/khối giao diện phòng học lịch học quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    tab_room, tab_schedule = st.tabs(["Phòng học", "Lịch học"])
    with tab_room:
        render_room_management()
    with tab_schedule:
        render_schedule_management()


SECTION_RENDERERS = {
    "headquarters": render_headquarter_management,
    "students": render_student_management,
    "teachers": render_teacher_management,
    "courses": render_course_management,
    "rooms_schedules": render_room_schedule_management,
    "classes": render_class_section_management,
    "rooms": render_room_management,
    "schedules": render_schedule_management,
}


# Vẽ màn hình/khối giao diện trang quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác.
def render_management_page(section=None):
    """Vẽ màn hình/khối giao diện trang quản lý dữ liệu và gọi API hoặc service khi người dùng thao tác."""
    if section:
        SECTION_RENDERERS[section]()
        return

    tabs = st.tabs(
        [
            "Cơ sở đào tạo",
            "Sinh viên",
            "Giảng viên",
            "Học phần",
            "Phòng học",
            "Lớp học phần",
            "Lịch học",
        ]
    )
    with tabs[0]:
        render_headquarter_management()
    with tabs[1]:
        render_student_management()
    with tabs[2]:
        render_teacher_management()
    with tabs[3]:
        render_course_management()
    with tabs[4]:
        render_room_management()
    with tabs[5]:
        render_class_section_management()
    with tabs[6]:
        render_schedule_management()
