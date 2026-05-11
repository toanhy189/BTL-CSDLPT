"""Trang quan ly du lieu co ban."""

import streamlit as st

from db import queries
from pages._helpers import id_options, select_site, selected_id, show_dataframe, show_result


def _pick_id(label, df, id_column="id", label_column=None, key=None):
    options = id_options(df, id_column, label_column)
    if options:
        return selected_id(st.selectbox(label, options, key=key))
    return st.text_input(label, key=key)


def render_headquarter_management():
    st.header("Quản lý cơ sở đào tạo")
    site_code = select_site(key="hq_site")
    df = queries.get_headquarters(site_code)
    show_dataframe(df)

    with st.form("form_add_headquarter"):
        st.subheader("Thêm cơ sở")
        hq_id = st.text_input("Mã cơ sở")
        name = st.text_input("Tên cơ sở")
        address = st.text_input("Địa chỉ")
        submitted = st.form_submit_button("Thêm")
        if submitted:
            show_result(*queries.add_headquarter(site_code, hq_id, name, address))


def render_student_management():
    st.header("Quản lý sinh viên")
    site_code = select_site(key="student_site")
    df = queries.get_students(site_code)
    show_dataframe(df)

    departments = queries.get_departments(site_code)
    with st.form("form_add_student"):
        st.subheader("Thêm sinh viên")
        student_id = st.text_input("Mã sinh viên")
        name = st.text_input("Họ tên")
        date_of_birth = st.text_input("Ngày sinh (YYYY-MM-DD)")
        address = st.text_input("Địa chỉ")
        formal_class = st.text_input("Lớp niên chế")
        year = st.number_input("Năm nhập học", min_value=2000, max_value=2100, value=2024)
        phone = st.text_input("Số điện thoại")
        dept = _pick_id("Khoa", departments, "id", "name_department", key="student_dept")
        hq = st.text_input("Cơ sở", value=site_code)
        submitted = st.form_submit_button("Thêm")
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


def render_teacher_management():
    st.header("Quản lý giảng viên")
    site_code = select_site(key="teacher_site")
    df = queries.get_teachers(site_code)
    show_dataframe(df)

    departments = queries.get_departments(site_code)
    with st.form("form_add_teacher"):
        st.subheader("Thêm giảng viên")
        teacher_id = st.text_input("Mã giảng viên")
        name = st.text_input("Họ tên")
        address = st.text_input("Địa chỉ")
        degree = st.text_input("Học vị")
        phone = st.text_input("Số điện thoại")
        dept = _pick_id("Khoa", departments, "id", "name_department", key="teacher_dept")
        hq = st.text_input("Cơ sở", value=site_code)
        submitted = st.form_submit_button("Thêm")
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


def render_course_management():
    st.header("Quản lý học phần")
    site_code = select_site("Site dùng để xem dữ liệu", key="course_site")
    df = queries.get_courses(site_code)
    show_dataframe(df)

    departments = queries.get_departments(site_code)
    with st.form("form_add_course"):
        st.subheader("Thêm học phần vào cả 5 site")
        course_id = st.text_input("Mã học phần")
        name = st.text_input("Tên học phần")
        credits = st.number_input("Số tín chỉ", min_value=1, max_value=10, value=3)
        dept = _pick_id("Khoa", departments, "id", "name_department", key="course_dept")
        submitted = st.form_submit_button("Thêm vào cả 5 site")
        if submitted:
            data = {
                "id": course_id,
                "name_subject": name,
                "number_of_credit": int(credits),
                "id_department": dept,
            }
            show_result(*queries.add_course_to_all_sites(data))


def render_room_management():
    st.header("Quản lý phòng học")
    site_code = select_site(key="room_site")
    df = queries.get_rooms(site_code)
    show_dataframe(df)

    with st.form("form_add_room"):
        st.subheader("Thêm phòng học")
        room_id = st.text_input("Mã phòng")
        name = st.text_input("Tên phòng")
        capacity = st.number_input("Sức chứa", min_value=1, max_value=500, value=50)
        hq = st.text_input("Cơ sở", value=site_code)
        submitted = st.form_submit_button("Thêm")
        if submitted:
            data = {
                "id": room_id,
                "name_room": name,
                "capacity": int(capacity),
                "id_headquarter": hq,
            }
            show_result(*queries.add_room(site_code, data))


def render_class_section_management():
    st.header("Quản lý lớp học phần")
    site_code = select_site(key="class_site")
    df = queries.get_class_sections(site_code)
    show_dataframe(df)

    subjects = queries.get_subjects(site_code)
    teachers = queries.get_teachers(site_code)
    with st.form("form_add_class"):
        st.subheader("Thêm lớp học phần")
        class_id = st.text_input("Mã lớp học phần")
        semester = st.number_input("Học kỳ", min_value=1, max_value=3, value=1)
        school_year = st.number_input("Năm học", min_value=2000, max_value=2100, value=2024)
        max_student = st.number_input("Sĩ số tối đa", min_value=1, max_value=300, value=50)
        shift = st.number_input("Ca học", min_value=1, max_value=10, value=1)
        subject_id = _pick_id("Học phần", subjects, "id", "name_subject", key="class_subject")
        teacher_id = _pick_id("Giảng viên", teachers, "id", "name_teacher", key="class_teacher")
        hq = st.text_input("Cơ sở mở lớp", value=site_code)
        submitted = st.form_submit_button("Thêm")
        if submitted:
            data = {
                "id": class_id,
                "semester": int(semester),
                "school_year": int(school_year),
                "number_of_student": 0,
                "max_student": int(max_student),
                "shift": int(shift),
                "id_subject": subject_id,
                "id_teacher": teacher_id,
                "id_headquarter": hq,
            }
            show_result(*queries.add_class_section(site_code, data))


def render_schedule_management():
    st.header("Quản lý phòng học và lịch học")
    site_code = select_site(key="schedule_site")
    df = queries.get_schedules(site_code)
    show_dataframe(df)

    classes = queries.get_class_sections(site_code)
    rooms = queries.get_rooms(site_code)
    with st.form("form_add_schedule"):
        st.subheader("Thêm lịch học")
        schedule_id = st.text_input("Mã lịch học")
        class_id = _pick_id("Lớp học phần", classes, "id", "name_subject", key="schedule_class")
        day = st.number_input("Thứ trong tuần", min_value=2, max_value=8, value=2)
        start_period = st.number_input("Tiết bắt đầu", min_value=1, max_value=12, value=1)
        end_period = st.number_input("Tiết kết thúc", min_value=1, max_value=12, value=2)
        room_id = _pick_id("Phòng học", rooms, "id", "name_room", key="schedule_room")
        submitted = st.form_submit_button("Thêm")
        if submitted:
            data = {
                "id": schedule_id,
                "id_class": class_id,
                "day_of_week": int(day),
                "start_period": int(start_period),
                "end_period": int(end_period),
                "id_room": room_id,
            }
            show_result(*queries.add_schedule(site_code, data))


SECTION_RENDERERS = {
    "headquarters": render_headquarter_management,
    "students": render_student_management,
    "teachers": render_teacher_management,
    "courses": render_course_management,
    "rooms_schedules": render_schedule_management,
    "classes": render_class_section_management,
    "rooms": render_room_management,
    "schedules": render_schedule_management,
}


def render_room_schedule_management():
    tab_room, tab_schedule = st.tabs(["Phòng học", "Lịch học"])
    with tab_room:
        render_room_management()
    with tab_schedule:
        render_schedule_management()


SECTION_RENDERERS["rooms_schedules"] = render_room_schedule_management


def render_management_page(section=None):
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
