"""Trang Streamlit cho nghiệp vụ trang mô phỏng đồng thời, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from db.queries import get_class_sections
from ui_pages._helpers import (
    id_options,
    metric_card,
    page_title,
    section_title,
    select_site,
    selected_id,
    show_dataframe,
)
from services.log_service import read_log_lines, write_concurrent_result
from services.registration_service import simulate_concurrent_registration


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu parse sinh viên trước khi hiển thị hoặc xử lý.
def _parse_students(raw_text):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu parse sinh viên trước khi hiển thị hoặc xử lý."""
    students = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line or "," not in line:
            continue
        student_id, site_code = [part.strip() for part in line.split(",", 1)]
        if student_id and site_code:
            students.append({"id_student": student_id, "id_student_headquarter": site_code})
    return students


# Vẽ màn hình/khối giao diện trang mô phỏng đồng thời và gọi API hoặc service khi người dùng thao tác.
def render_concurrency_page():
    """Vẽ màn hình/khối giao diện trang mô phỏng đồng thời và gọi API hoặc service khi người dùng thao tác."""
    page_title("⚙️ Mô phỏng đăng ký đồng thời", "Demo transaction và SELECT ... FOR UPDATE.")

    col1, col2 = st.columns([1, 2])
    with col1:
        class_site = select_site("Cơ sở mở lớp", key="concurrency_class_site")
    classes = get_class_sections(class_site)
    options = id_options(classes, "id", "name_subject")
    with col2:
        class_id = selected_id(st.selectbox("Lớp học phần", options)) if options else st.text_input("Mã lớp học phần")

    raw_students = st.text_area(
        "Danh sách sinh viên, mỗi dòng: MA_SV,SITE",
        value="SV-HL-0001,HL\nSV-HL-0002,HL\nSV-HL-0003,HL\nSV-HL-0004,HL\nSV-HL-0005,HL",
        height=130,
    )

    if st.button("Chạy mô phỏng", type="primary"):
        students = _parse_students(raw_students)
        if not class_id or not students:
            st.error("Vui lòng chọn lớp và nhập danh sách sinh viên hợp lệ")
            return
        df = simulate_concurrent_registration(class_site, class_id, students)
        write_concurrent_result(df)
        success_count = int(df["success"].sum()) if not df.empty else 0
        col3, col4 = st.columns(2)
        with col3:
            metric_card("Số thành công", success_count)
        with col4:
            metric_card("Số thất bại", max(len(df) - success_count, 0))
        section_title("Kết quả mô phỏng")
        show_dataframe(df, height=320)

    section_title("Log gần nhất")
    st.code("\n".join(read_log_lines(80)) or "Chưa có log")
