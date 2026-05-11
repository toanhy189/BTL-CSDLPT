# BTL CSDLPT - Đăng Ký Học Phần

Project mô phỏng hệ thống đăng ký học phần nhiều cơ sở, dùng Python, PostgreSQL và Docker Compose.

## 1. Mô Hình PostgreSQL Phân Tán

Project dùng 5 container PostgreSQL riêng, mỗi container là một server/site:

| Site | Container | Database | Port |
| --- | --- | --- | --- |
| Hòa Lạc | `postgres_hoalac` | `site_hoalac` | `5440` |
| Ngọc Trục | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| Hà Đông | `postgres_hadong` | `site_hadong` | `5442` |
| Cầu Giấy | `postgres_caugiay` | `site_caugiay` | `5443` |
| TP.HCM | `postgres_hcm` | `site_hcm` | `5444` |

Thông tin đăng nhập:

```text
Username: postgres
Password: toantk178@
```

## 2. Chạy Docker

Chạy trong thư mục gốc project `BTL-CSDLPT`:

```powershell
docker compose up -d
```

Kiểm tra 5 container:

```powershell
docker compose ps
```

Tắt container nhưng giữ dữ liệu:

```powershell
docker compose down
```

Tắt container và xóa toàn bộ volume dữ liệu:

```powershell
docker compose down -v
```

Khi đổi schema database, ví dụ đổi quan hệ `LopHocPhan 1 - n LichHoc n - 1 PhongHoc`, nên reset dữ liệu cũ rồi tạo lại từ đầu:

```powershell
docker compose down -v
docker compose up -d
.\run_sql.bat
python seed_data.py
python test_queries.py
```

## 3. Tạo Bảng Cho 5 Server

Sau khi Docker đã chạy, chạy file batch:

```powershell
.\run_sql.bat
```

File này sẽ chạy `sql/01_create_tables.sql` trên cả 5 server PostgreSQL.

## 4. Cài Thư Viện Python

```powershell
pip install -r requirements.txt
```

## 5. Bơm Dữ Liệu Mẫu

```powershell
python seed_data.py
```

Script này kết nối 5 database và thêm dữ liệu mẫu phục vụ demo.

## 6. Test Truy Vấn Phân Tán

Chạy:

```powershell
python test_queries.py
```

File `test_queries.py` sẽ gọi các hàm trong `db/distributed_queries.py`:

- `thong_ke_dang_ky_theo_co_so()`
- `hoc_phan_dang_ky_nhieu_nhat()`
- `sinh_vien_dang_ky_cheo_co_so()`
- `ty_le_lap_day_lop_hoc_phan()`
- `thong_ke_so_lop_theo_co_so()`
- `thong_ke_sinh_vien_theo_co_so()`
- `danh_sach_lop_hoc_phan_toan_truong()`

## 7. Chạy Ứng Dụng

Kiểm tra cấu hình Python hiện tại:

```powershell
python app.py
```

Nếu `app.py` đã được phát triển thành giao diện Streamlit, chạy:

```powershell
streamlit run app.py
```

## 8. Kết Nối PgAdmin

Trong pgAdmin, tự register 5 server connection sau:

| Name | Host | Port | Maintenance database |
| --- | --- | --- | --- |
| `site_hoalac` | `localhost` | `5440` | `site_hoalac` |
| `site_ngoctruc` | `localhost` | `5441` | `site_ngoctruc` |
| `site_hadong` | `localhost` | `5442` | `site_hadong` |
| `site_caugiay` | `localhost` | `5443` | `site_caugiay` |
| `site_hcm` | `localhost` | `5444` | `site_hcm` |

Username: `postgres`

Password: `toantk178@`

PgAdmin không tự hiện container Docker, nên phải register thủ công các server này.
