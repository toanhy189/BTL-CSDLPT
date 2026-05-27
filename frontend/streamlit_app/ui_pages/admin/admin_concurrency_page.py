"""Trang Streamlit cho nghiệp vụ trang mô phỏng đồng thời của quản trị viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, dataframe, metric_card, page_title, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


# Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu parse sinh viên trước khi hiển thị hoặc xử lý.
def _parse_students(raw_text):
    """Hàm hỗ trợ chuẩn hóa/lọc/chuẩn bị dữ liệu parse sinh viên trước khi hiển thị hoặc xử lý."""
    students = []
    for line in raw_text.splitlines():
        if "," not in line:
            continue
        sid, site = [part.strip() for part in line.split(",", 1)]
        if sid and site:
            students.append({"id_student": sid, "id_student_headquarter": site})
    return students


# Vẽ màn hình/khối giao diện admin concurrency và gọi API hoặc service khi người dùng thao tác.
def render_admin_concurrency(token):
    """Vẽ màn hình/khối giao diện admin concurrency và gọi API hoặc service khi người dùng thao tác."""
    page_title("Mô phỏng đồng thời", "Demo khóa dòng bằng SELECT ... FOR UPDATE.")
    c1, c2, c3 = st.columns(3)
    with c1:
        class_site = st.selectbox("Site mở lớp", SITE_CODES, format_func=lambda code: SITE_LABELS.get(code, code))
    with c2:
        class_id = st.text_input("Mã lớp học phần", value="LHP-HL-TEST")
    with c3:
        max_student = st.number_input("So cho demo", min_value=1, value=1, step=1)

    raw = st.text_area(
        "Danh sách sinh viên: MA_SV,SITE",
        value="SV-HL-0001,HL\nSV-HL-0002,HL\nSV-HL-0003,HL",
        height=120,
    )
    if st.button("Reset lop test"):
        reset_result = api_post(
            "/concurrency/reset-test-class",
            token=token,
            params={"class_site_code": class_site, "class_id": class_id, "max_student": max_student},
        )
        if reset_result.get("_error") or not reset_result.get("success"):
            st.error(reset_result.get("message", "Reset that bai"))
        else:
            st.success(reset_result.get("message", "Reset thanh cong"))

    if st.button("Chạy mô phỏng"):
        data = api_post(
            "/concurrency/simulate-registration",
            token=token,
            json={"class_site_code": class_site, "class_id": class_id, "students": _parse_students(raw)},
        )
        rows = data.get("data", []) if not data.get("_error") else []
        success_count = data.get("success_count", sum(1 for row in rows if row.get("success")))
        fail_count = data.get("fail_count", len(rows) - success_count)
        col1, col2 = st.columns(2)
        with col1:
            metric_card("Thành công", success_count, icon="✓", accent="green")
        with col2:
            metric_card("Thất bại", fail_count, icon="!", accent="red")
        dataframe(rows)
    section_title("Log gần nhất")
    logs = api_get("/concurrency/logs", token=token)
    st.code(logs.get("logs", "") if not logs.get("_error") else logs.get("message"))
