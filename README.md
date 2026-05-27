# Hệ thống đăng ký học phần nhiều cơ sở

Đồ án CSDL phân tán mô phỏng hệ thống đăng ký học phần trên 5 cơ sở đào tạo.

## Kiến trúc

```text
Streamlit Frontend -> FastAPI Backend -> psycopg2/pandas -> 5 PostgreSQL site
```

- Frontend: `frontend/streamlit_app`
- Backend API: `backend`
- Database: 5 PostgreSQL server chạy bằng Docker
- Xác thực: JWT
- Mật khẩu tài khoản: bcrypt
- Phân quyền: `ADMIN`, `GIANG_VIEN`, `SINH_VIEN`

## Công nghệ
- Python
- Streamlit
- FastAPI
- PostgreSQL
- Docker Compose
- psycopg2
- pandas
- bcrypt
- PyJWT
- pgAdmin

## 5 site PostgreSQL

| Site | Container | Database | Port |
| --- | --- | --- | --- |
| HL - Hòa Lạc | `postgres_hoalac` | `site_hoalac` | `5440` |
| NT - Ngọc Trục | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| HD - Hà Đông | `postgres_hadong` | `site_hadong` | `5442` |
| CG - Cầu Giấy | `postgres_caugiay` | `site_caugiay` | `5443` |
| HCM - TP.HCM | `postgres_hcm` | `site_hcm` | `5444` |


## Cài thư viện

Chạy trong thư mục `BTL-CSDLPT`:

```powershell
pip install -r requirements.txt
```

## Chạy database

```powershell
docker compose up -d
docker compose ps
```

## Tạo bảng và import dữ liệu

Cách nhanh:

```powershell
.\run_sql.bat
python seed_data.py
```

Sau khi backend FastAPI khởi động, hệ thống tự tạo thêm bảng `taikhoan` nếu chưa có và seed tài khoản demo.

## Chạy backend FastAPI

```powershell
uvicorn backend.main:app --reload --port 8000
```

Kiểm tra API:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Chạy frontend Streamlit

Mở terminal khác, vẫn trong thư mục `BTL-CSDLPT`:

```powershell
streamlit run frontend/streamlit_app/app.py
```

Frontend chạy tại:

```text
http://localhost:8501
```

## Tài khoản demo

Backend tự tạo tài khoản khi khởi động:

| Role | Username | Password | Ghi chú |
| --- | --- | --- | --- |
| ADMIN | `admin` | `admin123` | Quản trị hệ thống |
| SINH_VIEN | mã sinh viên viết thường | `123456` | Ví dụ `hl_sv001` nếu dữ liệu có mã `HL_SV001` |
| GIANG_VIEN | mã giảng viên viết thường | `123456` | Ví dụ `hl_gv001` nếu dữ liệu có mã `HL_GV001` |

## Chức năng theo role

### ADMIN

- Tổng quan hệ thống
- Trạng thái kết nối 5 site
- Quản lý sinh viên, giảng viên, học phần, lớp học phần, phòng học, lịch học
- Truy vấn phân tán / thống kê
- Mô phỏng đăng ký đồng thời
- Xem nhật ký thao tác

### SINH_VIEN

- Xem trang chủ và hồ sơ cá nhân
- Xem lớp học phần mở
- Đăng ký học phần
- Hủy đăng ký
- Tra cứu kết quả đăng ký
- Xem thời khóa biểu

### GIANG_VIEN

- Xem lớp học phần phụ trách
- Xem danh sách sinh viên theo lớp
- Xem lịch dạy
- Xem thống kê lớp

## API chính

- `POST /auth/login`
- `GET /auth/me`
- `GET /admin/dashboard`
- `GET /admin/sites/status`
- `GET /admin/students?site_code=HL`
- `POST /admin/students`
- `POST /student/register`
- `POST /student/cancel`
- `GET /student/registrations`
- `GET /student/open-classes`
- `GET /student/schedule`
- `GET /teacher/classes`
- `GET /teacher/schedule`
- `GET /distributed/registration-by-site`
- `GET /distributed/top-courses`
- `GET /distributed/cross-site-students`
- `GET /distributed/fill-rate`
- `GET /distributed/classes-by-site`
- `GET /distributed/students-by-site`
- `POST /concurrency/simulate-registration`
- `GET /concurrency/logs`

## Truy vấn phân tán

Các truy vấn đọc dữ liệu từ 5 site, sau đó tổng hợp bằng pandas:

- Thống kê số lượt đăng ký học phần theo cơ sở
- Học phần có nhiều sinh viên đăng ký nhất toàn trường
- Danh sách sinh viên đăng ký chéo cơ sở
- Tỷ lệ lấp đầy lớp học phần
- Thống kê số lớp học phần mở theo cơ sở
- Thống kê số sinh viên theo cơ sở
- Danh sách lớp học phần toàn trường

## Xử lý đồng thời

Đăng ký học phần được xử lý trong transaction:

- Kiểm tra sinh viên tại site gốc
- Ghi đăng ký tại site mở lớp
- Khóa dòng lớp học phần bằng `SELECT ... FOR UPDATE`
- Kiểm tra `number_of_student < max_student`
- Insert đăng ký
- Tăng sĩ số lớp
- Commit hoặc rollback

Trang mô phỏng đồng thời dùng `threading` để nhiều sinh viên đăng ký cùng lúc một lớp. Kết quả chứng minh sĩ số không vượt `max_student`.

## Kết nối pgAdmin

Trong pgAdmin, register thủ công 5 server:

| Name | Host | Port | Maintenance database |
| --- | --- | --- | --- |
| `site_hoalac` | `localhost` | `5440` | `site_hoalac` |
| `site_ngoctruc` | `localhost` | `5441` | `site_ngoctruc` |
| `site_hadong` | `localhost` | `5442` | `site_hadong` |
| `site_caugiay` | `localhost` | `5443` | `site_caugiay` |
| `site_hcm` | `localhost` | `5444` | `site_hcm` |

pgAdmin không tự hiện container Docker, nên phải register từng server.

## Dừng hệ thống

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

Sau đó chạy lại backend để tạo/seed bảng `taikhoan`.
