"""Trang Streamlit cho nghiệp vụ trang hủy đăng ký của sinh viên, hiển thị dữ liệu và gửi thao tác của người dùng."""

import streamlit as st

from api_client import api_get, api_post
from styles import SITE_LABELS, html_table, page_title, section_title


SITE_CODES = ["HL", "NT", "HD", "CG", "HCM"]


# Vẽ màn hình/khối giao diện sinh viên hủy đăng ký và gọi API hoặc service khi người dùng thao tác.
def render_student_cancel(token, user):
    """Vẽ màn hình/khối giao diện sinh viên hủy đăng ký và gọi API hoặc service khi người dùng thao tác."""
    page_title("Hủy đăng ký", "Chọn lớp học phần cần hủy khỏi danh sách đăng ký.")

    registrations = api_get("/student/registrations", token=token)
    section_title("Danh sách học phần hiện tại")
    html_table(
        registrations,
        [
            ("id_class", "Mã lớp"),
            ("name_subject", "Tên học phần"),
            ("class_headquarter", "Cơ sở mở lớp"),
            ("registration_date", "Ngày đăng ký"),
            ("status", "Trạng thái"),
        ],
        status_columns={"status"},
        limit=8,
    )

    st.divider()
    c1, c2, c3 = st.columns([0.3, 0.45, 0.25])
    with c1:
        site = st.selectbox("Cơ sở mở lớp", SITE_CODES, format_func=lambda code: SITE_LABELS.get(code, code))
    with c2:
        class_id = st.text_input("Mã lớp học phần", placeholder="Nhập mã lớp cần hủy")
    with c3:
        st.write("")
        if st.button("Hủy đăng ký", use_container_width=True):
            res = api_post(
                "/student/cancel",
                token=token,
                json={
                    "student_id": user.get("ref_id"),
                    "class_site_code": site,
                    "class_id": class_id,
                },
            )
            if res.get("success"):
                st.success(res["message"])
            else:
                st.error(res.get("message", res.get("detail", "Hủy đăng ký thất bại")))
