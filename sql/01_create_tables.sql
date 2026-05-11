-- =========================================================
-- 1. XÓA BẢNG NẾU ĐÃ TỒN TẠI
-- =========================================================
DROP TABLE IF EXISTS DangKy CASCADE;
DROP TABLE IF EXISTS LichHoc CASCADE;
DROP TABLE IF EXISTS LopHocPhan CASCADE;
DROP TABLE IF EXISTS SinhVien CASCADE;
DROP TABLE IF EXISTS GiangVien CASCADE;
DROP TABLE IF EXISTS PhongHoc CASCADE;
DROP TABLE IF EXISTS HocPhan CASCADE;
DROP TABLE IF EXISTS Khoa CASCADE;
DROP TABLE IF EXISTS CoSo CASCADE;

-- =========================================================
-- 2. TẠO LẠI CÁC BẢNG
-- =========================================================

-- 1. BẢNG CƠ SỞ
CREATE TABLE CoSo (
    ID varchar(255) NOT NULL,
    name_headquarter varchar(255) NOT NULL,
    address varchar(255),
    CONSTRAINT PK_CoSo PRIMARY KEY (ID)
);

-- 2. BẢNG KHOA
CREATE TABLE Khoa (
    ID varchar(255) NOT NULL,
    name_department varchar(255) NOT NULL,
    CONSTRAINT PK_Khoa PRIMARY KEY (ID)
);

-- 3. BẢNG HỌC PHẦN
CREATE TABLE HocPhan (
    ID varchar(255) NOT NULL,
    name_subject varchar(255) NOT NULL,
    number_of_credit int NOT NULL,
    ID_department varchar(255) NOT NULL,
    CONSTRAINT PK_HocPhan PRIMARY KEY (ID),
    CONSTRAINT FK_HocPhan_Khoa 
        FOREIGN KEY (ID_department) REFERENCES Khoa(ID)
);

-- 4. BẢNG PHÒNG HỌC
CREATE TABLE PhongHoc (
    ID varchar(255) NOT NULL,
    name_room varchar(255) NOT NULL,
    capacity int NOT NULL,
    ID_headquarter varchar(255) NOT NULL,
    CONSTRAINT PK_PhongHoc PRIMARY KEY (ID),
    CONSTRAINT FK_PhongHoc_CoSo 
        FOREIGN KEY (ID_headquarter) REFERENCES CoSo(ID)
);

-- 5. BẢNG GIẢNG VIÊN
CREATE TABLE GiangVien (
    ID varchar(255) NOT NULL,
    name_teacher varchar(255) NOT NULL,
    address_teacher varchar(255),
    degree varchar(255),
    phone_teacher varchar(255),
    ID_department varchar(255) NOT NULL,
    ID_headquarter varchar(255) NOT NULL,
    CONSTRAINT PK_GiangVien PRIMARY KEY (ID),
    CONSTRAINT FK_GiangVien_Khoa 
        FOREIGN KEY (ID_department) REFERENCES Khoa(ID),
    CONSTRAINT FK_GiangVien_CoSo 
        FOREIGN KEY (ID_headquarter) REFERENCES CoSo(ID)
);

-- 6. BẢNG SINH VIÊN
CREATE TABLE SinhVien (
    ID varchar(255) NOT NULL,
    name_student varchar(255) NOT NULL,
    date_of_birth date,
    address_student varchar(255),
    formal_class varchar(255),
    year_of_admission int,
    phone_student varchar(255),
    ID_department varchar(255) NOT NULL,
    ID_headquarter varchar(255) NOT NULL,
    CONSTRAINT PK_SinhVien PRIMARY KEY (ID),
    CONSTRAINT FK_SinhVien_Khoa 
        FOREIGN KEY (ID_department) REFERENCES Khoa(ID),
    CONSTRAINT FK_SinhVien_CoSo 
        FOREIGN KEY (ID_headquarter) REFERENCES CoSo(ID)
);

-- 7. BẢNG LỚP HỌC PHẦN
CREATE TABLE LopHocPhan (
    ID varchar(255) NOT NULL,
    semester int,
    school_year int,
    number_of_student int DEFAULT 0,
    max_student int NOT NULL,
    shift int,
    ID_subject varchar(255) NOT NULL,
    ID_teacher varchar(255) NOT NULL,
    ID_headquarter varchar(255) NOT NULL,
    CONSTRAINT PK_LopHocPhan PRIMARY KEY (ID),
    CONSTRAINT FK_Lop_HocPhan 
        FOREIGN KEY (ID_subject) REFERENCES HocPhan(ID),
    CONSTRAINT FK_Lop_GiangVien 
        FOREIGN KEY (ID_teacher) REFERENCES GiangVien(ID),
    CONSTRAINT FK_Lop_CoSo 
        FOREIGN KEY (ID_headquarter) REFERENCES CoSo(ID),
    CONSTRAINT CK_LopHocPhan_SiSo 
        CHECK (number_of_student >= 0 AND number_of_student <= max_student)
);

-- 8. BẢNG LỊCH HỌC
CREATE TABLE LichHoc (
    ID varchar(255) NOT NULL,
    ID_class varchar(255) NOT NULL,
    day_of_week int NOT NULL,
    start_period int NOT NULL,
    end_period int NOT NULL,
    ID_room varchar(255) NOT NULL,
    CONSTRAINT PK_LichHoc PRIMARY KEY (ID),
    CONSTRAINT FK_LichHoc_LopHocPhan 
        FOREIGN KEY (ID_class) REFERENCES LopHocPhan(ID),
    CONSTRAINT FK_LichHoc_PhongHoc 
        FOREIGN KEY (ID_room) REFERENCES PhongHoc(ID),
    CONSTRAINT CK_LichHoc_Thu
        CHECK (day_of_week BETWEEN 2 AND 8),
    CONSTRAINT CK_LichHoc_Tiet
        CHECK (start_period > 0 AND end_period >= start_period)
);

-- 9. BẢNG ĐĂNG KÝ
CREATE TABLE DangKy (
    ID_student varchar(255) NOT NULL,
    ID_student_headquarter varchar(255) NOT NULL,
    ID_class varchar(255) NOT NULL,
    registration_date timestamp DEFAULT CURRENT_TIMESTAMP,
    status varchar(50) DEFAULT 'DA_DANG_KY',
    CONSTRAINT PK_DangKy PRIMARY KEY (ID_student, ID_class),
    CONSTRAINT FK_DangKy_CoSoSinhVien 
        FOREIGN KEY (ID_student_headquarter) REFERENCES CoSo(ID),
    CONSTRAINT FK_DangKy_LopHocPhan 
        FOREIGN KEY (ID_class) REFERENCES LopHocPhan(ID),
    CONSTRAINT CK_DangKy_Status
        CHECK (status IN ('DA_DANG_KY', 'DA_HUY'))
);