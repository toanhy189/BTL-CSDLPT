-- =========================================================
-- 1. XÓA BẢNG NẾU ĐÃ TỒN TẠI (Thứ tự ngược với lúc tạo)
-- =========================================================
DROP TABLE IF EXISTS DangKy;
DROP TABLE IF EXISTS LopHocPhan;
DROP TABLE IF EXISTS SinhVien;
DROP TABLE IF EXISTS GiangVien;
DROP TABLE IF EXISTS Khoa;
DROP TABLE IF EXISTS HocPhan;
DROP TABLE IF EXISTS PhongHoc;
DROP TABLE IF EXISTS CoSo;

-- =========================================================
-- 2. TẠO LẠI CÁC BẢNG (Theo thứ tự cha -> con)
-- =========================================================

-- 1. BẢNG CƠ SỞ (Từ ảnh: dbo.headquarter)
CREATE TABLE CoSo (
    ID varchar(255) NOT NULL,
    name_headquarter varchar(255),
    address varchar(255),
    CONSTRAINT PK_CoSo PRIMARY KEY (ID)
);

-- 2. BẢNG PHÒNG HỌC
CREATE TABLE PhongHoc (
    ID varchar(255) NOT NULL,
    name_room varchar(255),
    capacity int,
    ID_headquarter varchar(255) NOT NULL,
    CONSTRAINT PK_PhongHoc PRIMARY KEY (ID),
    CONSTRAINT FK_PhongHoc_CoSo FOREIGN KEY (ID_headquarter) REFERENCES CoSo(ID)
);

-- 3. BẢNG KHOA
CREATE TABLE Khoa (
    ID varchar(255) NOT NULL,
    name_department varchar(255),
    CONSTRAINT PK_Khoa PRIMARY KEY (ID)
);

-- 4. BẢNG HỌC PHẦN (Từ ảnh: dbo.subject)
CREATE TABLE HocPhan (
    ID varchar(255) NOT NULL,
    name_subject varchar(255),
    number_of_credit int,
    CONSTRAINT PK_HocPhan PRIMARY KEY (ID)
);

-- 5. BẢNG GIẢNG VIÊN (Từ ảnh: dbo.teacher)
CREATE TABLE GiangVien (
    ID varchar(255) NOT NULL,
    name_teacher varchar(255),
    address_teacher varchar(255),
    degree varchar(255),
    phone_teacher varchar(255),
    ID_department varchar(255) NOT NULL,
    CONSTRAINT PK_GiangVien PRIMARY KEY (ID),
    CONSTRAINT FK_GiangVien_Khoa FOREIGN KEY (ID_department) REFERENCES Khoa(ID)
);

-- 6. BẢNG SINH VIÊN (Từ ảnh: dbo.student)
CREATE TABLE SinhVien (
    ID varchar(255) NOT NULL,
    name_student varchar(255),
    date_of_birth date,
    address_student varchar(255),
    formal_class varchar(255),
    year_of_admission int,
    phone_student varchar(255),
    ID_department varchar(255) NOT NULL,
    CONSTRAINT PK_SinhVien PRIMARY KEY (ID),
    CONSTRAINT FK_SinhVien_Khoa FOREIGN KEY (ID_department) REFERENCES Khoa(ID)
);

-- 7. BẢNG LỚP HỌC PHẦN (Từ ảnh: dbo.class)
CREATE TABLE LopHocPhan (
    ID varchar(255) NOT NULL,
    semester int,
    school_year int,
    number_of_student int,
    shift int,
    ID_subject varchar(255) NOT NULL,
    ID_teacher varchar(255) NOT NULL,
    ID_room varchar(255),
    CONSTRAINT PK_LopHocPhan PRIMARY KEY (ID),
    CONSTRAINT FK_Lop_HocPhan FOREIGN KEY (ID_subject) REFERENCES HocPhan(ID),
    CONSTRAINT FK_Lop_GiangVien FOREIGN KEY (ID_teacher) REFERENCES GiangVien(ID),
    CONSTRAINT FK_Lop_PhongHoc FOREIGN KEY (ID_room) REFERENCES PhongHoc(ID)
);

-- 8. BẢNG ĐĂNG KÝ
CREATE TABLE DangKy (
    ID_student varchar(255) NOT NULL,
    ID_class varchar(255) NOT NULL,
    registration_date date,
    CONSTRAINT PK_DangKy PRIMARY KEY (ID_student, ID_class),
    CONSTRAINT FK_DangKy_SinhVien FOREIGN KEY (ID_student) REFERENCES SinhVien(ID),
    CONSTRAINT FK_DangKy_LopHocPhan FOREIGN KEY (ID_class) REFERENCES LopHocPhan(ID)
);