"""Login page."""

import streamlit as st

from api_client import api_post
from styles import login_mode_css


def render_login_page() -> None:
    login_mode_css()

    left, right = st.columns([1.25, 0.85], gap="large")
    with left:
        st.markdown(
            """
            <div class="login-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
            <div class="login-subtitle">Cổng quản lý đào tạo</div>
            <div class="login-feature">
                <div class="feature-title">Đăng ký học phần</div>
                <div class="feature-sub">Tra cứu lớp mở, đăng ký, hủy đăng ký và xem thời khóa biểu.</div>
            </div>
            <div class="login-feature">
                <div class="feature-title">Thời khóa biểu</div>
                <div class="feature-sub">Theo dõi lịch học theo học kỳ, năm học và tuần học.</div>
            </div>
            <div class="login-feature">
                <div class="feature-title">Quản trị đào tạo</div>
                <div class="feature-sub">Quản lý dữ liệu và thống kê toàn trường.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-card-title">Đăng nhập hệ thống</div>
            <div class="login-card-sub">Vui lòng nhập tài khoản để tiếp tục.</div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="admin")
            password = st.text_input("Mật khẩu", type="password", placeholder="admin123")
            submitted = st.form_submit_button("Đăng nhập")
            if submitted:
                data = api_post("/auth/login", json={"username": username, "password": password})
                if data.get("_error"):
                    st.error(data.get("message"))
                    return
                st.session_state["access_token"] = data["access_token"]
                st.session_state["user"] = data["user"]
                st.rerun()
        st.markdown(
            """
            <div class="login-secondary">Tài khoản demo admin: admin / admin123</div>
            """,
            unsafe_allow_html=True,
        )
