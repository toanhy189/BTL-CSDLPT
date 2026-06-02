"""Trang quản trị quản lý các yêu cầu bị gián đoạn do site mất kết nối."""

import json

import streamlit as st

from api_client import api_get, api_post
from styles import dataframe, page_title, section_title


STATUS_OPTIONS = ["PENDING", "FAILED", "RETRYING", "DONE", "CANCELLED", "ALL"]

STATUS_LABELS = {
    "PENDING": "Chờ xử lý",
    "FAILED": "Thử lại thất bại",
    "RETRYING": "Đang thử lại",
    "DONE": "Đã xử lý",
    "CANCELLED": "Đã hủy",
    "ALL": "Tất cả",
}

ACTION_LABELS = {
    "DANG_KY": "Đăng ký học phần",
    "HUY_DANG_KY": "Hủy đăng ký",
}


def _format_rows(rows):
    formatted = []
    for row in rows:
        payload = row.get("payload") or {}
        formatted.append(
            {
                "Mã yêu cầu": row.get("id"),
                "Site lỗi": row.get("site_code"),
                "Thao tác": ACTION_LABELS.get(row.get("action"), row.get("action")),
                "Mã sinh viên": payload.get("student_id"),
                "Site mở lớp": payload.get("class_site_code"),
                "Mã lớp": payload.get("class_id"),
                "Trạng thái": STATUS_LABELS.get(row.get("status"), row.get("status")),
                "Số lần thử lại": row.get("retry_count"),
                "Thời điểm tạo": row.get("created_at"),
                "Lần thử gần nhất": row.get("retried_at"),
                "Lỗi/ghi chú": row.get("error_message"),
                "Dữ liệu xử lý lại": json.dumps(payload, ensure_ascii=False),
            }
        )
    return formatted


def render_admin_offline_operations(token):
    page_title(
        "Yêu cầu chờ xử lý",
        "Lưu các yêu cầu đăng ký hoặc hủy đăng ký bị gián đoạn do site mất kết nối.",
    )

    cols = st.columns([0.22, 0.16, 0.2, 0.24, 0.18])
    with cols[0]:
        status = st.selectbox(
            "Trạng thái",
            STATUS_OPTIONS,
            index=0,
            format_func=lambda value: STATUS_LABELS.get(value, value),
        )
    with cols[1]:
        refresh = st.button("Tải lại", use_container_width=True)
    with cols[2]:
        show_payload = st.checkbox("Hiện dữ liệu xử lý lại", value=False)
    with cols[3]:
        retry_all_clicked = st.button("Xử lý tất cả", use_container_width=True)

    if retry_all_clicked:
        result = api_post("/admin/offline-operations/retry-all", token=token)
        if result.get("_error"):
            st.error(result.get("message", "Không thể thử lại các yêu cầu"))
        else:
            st.success(
                "Đã xử lý hàng loạt: "
                f"tổng {result.get('total', 0)}, "
                f"thử lại {result.get('retried', 0)}, "
                f"thành công {result.get('done', 0)}, "
                f"thất bại {result.get('failed', 0)}, "
                f"bỏ qua {result.get('skipped', 0)}."
            )

    params = None if status == "ALL" else {"status": status}
    rows = api_get("/admin/offline-operations", token=token, params=params)
    if isinstance(rows, dict) and rows.get("_error"):
        st.error(rows.get("message", "Không tải được danh sách yêu cầu chờ xử lý"))
        return
    if refresh:
        st.rerun()

    rows = rows or []
    section_title("Danh sách yêu cầu")
    if not rows:
        st.info("Không có yêu cầu nào theo bộ lọc hiện tại.")
        return

    table_rows = _format_rows(rows)
    visible_rows = (
        table_rows
        if show_payload
        else [{k: v for k, v in row.items() if k != "Dữ liệu xử lý lại"} for row in table_rows]
    )
    dataframe(visible_rows, height=360)

    section_title("Xử lý yêu cầu")
    retryable_rows = [row for row in rows if row.get("status") in ("PENDING", "FAILED")]
    if not retryable_rows:
        st.info("Không có yêu cầu nào có thể thử lại.")
        return

    labels = [
        f"#{row['id']} - {ACTION_LABELS.get(row['action'], row['action'])} - "
        f"{row.get('site_code')} - {STATUS_LABELS.get(row.get('status'), row.get('status'))}"
        for row in retryable_rows
    ]
    selected_label = st.selectbox("Chọn yêu cầu", labels)
    selected = retryable_rows[labels.index(selected_label)]

    action_cols = st.columns([0.2, 0.2, 0.6])
    with action_cols[0]:
        retry_clicked = st.button("Thử lại", use_container_width=True)
    with action_cols[1]:
        cancel_clicked = st.button("Hủy yêu cầu", use_container_width=True)

    if retry_clicked:
        result = api_post(f"/admin/offline-operations/{selected['id']}/retry", token=token)
        if result.get("_error") or not result.get("success"):
            st.error(result.get("message", "Thử lại thất bại"))
        else:
            st.success(result.get("message", "Thử lại thành công"))
        st.rerun()

    if cancel_clicked:
        result = api_post(f"/admin/offline-operations/{selected['id']}/cancel", token=token)
        if result.get("_error") or not result.get("success"):
            st.error(result.get("message", "Hủy yêu cầu thất bại"))
        else:
            st.success(result.get("message", "Đã hủy yêu cầu"))
        st.rerun()
