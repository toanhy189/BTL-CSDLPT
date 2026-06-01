# Hệ thống đăng ký học phần nhiều cơ sở

Đồ án Cơ sở dữ liệu phân tán mô phỏng hệ thống đăng ký học phần cho trường đại học có nhiều cơ sở đào tạo. Mỗi cơ sở có một PostgreSQL site riêng để quản lý dữ liệu cục bộ, đồng thời các danh mục dùng chung toàn trường được nhân bản trên các site.

## 1. Kiến trúc

```text
Streamlit Frontend -> FastAPI Backend -> psycopg2/pandas -> 5 PostgreSQL site
```

- Frontend: `frontend/streamlit_app`
- Backend API: `backend`
- Database: 5 PostgreSQL container
- Xác thực: JWT
- Mật khẩu tài khoản: bcrypt
- Phân quyền: `ADMIN`, `GIANG_VIEN`, `SINH_VIEN`

## 2. Công nghệ sử dụng

- Python
- FastAPI
- Streamlit
- PostgreSQL
- Docker Compose
- psycopg2
- pandas
- bcrypt
- PyJWT
- pgAdmin

## 3. Các site PostgreSQL

| Site | Cơ sở | Container | Database | Port |
| --- | --- | --- | --- | --- |
| HL | Hòa Lạc | `postgres_hoalac` | `site_hoalac` | `5440` |
| NT | Ngọc Trúc | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| HD | Hà Đông | `postgres_hadong` | `site_hadong` | `5442` |
| CG | Cầu Giấy | `postgres_caugiay` | `site_caugiay` | `5443` |
| HCM | TP. Hồ Chí Minh | `postgres_hcm` | `site_hcm` | `5444` |

## 4. Mô hình dữ liệu phân tán

Project sử dụng phân mảnh ngang theo địa điểm/cơ sở.

Dữ liệu cục bộ theo từng cơ sở:

- `SinhVien`
- `GiangVien`
- `PhongHoc`
- `LopHocPhan`
- `LichHoc`
- `DangKy`

Dữ liệu dùng chung, được nhân bản trên các site:

- `CoSo`
- `Khoa`
- `HocPhan`
- `ChuongTrinhDaoTao`
- `DotDangKy`

Ý nghĩa:

- Sinh viên, giảng viên, phòng học, lớp học phần và lịch học thuộc cơ sở nào thì lưu tại site cơ sở đó.
- Bản ghi đăng ký được lưu tại site mở lớp học phần.
- Nếu sinh viên ở cơ sở này đăng ký lớp mở tại cơ sở khác thì đó là đăng ký chéo cơ sở.
- Danh mục học phần, chương trình đào tạo và đợt đăng ký được nhân bản để các site có thể xử lý nghiệp vụ độc lập hơn.

## 5. Lược đồ chính

Các bảng nghiệp vụ chính:

- `CoSo`: danh sách cơ sở đào tạo.
- `Khoa`: danh sách khoa/ngành.
- `HocPhan`: danh mục học phần dùng chung.
- `ChuongTrinhDaoTao`: học phần thuộc chương trình đào tạo của từng khoa/ngành.
- `DotDangKy`: đợt đăng ký theo học kỳ, năm học, khoa/ngành và khóa tuyển sinh.
- `SinhVien`: sinh viên.
- `GiangVien`: giảng viên.
- `PhongHoc`: phòng học.
- `LopHocPhan`: lớp học phần được mở.
- `LichHoc`: lịch học theo ngày, tuần, tiết, giờ và phòng.
- `DangKy`: bản ghi đăng ký học phần.

Bảng `DangKy` liên kết với `DotDangKy` qua `ID_registration_period`, giúp xác định mỗi bản ghi đăng ký thuộc đợt đăng ký nào.

## 6. Cài đặt thư viện

Chạy trong thư mục `BTL-CSDLPT`:

```powershell
pip install -r requirements.txt
```

## 7. Khởi động database

```powershell
docker compose up -d
docker compose ps
```

## 8. Tạo schema và dữ liệu mẫu

Chạy trong thư mục `BTL-CSDLPT`:

```powershell
.\run_sql.bat
python seed_data.py
```

`run_sql.bat` tạo lại schema trên 5 site và nạp trigger. `seed_data.py` sinh dữ liệu mẫu gồm cơ sở, khoa, học phần, chương trình đào tạo, đợt đăng ký, sinh viên, giảng viên, phòng học, lớp học phần và lịch học.

Lưu ý: lệnh `run_sql.bat` drop/create lại bảng. Nếu đã cấu hình logical replication thủ công trong pgAdmin thì cần cấu hình lại sau khi reset schema.

## 9. Chạy backend FastAPI

```powershell
uvicorn backend.main:app --reload --port 8000
```

Kiểm tra API:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Khi backend khởi động, hệ thống tự tạo bảng `taikhoan` nếu chưa có và seed tài khoản demo.

## 10. Chạy frontend Streamlit

Mở terminal khác, vẫn trong thư mục `BTL-CSDLPT`:

```powershell
streamlit run frontend/streamlit_app/app.py
```

Frontend mặc định chạy tại:

```text
http://localhost:8501
```

## 11. Tài khoản demo

| Vai trò | Username | Password | Ghi chú |
| --- | --- | --- | --- |
| ADMIN | `admin` | `admin123` | Quản trị hệ thống |
| SINH_VIEN | mã sinh viên viết thường | `123456` | Ví dụ `sv-hl-0001` nếu có sinh viên `SV-HL-0001` |
| GIANG_VIEN | mã giảng viên viết thường | `123456` | Ví dụ `gv-hl-0001` nếu có giảng viên `GV-HL-0001` |

## 12. Chức năng theo vai trò

### ADMIN

- Xem tổng quan hệ thống.
- Xem trạng thái kết nối 5 site.
- Quản lý sinh viên.
- Quản lý giảng viên.
- Quản lý học phần.
- Quản lý chương trình đào tạo.
- Quản lý đợt đăng ký.
- Quản lý lớp học phần.
- Quản lý phòng học.
- Quản lý lịch học.
- Mở/đóng đăng ký học phần.
- Chạy truy vấn phân tán.
- Mô phỏng đăng ký đồng thời.
- Xem nhật ký thao tác.

### SINH_VIEN

- Xem trang chủ và hồ sơ cá nhân.
- Xem lớp học phần được phép đăng ký theo đợt đăng ký và chương trình đào tạo.
- Đăng ký học phần.
- Hủy đăng ký học phần.
- Xem thời khóa biểu.

### GIANG_VIEN

- Xem lớp học phần phụ trách.
- Xem danh sách sinh viên theo lớp.
- Xem lịch dạy theo tuần.

## 13. Xử lý đăng ký học phần

Khi sinh viên đăng ký một lớp học phần, backend thực hiện:

1. Kiểm tra trạng thái đăng ký chung có đang mở không.
2. Xác định sinh viên thuộc site nào.
3. Lấy khoa/ngành và năm nhập học của sinh viên.
4. Kiểm tra lớp học phần tồn tại tại site mở lớp.
5. Kiểm tra có `DotDangKy` hợp lệ theo học kỳ, năm học, khoa/ngành, khóa tuyển sinh và thời gian hiện tại.
6. Kiểm tra học phần nằm trong `ChuongTrinhDaoTao` của sinh viên.
7. Khóa lớp học phần bằng transaction.
8. Kiểm tra lớp còn chỗ.
9. Kiểm tra trùng lịch học.
10. Nếu sinh viên đã đăng ký lớp khác cùng học phần, cùng kỳ, cùng năm thì xử lý như đổi lớp.
11. Ghi bản ghi `DangKy`.
12. Trigger tự động cập nhật sĩ số.
13. Commit nếu thành công, rollback nếu có lỗi.

## 14. Kiểm soát đồng thời

Project xử lý đăng ký đồng thời bằng:

- Transaction.
- `SELECT ... FOR UPDATE` để khóa dòng lớp học phần.
- Advisory lock theo sinh viên và học phần.
- Trigger đồng bộ sĩ số.
- Atomic update để không vượt quá sĩ số tối đa.
- Rollback khi lớp đầy hoặc có lỗi.

Tình huống demo:

- Một lớp học phần có số chỗ giới hạn.
- Nhiều sinh viên cùng đăng ký lớp đó tại cùng thời điểm.
- Hệ thống đảm bảo chỉ số lượng sinh viên hợp lệ được đăng ký, sĩ số không vượt `max_student`.

## 15. Trigger

File trigger:

```text
sql/08_create_triggers.sql
```

Trigger trên bảng `DangKy` dùng để:

- Tăng `LopHocPhan.number_of_student` khi đăng ký thành công.
- Giảm `LopHocPhan.number_of_student` khi hủy đăng ký.
- Chặn đăng ký nếu lớp đã đầy.
- Kiểm tra đăng ký phải gắn với `DotDangKy`.
- Kiểm tra lớp học phần thuộc đúng học kỳ/năm học của đợt đăng ký.

Trigger sử dụng atomic update:

```sql
UPDATE LopHocPhan
SET number_of_student = number_of_student + 1
WHERE ID = NEW.ID_class
  AND number_of_student < max_student;
```

Cách này giúp tránh lỗi nhiều transaction cùng đọc thấy còn chỗ rồi cùng tăng sĩ số vượt giới hạn.

## 16. Phòng tránh deadlock khi đổi lớp

Project xử lý tình huống sinh viên đổi lớp học phần cùng môn.

Ví dụ:

- Sinh viên A đổi từ lớp 1 sang lớp 2.
- Sinh viên B đổi từ lớp 2 sang lớp 1.

Nếu mỗi transaction khóa lớp cũ trước rồi lớp mới sau thì có thể xảy ra deadlock. Project xử lý bằng cách:

- Gom các lớp liên quan.
- Sắp xếp mã lớp theo thứ tự cố định.
- Khóa các lớp theo cùng thứ tự bằng `SELECT ... FOR UPDATE`.

Nhờ đó các transaction không tạo vòng chờ.

## 17. Truy vấn phân tán

Các truy vấn phân tán được thực hiện bằng cách backend kết nối đến từng site, lấy dữ liệu cục bộ rồi tổng hợp kết quả toàn trường bằng pandas/logic ứng dụng.

Các truy vấn chính:

- Thống kê số lượt đăng ký học phần theo từng cơ sở.
- Tìm học phần có nhiều sinh viên đăng ký nhất toàn trường.
- Danh sách sinh viên đăng ký chéo cơ sở.
- Tỷ lệ lấp đầy của các lớp học phần trên toàn hệ thống.
- Thống kê số lớp học phần mở theo cơ sở hoặc theo khoa.
- Thống kê số sinh viên theo cơ sở.
- Danh sách lớp học phần toàn trường.

## 18. Replication dữ liệu dùng chung

Docker đã bật các tham số phục vụ logical replication:

- `wal_level=logical`
- `max_replication_slots=10`
- `max_wal_senders=10`

Trong dữ liệu mẫu, các bảng dùng chung được nhân bản bằng script seed vào 5 site:

- `CoSo`
- `Khoa`
- `HocPhan`
- `ChuongTrinhDaoTao`
- `DotDangKy`

Đã demo logical replication thật, có thể cấu hình publication/subscription trong PostgreSQL hoặc pgAdmin cho các bảng dùng chung.

## 19. Kết nối pgAdmin

Trong pgAdmin, register thủ công 5 server:

| Name | Host | Port | Maintenance database |
| --- | --- | --- | --- |
| `site_hoalac` | `localhost` | `5440` | `site_hoalac` |
| `site_ngoctruc` | `localhost` | `5441` | `site_ngoctruc` |
| `site_hadong` | `localhost` | `5442` | `site_hadong` |
| `site_caugiay` | `localhost` | `5443` | `site_caugiay` |
| `site_hcm` | `localhost` | `5444` | `site_hcm` |

Thông tin đăng nhập PostgreSQL mặc định nằm trong `docker-compose.yml`.

## 20. Dừng và reset hệ thống

Dừng container nhưng giữ volume dữ liệu:

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

## 21. Các file quan trọng

- `docker-compose.yml`: cấu hình 5 PostgreSQL site.
- `sql/01_create_tables.sql`: schema toàn cục.
- `sql/08_create_triggers.sql`: trigger đồng bộ sĩ số.
- `run_sql.bat`: tạo schema và trigger trên 5 site.
- `seed_data.py`: sinh dữ liệu mẫu.
- `backend/services/registration_service.py`: xử lý đăng ký, hủy, đồng thời và đổi lớp.
- `backend/db/queries.py`: truy vấn quản trị và truy vấn phân tán.
- `frontend/streamlit_app/app.py`: giao diện Streamlit.

