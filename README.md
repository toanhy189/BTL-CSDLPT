# Hệ Thống Đăng Ký Học Phần Nhiều Cơ Sở

Đồ án CSDL phân tán mô phỏng hệ thống đăng ký học phần trên 5 cơ sở đào tạo.

## Công Nghệ

- Python
- Streamlit
- PostgreSQL
- Docker Compose
- psycopg2
- pandas
- pgAdmin

## Kiến Trúc

Hệ thống dùng 5 PostgreSQL server Docker, mỗi server là một site:

| Site | Container | Database | Port |
| --- | --- | --- | --- |
| Hòa Lạc | `postgres_hoalac` | `site_hoalac` | `5440` |
| Ngọc Trục | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| Hà Đông | `postgres_hadong` | `site_hadong` | `5442` |
| Cầu Giấy | `postgres_caugiay` | `site_caugiay` | `5443` |
| TP.HCM | `postgres_hcm` | `site_hcm` | `5444` |

Luồng xử lý:

```text
Streamlit UI -> Python services -> psycopg2 -> 5 PostgreSQL server
```

Truy vấn phân tán đọc dữ liệu từ 5 site rồi tổng hợp bằng pandas.

## Thông Tin Database

```text
Host: localhost
User: postgres
Password: toantk178@
Ports: 5440, 5441, 5442, 5443, 5444
```

Mật khẩu trên đang khớp với `docker-compose.yml` và `db/connections.py` hiện tại.

## Cài Thư Viện

Chạy trong thư mục `BTL-CSDLPT`:

```powershell
pip install -r requirements.txt
```

## Chạy Database

```powershell
docker compose up -d
```

Kiểm tra container:

```powershell
docker ps
docker compose ps
```

## Tạo Bảng Và Import Dữ Liệu

Cách nhanh cho project hiện tại:

```powershell
.\run_sql.bat
python seed_data.py
```

`run_sql.bat` chạy `sql/01_create_tables.sql` trên cả 5 server. `seed_data.py` sinh dữ liệu mẫu cho cơ sở, khoa, học phần, sinh viên, giảng viên, phòng học, lớp học phần và lịch học.

Nếu muốn chạy SQL thủ công trong pgAdmin, mỗi server chạy:

1. `sql/01_create_tables.sql`
2. `sql/02_insert_common_data.sql`
3. File site riêng:

| Site | File SQL |
| --- | --- |
| HL | `sql/03_insert_site_hoalac.sql` |
| NT | `sql/04_insert_site_ngoctruc.sql` |
| HD | `sql/05_insert_site_hadong.sql` |
| CG | `sql/06_insert_site_caugiay.sql` |
| HCM | `sql/07_insert_site_hcm.sql` |

## Kết Nối pgAdmin

Trong pgAdmin, tự register 5 server connection:

| Name | Host | Port | Maintenance database |
| --- | --- | --- | --- |
| `site_hoalac` | `localhost` | `5440` | `site_hoalac` |
| `site_ngoctruc` | `localhost` | `5441` | `site_ngoctruc` |
| `site_hadong` | `localhost` | `5442` | `site_hadong` |
| `site_caugiay` | `localhost` | `5443` | `site_caugiay` |
| `site_hcm` | `localhost` | `5444` | `site_hcm` |

Username: `postgres`

Password: `toantk178@`

pgAdmin không tự hiện container Docker, nên phải register thủ công.

## Chạy Web

```powershell
streamlit run app.py
```

Mở trình duyệt tại:

```text
http://localhost:8501
```

## Test Truy Vấn Phân Tán

```powershell
python test_queries.py
```

## Chức Năng Chính

- Tổng quan hệ thống và trạng thái kết nối 5 site
- Quản lý cơ sở đào tạo
- Quản lý sinh viên
- Quản lý giảng viên
- Quản lý học phần
- Quản lý lớp học phần
- Quản lý phòng học và lịch học
- Đăng ký học phần
- Hủy đăng ký học phần
- Tra cứu kết quả đăng ký
- Truy vấn phân tán / thống kê
- Mô phỏng đăng ký đồng thời
- Nhật ký thao tác

## Truy Vấn Phân Tán

Các truy vấn hiện có:

- Thống kê số lượt đăng ký học phần theo cơ sở
- Học phần có nhiều sinh viên đăng ký nhất toàn trường
- Danh sách sinh viên đăng ký chéo cơ sở
- Tỷ lệ lấp đầy lớp học phần
- Thống kê số lớp học phần mở theo cơ sở
- Thống kê số sinh viên theo cơ sở
- Danh sách lớp học phần toàn trường

## Xử Lý Đồng Thời

Đăng ký học phần dùng transaction:

- Kiểm tra sinh viên tại site gốc của sinh viên
- Ghi đăng ký tại site mở lớp
- Khóa dòng lớp học phần bằng `SELECT ... FOR UPDATE`
- Kiểm tra `number_of_student < max_student`
- Insert/khôi phục đăng ký
- Tăng sĩ số lớp
- Commit hoặc rollback

Mô phỏng đồng thời dùng `threading`, nhiều sinh viên cùng đăng ký một lớp để chứng minh không vượt sĩ số.

## Dừng Hệ Thống

Tắt container nhưng giữ dữ liệu:

```powershell
docker compose down
```

Reset sạch database:

```powershell
docker compose down -v
docker compose up -d
.\run_sql.bat
python seed_data.py
```

## Ghi Chú Schema

Quan hệ phòng học và lớp học phần:

```text
LopHocPhan 1 - n LichHoc n - 1 PhongHoc
```

Vì vậy `lophocphan` không lưu `id_room`; phòng học được gắn qua bảng `lichhoc`.
