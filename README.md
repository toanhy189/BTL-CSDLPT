# Hệ thống đăng ký học phần nhiều cơ sở

Đồ án Cơ sở dữ liệu phân tán mô phỏng hệ thống đăng ký học phần cho trường đại học có nhiều cơ sở đào tạo. Mỗi cơ sở có một PostgreSQL site riêng để quản lý dữ liệu cục bộ. Các danh mục dùng chung toàn trường được nhân bản để các site có thể xử lý nghiệp vụ độc lập hơn.

## 1. Kiến trúc tổng quan

```text
Streamlit Frontend -> FastAPI Backend -> psycopg2/pandas -> 5 PostgreSQL site
```

Thành phần chính:

- `frontend/streamlit_app`: giao diện Streamlit.
- `backend`: FastAPI backend.
- `sql`: script tạo schema, trigger và replication.
- `seed_data.py`: sinh dữ liệu mẫu.
- `docker-compose.yml`: cấu hình 5 PostgreSQL container.

Vai trò người dùng:

- `ADMIN`: quản trị hệ thống.
- `SINH_VIEN`: đăng ký/hủy học phần, xem lịch học.
- `GIANG_VIEN`: xem lớp phụ trách, danh sách sinh viên và lịch dạy.

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

Project sử dụng **phân mảnh ngang theo cơ sở/site**.

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

Nguyên tắc lưu dữ liệu:

- Sinh viên, giảng viên, phòng học, lớp học phần và lịch học thuộc cơ sở nào thì lưu tại site cơ sở đó.
- Bản ghi đăng ký học phần được lưu tại site mở lớp học phần.
- Nếu sinh viên ở cơ sở này đăng ký lớp mở tại cơ sở khác thì đó là đăng ký chéo cơ sở.
- Dữ liệu dùng chung được nhân bản để giảm truy vấn liên site khi xử lý nghiệp vụ.

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
- `OfflineOperationLog`: yêu cầu đăng ký/hủy đăng ký bị gián đoạn do site mất kết nối.

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

## 8. Setup database tự động

Chạy trong thư mục `BTL-CSDLPT`:

```powershell
.\setup_all.bat
```

Script này tự khởi động Docker, chờ 5 PostgreSQL site sẵn sàng, tạo schema/trigger, sinh dữ liệu mẫu và cấu hình logical replication cho các bảng dùng chung từ `site_hadong` sang các site còn lại.

## 9. Setup database thủ công

Nếu muốn chạy từng bước:

```powershell
.\run_sql.bat
python seed_data.py
.\setup_replication.bat
```

Ý nghĩa:

- `run_sql.bat`: tạo lại schema và trigger trên 5 site.
- `seed_data.py`: sinh dữ liệu mẫu.
- `setup_replication.bat`: tạo role `replicator`, publication `pub_common_data` trên `site_hadong` và subscription sang các site còn lại.

Lưu ý: `run_sql.bat` drop/create lại bảng, nên dữ liệu hiện tại sẽ mất.

## 10. Chạy backend FastAPI

```powershell
uvicorn backend.main:app --reload --port 8000
```

Kiểm tra API:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

Khi backend khởi động, hệ thống tự tạo bảng `taikhoan` nếu chưa có. Bảng `offlineoperationlog` cũng được tự tạo tại site điều phối `HD` nếu chưa tồn tại.

## 11. Chạy frontend Streamlit

Mở terminal khác, vẫn trong thư mục `BTL-CSDLPT`:

```powershell
streamlit run frontend/streamlit_app/app.py
```

Frontend mặc định chạy tại:

```text
http://localhost:8501
```

## 12. Tài khoản demo

| Vai trò | Username | Password | Ghi chú |
| --- | --- | --- | --- |
| ADMIN | `admin` | `admin123` | Quản trị hệ thống |
| SINH_VIEN | mã sinh viên viết thường | `123456` | Ví dụ `sv-hl-0001` nếu có sinh viên `SV-HL-0001` |
| GIANG_VIEN | mã giảng viên viết thường | `123456` | Ví dụ `gv-hl-0001` nếu có giảng viên `GV-HL-0001` |

## 13. Chức năng theo vai trò

### ADMIN

- Xem tổng quan hệ thống.
- Xem trạng thái kết nối 5 site.
- Quản lý sinh viên, giảng viên, học phần, chương trình đào tạo, đợt đăng ký, lớp học phần, phòng học và lịch học.
- Mở/đóng đăng ký học phần.
- Chạy truy vấn phân tán.
- Mô phỏng đăng ký đồng thời.
- Xem nhật ký thao tác.
- Xem và xử lý yêu cầu chờ khi site mất kết nối.

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

## 14. Luồng xử lý đăng ký học phần

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

File xử lý chính:

```text
backend/services/registration_service.py
```

## 15. Kiểm soát đồng thời và phòng tránh deadlock

Project xử lý đăng ký đồng thời bằng:

- Transaction.
- `SELECT ... FOR UPDATE` để khóa dòng lớp học phần.
- `pg_advisory_xact_lock()` để khóa logic theo sinh viên và học phần.
- Khóa các lớp liên quan theo thứ tự cố định khi đổi lớp.
- Trigger đồng bộ sĩ số.
- Atomic update để không vượt quá sĩ số tối đa.
- Rollback khi lớp đầy hoặc có lỗi.

Trigger tăng sĩ số dùng atomic update:

```sql
UPDATE LopHocPhan
SET number_of_student = number_of_student + 1
WHERE ID = NEW.ID_class
  AND number_of_student < max_student;
```

File trigger:

```text
sql/08_create_triggers.sql
```

Demo đổi lớp chéo để minh họa phòng tránh deadlock:

```text
demo_swap_deadlock_solution.py
```

Tình huống demo:

- Sinh viên A đổi từ lớp 1 sang lớp 2.
- Sinh viên B đổi từ lớp 2 sang lớp 1.
- Hệ thống khóa các lớp theo thứ tự cố định để không tạo vòng chờ.

## 16. Truy vấn phân tán

Các truy vấn phân tán được thực hiện bằng cách backend kết nối đến từng site, lấy dữ liệu cục bộ rồi tổng hợp kết quả toàn trường bằng pandas/logic ứng dụng.

Các truy vấn chính:

- Thống kê số lượt đăng ký học phần theo từng cơ sở.
- Tìm học phần có nhiều sinh viên đăng ký nhất toàn trường.
- Danh sách sinh viên đăng ký chéo cơ sở.
- Tỷ lệ lấp đầy của các lớp học phần trên toàn hệ thống.
- Thống kê số lớp học phần mở theo cơ sở.
- Thống kê số sinh viên theo cơ sở.
- Danh sách lớp học phần toàn trường.

File liên quan:

```text
backend/db/distributed_queries.py
backend/api/distributed_query_api.py
```

## 17. Replication dữ liệu dùng chung

Docker đã bật các tham số phục vụ logical replication:

- `wal_level=logical`
- `max_replication_slots=10`
- `max_wal_senders=10`

Logical replication được cấu hình bằng:

```text
setup_replication.bat
```

Site `site_hadong` là publisher/source cho các bảng dùng chung:

- `CoSo`
- `Khoa`
- `HocPhan`
- `ChuongTrinhDaoTao`
- `DotDangKy`

Các site `site_hoalac`, `site_ngoctruc`, `site_caugiay`, `site_hcm` là subscriber/replica.

Project không replication bảng `DangKy` làm dữ liệu ghi chính, vì đây là bảng giao dịch có tần suất thay đổi cao, dễ phát sinh conflict và sai lệch sĩ số nếu nhiều site cùng ghi.

## 18. Xử lý khi một site tạm thời mất kết nối

Project bổ sung cơ chế ghi nhận yêu cầu bị gián đoạn bằng bảng:

```text
OfflineOperationLog
```

Bảng này được lưu tại site điều phối `HD`.

Khi đăng ký hoặc hủy đăng ký gặp lỗi do site mất kết nối:

1. Hệ thống không ghi tạm vào `DangKy`.
2. Rollback transaction nếu có.
3. Lưu yêu cầu vào `OfflineOperationLog`.
4. Gán trạng thái `PENDING`.
5. Admin xử lý lại khi site online.

Các trạng thái:

| Trạng thái | Ý nghĩa |
| --- | --- |
| `PENDING` | Chờ xử lý lại |
| `RETRYING` | Đang thử xử lý lại |
| `DONE` | Xử lý thành công |
| `FAILED` | Xử lý thất bại |
| `CANCELLED` | Admin hủy yêu cầu |

Giao diện admin có mục **Yêu cầu chờ xử lý**:

- Xem danh sách yêu cầu chờ.
- Thử lại một yêu cầu.
- Hủy một yêu cầu.
- Xử lý tất cả các yêu cầu có thể thử lại.

Khi xử lý lại, hệ thống gọi lại logic nghiệp vụ thật (`register_course` hoặc `cancel_registration`), nên vẫn kiểm tra lại đầy đủ:

- Đợt đăng ký còn mở không.
- Lớp còn chỗ không.
- Có trùng lịch không.
- Sinh viên đã đăng ký lớp đó chưa.
- Site đã kết nối lại chưa.

File liên quan:

```text
backend/services/offline_operation_service.py
backend/api/admin_api.py
frontend/streamlit_app/ui_pages/admin/admin_offline_operations_page.py
```

## 19. Kết nối pgAdmin

Register thủ công 5 server:

| Name | Host | Port | Maintenance database |
| --- | --- | --- | --- |
| `site_hoalac` | `localhost` | `5440` | `site_hoalac` |
| `site_ngoctruc` | `localhost` | `5441` | `site_ngoctruc` |
| `site_hadong` | `localhost` | `5442` | `site_hadong` |
| `site_caugiay` | `localhost` | `5443` | `site_caugiay` |
| `site_hcm` | `localhost` | `5444` | `site_hcm` |

Thông tin đăng nhập PostgreSQL nằm trong `docker-compose.yml`.

## 20. Dừng và reset hệ thống

Dừng container nhưng giữ volume dữ liệu:

```powershell
docker compose down
```

Reset sạch database:

```powershell
docker compose down -v
.\setup_all.bat
```

Sau đó chạy lại backend để tạo/seed bảng `taikhoan` nếu cần.

## 21. Các file quan trọng

| File | Vai trò |
| --- | --- |
| `docker-compose.yml` | Cấu hình 5 PostgreSQL site |
| `sql/01_create_tables.sql` | Schema toàn cục |
| `sql/08_create_triggers.sql` | Trigger đồng bộ sĩ số |
| `run_sql.bat` | Tạo schema và trigger trên 5 site |
| `setup_all.bat` | Setup database, dữ liệu mẫu và replication bằng một lệnh |
| `setup_replication.bat` | Tạo publication/subscription cho dữ liệu dùng chung |
| `seed_data.py` | Sinh dữ liệu mẫu |
| `backend/services/registration_service.py` | Xử lý đăng ký, hủy, đồng thời và đổi lớp |
| `backend/services/offline_operation_service.py` | Lưu và xử lý lại yêu cầu khi site mất kết nối |
| `backend/db/distributed_queries.py` | Truy vấn phân tán |
| `frontend/streamlit_app/app.py` | Router giao diện Streamlit |

