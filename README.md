# BTL CSDLPT - Dang Ky Hoc Phan

## Mo hinh PostgreSQL phan tan

Project dung 5 container PostgreSQL rieng, moi container la mot server/site:

| Site | Container | Database | Port |
| --- | --- | --- | --- |
| Hoa Lac | `postgres_hoalac` | `site_hoalac` | `5440` |
| Ngoc Truc | `postgres_ngoctruc` | `site_ngoctruc` | `5441` |
| Ha Dong | `postgres_hadong` | `site_hadong` | `5442` |
| Cau Giay | `postgres_caugiay` | `site_caugiay` | `5443` |
| HCM | `postgres_hcm` | `site_hcm` | `5444` |

Username: `postgres`

Password: `toantk178@`

## Chay Docker

```powershell
docker compose up -d
docker ps
```

## Hướng dẫn chạy và setup cho nhóm
Để setup toàn bộ 5 server và đẩy dữ liệu mẫu vào, chỉ cần làm theo 4 bước sau:

**Bước 1: Bật các server PostgreSQL bằng Docker**
```powershell
docker compose up -d
```

**Bước 2: Tạo cấu trúc bảng cho 5 Database**
Chạy file `.bat` sau (trên Windows) để tự động đẩy file `sql/01_create_tables.sql` vào cả 5 server:
```powershell
.\run_sql.bat
```

**Bước 3: Cài đặt thư viện Python**
```powershell
pip install -r requirements.txt
```

**Bước 4: Bơm dữ liệu mẫu (Mock Data)**
Chạy script Python dưới đây. Script sẽ tự động kết nối 5 database, insert dữ liệu chung (Khoa, Học phần) và dữ liệu cục bộ (Sinh viên, Phòng học, Lớp HP) đúng theo nguyên tắc phân mảnh:
```powershell
python seed_data.py
```
