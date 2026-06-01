"""Admin concurrency simulation page."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, dataframe, metric_card, page_title, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


def _parse_students(raw_text):
    students = []
    for line in raw_text.splitlines():
        if "," not in line:
            continue
        sid, site = [part.strip() for part in line.split(",", 1)]
        if sid and site:
            students.append({"id_student": sid, "id_student_headquarter": site})
    return students


def render_admin_concurrency(token):
    page_title("Mô phỏng đăng ký đồng thời", "Nhiều sinh viên cùng đăng ký một lớp có số chỗ giới hạn.")

    cols = st.columns([0.22, 0.28, 0.18, 0.16, 0.16])
    with cols[0]:
        class_site = st.selectbox("Site mở lớp", SITE_CODES, format_func=lambda code: SITE_LABELS.get(code, code))
    with cols[1]:
        class_id = st.text_input("Mã lớp học phần", value="LHP-HL-TEST")
    with cols[2]:
        max_student = st.number_input("Số chỗ demo", min_value=1, value=1, step=1)
    with cols[3]:
        st.write("")
        reset_clicked = st.button("Reset lớp test", use_container_width=True)
    with cols[4]:
        st.write("")
        run_clicked = st.button("Chạy mô phỏng", use_container_width=True)

    raw = st.text_area(
        "Danh sách sinh viên tham gia mô phỏng, mỗi dòng theo mẫu MA_SV,SITE",
        value="SV-HL-0001,HL\nSV-HL-0002,HL\nSV-HL-0003,HL\nSV-HL-0004,HL\nSV-HL-0005,HL",
        height=130,
    )
    students = _parse_students(raw)

    if reset_clicked:
        reset_result = api_post(
            "/concurrency/reset-test-class",
            token=token,
            params={"class_site_code": class_site, "class_id": class_id, "max_student": max_student},
        )
        if reset_result.get("_error") or not reset_result.get("success"):
            st.error(reset_result.get("message", "Reset thất bại"))
        else:
            st.success(reset_result.get("message", "Reset thành công"))

    if run_clicked:
        data = api_post(
            "/concurrency/simulate-registration",
            token=token,
            json={"class_site_code": class_site, "class_id": class_id, "students": students},
        )
        rows = data.get("data", []) if not data.get("_error") else []
        success_count = int(data.get("success_count", sum(1 for row in rows if row.get("success"))))
        fail_count = int(data.get("fail_count", len(rows) - success_count))
        metric_cols = st.columns(4)
        with metric_cols[0]:
            metric_card("Tổng request", len(rows), red_value=True)
        with metric_cols[1]:
            metric_card("Thành công", success_count)
        with metric_cols[2]:
            metric_card("Thất bại", fail_count)
        with metric_cols[3]:
            metric_card("Số chỗ tối đa", max_student)
        section_title("Kết quả từng transaction")
        dataframe(rows, height=320)

    section_title("Ghi chú demo")
    st.info("Kết quả dùng để minh họa kiểm soát đồng thời khi nhiều sinh viên cùng đăng ký một lớp học phần.")

    section_title("Log gần nhất")
    logs = api_get("/concurrency/logs", token=token)
    st.code(logs.get("logs", "") if not logs.get("_error") else logs.get("message"))
