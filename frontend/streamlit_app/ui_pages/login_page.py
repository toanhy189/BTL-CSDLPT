"""Trang đăng nhập, lấy token từ API rồi lưu phiên người dùng trong session_state."""

import streamlit as st

from api_client import api_post
from styles import login_mode_css


# Vẽ form đăng nhập, gọi API xác thực và lưu token/user vào session khi thành công.
def render_login_page() -> None:
    """Vẽ form đăng nhập, gọi API xác thực và lưu token/user vào session khi thành công."""
    login_mode_css()

    left, right = st.columns([1.35, 0.85], gap="large")
    with left:
        st.markdown(
            """
            <div class="login-title">Hệ thống đăng ký học phần nhiều cơ sở</div>
            <div class="login-subtitle">Cổng quản lý đào tạo</div>
            <div class="login-features">
                <div class="login-feature">
                    <div class="feature-icon">▣</div>
                    <div>
                        <div class="feature-title">Đồng bộ dữ liệu</div>
                        <div class="feature-sub">Kết nối toàn bộ các cơ sở</div>
                    </div>
                </div>
                <div class="login-feature">
                    <div class="feature-icon">▤</div>
                    <div>
                        <div class="feature-title">Đăng ký linh hoạt</div>
                        <div class="feature-sub">Dễ dàng, nhanh chóng</div>
                    </div>
                </div>
                <div class="login-feature">
                    <div class="feature-icon">▥</div>
                    <div>
                        <div class="feature-title">Quản lý hiệu quả</div>
                        <div class="feature-sub">Minh bạch, chính xác</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="login-form-panel"></div>
            <div class="login-card-title">Đăng nhập hệ thống</div>
            <div class="login-card-sub">Vui lòng đăng nhập để tiếp tục sử dụng hệ thống</div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
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
            <div class="login-secondary">Xem thông báo</div>
            <div class="forgot-link">Quên mật khẩu?</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="login-footer-text">
            Hệ thống đăng ký học phần nhiều cơ sở
            <span class="login-footer-sub">Cổng quản lý đào tạo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
