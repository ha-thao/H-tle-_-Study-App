# database.py
import pyodbc
from datetime import datetime


class Database:
    def __init__(self):
        # Kết nối SQL Server với Windows Authentication
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=CSPROJECT;'
            'Trusted_Connection=yes;'
        )
        self.cursor = self.conn.cursor()
        self.current_mssv = None
        print("✅ Kết nối SQL Server (CSPROJECT) thành công!")
   
    def set_current_user(self, mssv):
        self.current_mssv = mssv

# database.py - CHỈ THÊM CÁC METHOD NÀY VÀO CUỐI FILE, TRƯỚC method close()

    # ========== PHƯƠNG THỨC BỔ SUNG CHO GPA APP ==========
    
    def update_grade_full(self, grade_id, diem_qt, diem_ck, heso_qt, heso_ck):
        """Cập nhật điểm và hệ số"""
        try:
            self.cursor.execute("""
                UPDATE BANGDIEM 
                SET DIEM_QT = ?, DIEM_CK = ?, HESO_QT = ?, HESO_CK = ?
                WHERE ID_DIEM = ? AND MSSV = ?
            """, (diem_qt, diem_ck, heso_qt, heso_ck, grade_id, self.current_mssv))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi update_grade_full: {e}")
            return False
    

    # ========== ĐĂNG NHẬP / ĐĂNG KÝ ==========
    def login(self, email_or_mssv, password):
        self.cursor.execute("""
            SELECT MSSV, HO_TEN, EMAIL, ID_NGANH
            FROM SINHVIEN
            WHERE (EMAIL = ? OR MSSV = ?) AND MATKHAU = ?
        """, (email_or_mssv, email_or_mssv, password))
        return self.cursor.fetchone()
   
    def check_mssv_exists(self, mssv):
        self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE MSSV = ?", (mssv,))
        return self.cursor.fetchone()[0] > 0
   
    def check_email_exists(self, email):
        self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE EMAIL = ?", (email,))
        return self.cursor.fetchone()[0] > 0
   
    def register(self, mssv, ho_ten, email, password, id_nganh):
        try:
            self.cursor.execute("SELECT EMAIL, MATKHAU FROM SINHVIEN WHERE MSSV = ?", (mssv,))
            user = self.cursor.fetchone()


            if user:
                if user[0] is not None or user[1] is not None:
                    return False, "Tài khoản này đã được đăng ký trước đó!"
               
                self.cursor.execute("""
                    UPDATE SINHVIEN
                    SET EMAIL = ?, MATKHAU = ?, HO_TEN = ?, ID_NGANH = ?
                    WHERE MSSV = ?
                """, (email, password, ho_ten, id_nganh, mssv))
                self.conn.commit()
                return True, "Đăng ký tài khoản thành công!"
            else:
                return False, "MSSV không tồn tại trong danh sách sinh viên!"
        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"
   
    def get_nganh_list(self):
        self.cursor.execute("SELECT ID_NGANH, TEN_NGANH FROM NGANHHOC")
        return self.cursor.fetchall()
   
    # ========== MÔN HỌC ==========
    def get_subject_id_by_name(self, subject_name):
        """Lấy ID môn học từ tên môn"""
        try:
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Lỗi get_subject_id_by_name: {e}")
            return None
        
    def get_subjects_by_student(self):
        self.cursor.execute("""
            SELECT DISTINCT m.ID_MON, m.TEN_MON, m.SO_TIN_CHI
            FROM BANGDIEM bd
            JOIN MONHOC m ON bd.ID_MON = m.ID_MON
            WHERE bd.MSSV = ?
            ORDER BY m.TEN_MON
        """, (self.current_mssv,))
        return self.cursor.fetchall()
   
    def get_subjects_by_program(self):
        id_nganh = self.get_student_nganh()
        if not id_nganh:
            return []
        self.cursor.execute("""
            SELECT m.ID_MON, m.TEN_MON, m.SO_TIN_CHI, ct.HOC_KY_DU_KIEN, ct.LOAI_MON
            FROM CHUONGTRINH_DAOTAO ct
            JOIN MONHOC m ON ct.ID_MON = m.ID_MON
            WHERE ct.ID_NGANH = ?
            ORDER BY ct.HOC_KY_DU_KIEN
        """, (id_nganh,))
        return self.cursor.fetchall()
   
    def add_subject(self, subject_name, hoc_ky=1):
        id_nganh = self.get_student_nganh()
        self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
        exist = self.cursor.fetchone()
        if exist:
            subject_id = exist[0]
        else:
            import time
            subject_id = f"MON{int(time.time())}"
            self.cursor.execute("""
                INSERT INTO MONHOC (ID_MON, TEN_MON, SO_TIN_CHI)
                VALUES (?, ?, 3)
            """, (subject_id, subject_name))
            self.conn.commit()
       
        self.cursor.execute("""
            SELECT COUNT(*) FROM CHUONGTRINH_DAOTAO
            WHERE ID_NGANH = ? AND ID_MON = ?
        """, (id_nganh, subject_id))
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("""
                INSERT INTO CHUONGTRINH_DAOTAO (ID_NGANH, ID_MON, HOC_KY_DU_KIEN, LOAI_MON)
                VALUES (?, ?, ?, 'Tự chọn')
            """, (id_nganh, subject_id, hoc_ky))
            self.conn.commit()
        return subject_id
   
    def update_grade(self, grade_id, diem_qt, diem_ck):
        """Cập nhật điểm (giữ nguyên hệ số)"""
        try:
            self.cursor.execute("""
                UPDATE BANGDIEM SET DIEM_QT = ?, DIEM_CK = ?
                WHERE ID_DIEM = ? AND MSSV = ?
            """, (diem_qt, diem_ck, grade_id, self.current_mssv))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi update_grade: {e}")
            return False
   
    def delete_grade(self, grade_id):
        self.cursor.execute("DELETE FROM BANGDIEM WHERE ID_DIEM = ? AND MSSV = ?", (grade_id, self.current_mssv))
        self.conn.commit()
   
    # ========== TÀI LIỆU ==========
    def get_file_path(self, file_id):
        self.cursor.execute("SELECT FILE_PATH FROM TAILIEU WHERE ID_FILE = ?", (file_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None


    def get_files(self, subject_name):
        """Lấy danh sách file theo tên môn"""
        try:
            # Lấy ID_MON từ tên môn
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Không tìm thấy ID_MON cho môn: {subject_name}")
                return []
            id_mon = result[0]
           
            self.cursor.execute("""
                SELECT ID_FILE, TEN_FILE, LOAI_FILE, NGAY_THEM_TL, FILE_PATH
                FROM TAILIEU
                WHERE MSSV = ? AND ID_MON = ?
                ORDER BY NGAY_THEM_TL DESC
            """, (self.current_mssv, id_mon))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi get_files: {e}")
            return []
   
    def add_file(self, id_mon, ten_file, loai_file, file_path):
        """Thêm tài liệu vào database"""
        try:
            self.cursor.execute("""
                INSERT INTO TAILIEU (MSSV, ID_MON, TEN_FILE, LOAI_FILE, NGAY_THEM_TL, FILE_PATH)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            """, (self.current_mssv, id_mon, ten_file, loai_file, file_path))
            self.conn.commit()
           
            # Dùng @@IDENTITY thay vì SCOPE_IDENTITY()
            self.cursor.execute("SELECT @@IDENTITY")
            new_id = self.cursor.fetchone()[0]
            print(f"Thêm file thành công, ID={new_id}")
            return new_id
        except Exception as e:
            print(f"Lỗi add_file chi tiết: {e}")
            return None
   
    # ========== GHI CHÚ ==========
    def get_notes(self, subject_name):
        """Lấy danh sách ghi chú theo tên môn"""
        try:
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
            result = self.cursor.fetchone()
            if not result:
                return []
            id_mon = result[0]
           
            self.cursor.execute("""
                SELECT ID_NOTE, TEN_NOTE, NOIDUNG, NGAY_THEM_NOTE
                FROM GHICHU
                WHERE MSSV = ? AND ID_MON = ?
                ORDER BY NGAY_THEM_NOTE DESC
            """, (self.current_mssv, id_mon))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi get_notes: {e}")
            return []
       
    def add_note(self, subject_name, title, content):
        """Thêm ghi chú vào bảng GHICHU"""
        try:
            # Lấy ID_MON từ tên môn
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Không tìm thấy môn: {subject_name}")
                return None
           
            id_mon = result[0]
           
            self.cursor.execute("""
                INSERT INTO GHICHU (MSSV, ID_MON, TEN_NOTE, NOIDUNG, NGAY_THEM_NOTE)
                VALUES (?, ?, ?, ?, GETDATE())
            """, (self.current_mssv, id_mon, title, content))
            self.conn.commit()
           
            # Cách lấy ID đúng cho pyodbc
            self.cursor.execute("SELECT @@IDENTITY as id")
            new_id = self.cursor.fetchone()[0]
            print(f"Thêm ghi chú thành công, ID: {new_id}")
            return new_id
        except Exception as e:
            print(f"Lỗi add_note: {e}")
            return None
       
    def delete_file(self, file_id):
        """Xóa tài liệu khỏi database"""
        try:
            self.cursor.execute("DELETE FROM TAILIEU WHERE ID_FILE = ? AND MSSV = ?", (file_id, self.current_mssv))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi delete_file: {e}")
            return False
   
    def update_note(self, note_id, title, content):
        self.cursor.execute("""
            UPDATE GHICHU SET TEN_NOTE = ?, NOIDUNG = ?
            WHERE ID_NOTE = ? AND MSSV = ?
        """, (title, content, note_id, self.current_mssv))
        self.conn.commit()
   
    def delete_note(self, note_id):
        self.cursor.execute("DELETE FROM GHICHU WHERE ID_NOTE = ? AND MSSV = ?", (note_id, self.current_mssv))
        self.conn.commit()
   
    # ========== GPA ==========
    def calculate_gpa(self):
        self.cursor.execute("""
            SELECT
                SUM(( (DIEM_QT * HESO_QT + DIEM_CK * HESO_CK) / (HESO_QT + HESO_CK) * m.SO_TIN_CHI )) as tong_diem,
                SUM(m.SO_TIN_CHI) as tong_tc
            FROM BANGDIEM bd
            JOIN MONHOC m ON bd.ID_MON = m.ID_MON
            WHERE bd.MSSV = ?
        """, (self.current_mssv,))
        result = self.cursor.fetchone()
        if result and result[1] and result[1] > 0:
            return round(result[0] / result[1], 2)
        return 0.0
   
    def get_gpa_target(self):
        self.cursor.execute("SELECT GPA_TARGET FROM MUCTIEUDIEM WHERE MSSV = ?", (self.current_mssv,))
        result = self.cursor.fetchone()
        return result[0] if result else 3.5
   
    def set_gpa_target(self, target):
        self.cursor.execute("SELECT ID_TARGET FROM MUCTIEUDIEM WHERE MSSV = ?", (self.current_mssv,))
        exists = self.cursor.fetchone()
        if exists:
            self.cursor.execute("UPDATE MUCTIEUDIEM SET GPA_TARGET = ? WHERE MSSV = ?", (target, self.current_mssv))
        else:
            self.cursor.execute("INSERT INTO MUCTIEUDIEM (MSSV, GPA_TARGET) VALUES (?, ?)", (self.current_mssv, target))
        self.conn.commit()
   
    # ========== CHƯƠNG TRÌNH ĐÀO TẠO ==========
    def get_student_nganh(self):
        self.cursor.execute("SELECT ID_NGANH FROM SINHVIEN WHERE MSSV = ?", (self.current_mssv,))
        result = self.cursor.fetchone()
        return result[0] if result else None
   
    def get_student_nganh_name(self):
        self.cursor.execute("""
            SELECT nh.TEN_NGANH
            FROM SINHVIEN sv
            JOIN NGANHHOC nh ON sv.ID_NGANH = nh.ID_NGANH
            WHERE sv.MSSV = ?
        """, (self.current_mssv,))
        result = self.cursor.fetchone()
        return result[0] if result else "Chưa xác định"
   
    def get_chuong_trinh_dao_tao(self):
        """Lấy chương trình đào tạo theo ngành của sinh viên"""
        id_nganh = self.get_student_nganh()
        if not id_nganh:
            return []
        self.cursor.execute("""
            SELECT m.ID_MON, m.TEN_MON, m.SO_TIN_CHI, ct.HOC_KY_DU_KIEN, ct.LOAI_MON
            FROM CHUONGTRINH_DAOTAO ct
            JOIN MONHOC m ON ct.ID_MON = m.ID_MON
            WHERE ct.ID_NGANH = ?
            ORDER BY ct.HOC_KY_DU_KIEN, m.TEN_MON
        """, (id_nganh,))
        return self.cursor.fetchall()
   
    def get_completed_subjects(self):
        self.cursor.execute("SELECT DISTINCT ID_MON FROM BANGDIEM WHERE MSSV = ?", (self.current_mssv,))
        return [row[0] for row in self.cursor.fetchall()]
   
    def get_nganh_info(self):
        id_nganh = self.get_student_nganh()
        if not id_nganh:
            return None
        self.cursor.execute("SELECT TEN_NGANH, GIOI_THIEU, CHUAN_DAU_RA FROM NGANHHOC WHERE ID_NGANH = ?", (id_nganh,))
        return self.cursor.fetchone()
   
    # ========== CHECKLIST ==========
    def get_checklist(self):
        """Lấy danh sách checklist (có cả HOAN_THANH)"""
        self.cursor.execute("""
            SELECT ID_CHECK, DANH_MUC, TEN_MUC_TIEU, KETQUA, HOAN_THANH
            FROM CHECKLIST
            WHERE MSSV = ?
            ORDER BY DANH_MUC
        """, (self.current_mssv,))
        return self.cursor.fetchall()
   
    def add_checklist_item(self, danh_muc, ten_muc_tieu):
        """Thêm mục tiêu mới (mặc định chưa hoàn thành)"""
        self.cursor.execute("""
            INSERT INTO CHECKLIST (MSSV, DANH_MUC, TEN_MUC_TIEU, HOAN_THANH)
            VALUES (?, ?, ?, 0)
        """, (self.current_mssv, danh_muc, ten_muc_tieu))
        self.conn.commit()
        return self.cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()
   
    def update_checklist_result(self, check_id, ketqua, hoan_thanh=None):
        """Cập nhật kết quả và trạng thái hoàn thành"""
        if hoan_thanh is not None:
            self.cursor.execute("""
                UPDATE CHECKLIST SET KETQUA = ?, HOAN_THANH = ?
                WHERE ID_CHECK = ? AND MSSV = ?
            """, (ketqua, hoan_thanh, check_id, self.current_mssv))
        else:
            self.cursor.execute("""
                UPDATE CHECKLIST SET KETQUA = ?
                WHERE ID_CHECK = ? AND MSSV = ?
            """, (ketqua, check_id, self.current_mssv))
        self.conn.commit()


    def delete_checklist_item(self, check_id):
        self.cursor.execute("DELETE FROM CHECKLIST WHERE ID_CHECK = ? AND MSSV = ?", (check_id, self.current_mssv))
        self.conn.commit()
   
    # ========== ĐẶT PHÒNG LAB ==========
    def get_my_bookings(self):
        self.cursor.execute("""
            SELECT ID_BOOKING, NGAY_DAT, KHUNG_GIO, SO_THANH_VIEN, DS_TV, TRANGTHAI, BOOKING_CODE
            FROM DATPHONGLAB
            WHERE MSSV = ?
            ORDER BY NGAY_DAT DESC
        """, (self.current_mssv,))
        return self.cursor.fetchall()
   
    def check_available_lab(self, ngay_dat, khung_gio):
        self.cursor.execute("""
            SELECT COUNT(*) FROM DATPHONGLAB
            WHERE NGAY_DAT = ? AND KHUNG_GIO = ? AND TRANGTHAI = 1
        """, (ngay_dat, khung_gio))
        result = self.cursor.fetchone()
        return result[0] == 0 if result else True
   
    def add_booking(self, ngay_dat, khung_gio, so_thanh_vien, ds_tv, booking_code=None):
        """Thêm đặt phòng (ID tự động, lưu thêm mã booking_code)"""
        try:
            if booking_code:
                self.cursor.execute("""
                    INSERT INTO DATPHONGLAB (MSSV, NGAY_DAT, KHUNG_GIO, SO_THANH_VIEN, DS_TV, TRANGTHAI, BOOKING_CODE)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (self.current_mssv, ngay_dat, khung_gio, so_thanh_vien, ds_tv, booking_code))
            else:
                self.cursor.execute("""
                    INSERT INTO DATPHONGLAB (MSSV, NGAY_DAT, KHUNG_GIO, SO_THANH_VIEN, DS_TV, TRANGTHAI)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (self.current_mssv, ngay_dat, khung_gio, so_thanh_vien, ds_tv))
            self.conn.commit()
            self.cursor.execute("SELECT @@IDENTITY")
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Lỗi add_booking: {e}")
            return None
   
    def cancel_booking(self, booking_id):
        self.cursor.execute("""
            UPDATE DATPHONGLAB SET TRANGTHAI = 0 WHERE ID_BOOKING = ? AND MSSV = ?
        """, (booking_id, self.current_mssv))
        self.conn.commit()
   
    # ========== THÔNG TIN SINH VIÊN ==========
    def get_student_info(self):
        self.cursor.execute("""
            SELECT sv.MSSV, sv.HO_TEN, sv.EMAIL, nh.TEN_NGANH
            FROM SINHVIEN sv
            JOIN NGANHHOC nh ON sv.ID_NGANH = nh.ID_NGANH
            WHERE sv.MSSV = ?
        """, (self.current_mssv,))
        return self.cursor.fetchone()
   
    # ========== QUẢN LÝ HỌC KỲ (CHO MODULE LỚP HỌC) ==========
    def get_all_semesters(self):
        """Lấy danh sách các học kỳ từ chương trình đào tạo của sinh viên"""
        try:
            id_nganh = self.get_student_nganh()
            if not id_nganh:
                return []
           
            self.cursor.execute("""
                SELECT DISTINCT
                    HOC_KY_DU_KIEN as hoc_ky,
                    CONCAT('Học kỳ ', HOC_KY_DU_KIEN) as ten_hoc_ky
                FROM CHUONGTRINH_DAOTAO
                WHERE ID_NGANH = ?
                ORDER BY HOC_KY_DU_KIEN
            """, (id_nganh,))
           
            results = self.cursor.fetchall()
            semesters = []
            for idx, row in enumerate(results, 1):
                semesters.append({
                    'id_hoc_ky': idx,
                    'hoc_ky': row[0],
                    'ten_hoc_ky': row[1]
                })
            return semesters
        except Exception as e:
            print(f"Lỗi get_all_semesters: {e}")
            return []


    def get_courses_by_semester(self, hoc_ky):
        """Lấy môn học: Dùng Marker Subject để nhận diện học kỳ đã khởi tạo"""
        try:
            id_nganh = self.get_student_nganh()
            if not id_nganh: return []

            # 1. Kiểm tra xem 'Môn học đánh dấu' đã có trong kỳ này chưa
            self.cursor.execute("""
                SELECT COUNT(*) FROM SINHVIEN_MON 
                WHERE MSSV = ? AND HOC_KY = ? AND ID_MON = 'START_MARKER'
            """, (self.current_mssv, hoc_ky))
            
            if self.cursor.fetchone()[0] == 0:
                # 2. Nếu CHƯA CÓ: Nạp môn ngành và chèn thêm mốc 'START_MARKER'
                self.cursor.execute("""
                    INSERT INTO SINHVIEN_MON (MSSV, ID_MON, HOC_KY)
                    SELECT ?, ID_MON, HOC_KY_DU_KIEN 
                    FROM CHUONGTRINH_DAOTAO 
                    WHERE ID_NGANH = ? AND HOC_KY_DU_KIEN = ?
                """, (self.current_mssv, id_nganh, hoc_ky))
                
                # Chèn cái mốc để lần sau không nạp lại nữa
                self.cursor.execute("""
                    INSERT INTO SINHVIEN_MON (MSSV, ID_MON, HOC_KY) 
                    VALUES (?, 'START_MARKER', ?)
                """, (self.current_mssv, hoc_ky))
                self.conn.commit()

            # 3. Load danh sách nhưng LOẠI BỎ cái mốc này ra để không hiện lên UI
            self.cursor.execute("""
                SELECT m.ID_MON, m.TEN_MON, m.SO_TIN_CHI, 
                       'Personal' as LOAI_MON,
                       CASE WHEN bd.ID_MON IS NOT NULL THEN 1 ELSE 0 END as DA_HOC,
                       NULL as DIEM_TB
                FROM SINHVIEN_MON sm
                JOIN MONHOC m ON sm.ID_MON = m.ID_MON
                LEFT JOIN BANGDIEM bd ON bd.ID_MON = m.ID_MON AND bd.MSSV = ?
                WHERE sm.MSSV = ? AND sm.HOC_KY = ? AND m.ID_MON != 'START_MARKER' -- Lọc mốc ra ở đây
                ORDER BY m.TEN_MON
            """, (self.current_mssv, self.current_mssv, hoc_ky))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi load môn học: {e}")
            return []

    def add_subject(self, subject_name, hoc_ky=1):
        """Thêm môn mới - CHỈ thêm vào bảng cá nhân SINHVIEN_MON"""
        try:
            # Kiểm tra môn có trong danh mục chung chưa
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (subject_name,))
            exist = self.cursor.fetchone()
            if exist:
                subject_id = exist[0]
            else:
                import time
                subject_id = f"MON{int(time.time())}"
                self.cursor.execute("INSERT INTO MONHOC (ID_MON, TEN_MON, SO_TIN_CHI) VALUES (?, ?, 3)", 
                                    (subject_id, subject_name))
            
            # CHỈ lưu vào bảng cá nhân (Không làm rác bảng CTĐT của trường)
            self.cursor.execute("""
                IF NOT EXISTS (SELECT * FROM SINHVIEN_MON WHERE MSSV=? AND ID_MON=? AND HOC_KY=?)
                INSERT INTO SINHVIEN_MON (MSSV, ID_MON, HOC_KY) VALUES (?, ?, ?)
            """, (self.current_mssv, subject_id, hoc_ky, self.current_mssv, subject_id, hoc_ky))
            self.conn.commit()
            return subject_id
        except Exception as e:
            print(f"Lỗi add_subject: {e}")
            return None

    def delete_student_subject_by_name(self, subject_name, hoc_ky):
        """Hàm xóa môn theo tên - phục vụ nút 'x' trên folder"""
        try:
            id_mon = self.get_subject_id_by_name(subject_name)
            if id_mon:
                self.cursor.execute("DELETE FROM SINHVIEN_MON WHERE MSSV = ? AND ID_MON = ? AND HOC_KY = ?", 
                                    (self.current_mssv, id_mon, hoc_ky))
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi xóa môn: {e}")
            return False


    def get_student_courses_with_grades(self):
        """Lấy danh sách môn học đã học kèm điểm chi tiết"""
        try:
            self.cursor.execute("""
                SELECT
                    bd.ID_DIEM,
                    m.ID_MON,
                    m.TEN_MON,
                    m.SO_TIN_CHI,
                    bd.KY_HOC_THUC_TE as hoc_ky,
                    ISNULL(bd.NAM_HOC, '2024-2025') as nam_hoc,
                    bd.DIEM_QT,
                    bd.HESO_QT,
                    bd.DIEM_CK,
                    bd.HESO_CK,
                    CASE
                        WHEN bd.DIEM_QT IS NOT NULL AND bd.DIEM_CK IS NOT NULL
                        THEN (bd.DIEM_QT * bd.HESO_QT + bd.DIEM_CK * bd.HESO_CK) / (bd.HESO_QT + bd.HESO_CK)
                        ELSE NULL
                    END as DIEM_TB
                FROM BANGDIEM bd
                JOIN MONHOC m ON bd.ID_MON = m.ID_MON
                WHERE bd.MSSV = ?
                ORDER BY bd.NAM_HOC DESC, bd.KY_HOC_THUC_TE DESC
            """, (self.current_mssv,))
           
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi get_student_courses_with_grades: {e}")
            return []


    def get_all_grade_conversion(self):
        """Bảng quy đổi điểm thang 10 sang thang 4 và điểm chữ"""
        return [
            {'min': 9.0, 'max': 10.0, 'thang_4': 4.0, 'diem_chu': 'A+', 'xep_loai': 'Xuất sắc'},
            {'min': 8.5, 'max': 8.9, 'thang_4': 4.0, 'diem_chu': 'A', 'xep_loai': 'Xuất sắc'},
            {'min': 8.0, 'max': 8.4, 'thang_4': 3.5, 'diem_chu': 'B+', 'xep_loai': 'Giỏi'},
            {'min': 7.0, 'max': 7.9, 'thang_4': 3.0, 'diem_chu': 'B', 'xep_loai': 'Giỏi'},
            {'min': 6.5, 'max': 6.9, 'thang_4': 2.5, 'diem_chu': 'C+', 'xep_loai': 'Khá'},
            {'min': 5.5, 'max': 6.4, 'thang_4': 2.0, 'diem_chu': 'C', 'xep_loai': 'Khá'},
            {'min': 5.0, 'max': 5.4, 'thang_4': 1.5, 'diem_chu': 'D+', 'xep_loai': 'Trung bình'},
            {'min': 4.0, 'max': 4.9, 'thang_4': 1.0, 'diem_chu': 'D', 'xep_loai': 'Trung bình'},
            {'min': 3.0, 'max': 3.9, 'thang_4': 0.5, 'diem_chu': 'F+', 'xep_loai': 'Yếu'},
            {'min': 0.0, 'max': 2.9, 'thang_4': 0.0, 'diem_chu': 'F', 'xep_loai': 'Yếu'},
        ]


    def convert_grade(self, diem_tb):
        """Chuyển đổi điểm thang 10 sang thang 4 và điểm chữ"""
        if diem_tb is None:
            return {'thang_4': 0.0, 'diem_chu': 'F', 'xep_loai': 'Chưa có điểm'}
       
        for g in self.get_all_grade_conversion():
            if g['min'] <= diem_tb <= g['max']:
                return {'thang_4': g['thang_4'], 'diem_chu': g['diem_chu'], 'xep_loai': g['xep_loai']}
       
        return {'thang_4': 0.0, 'diem_chu': 'F', 'xep_loai': 'Yếu'}


    def get_semester_gpa_list(self):
        """Tính GPA theo từng học kỳ"""
        try:
            self.cursor.execute("""
                SELECT
                    bd.KY_HOC_THUC_TE as hoc_ky,
                    ISNULL(bd.NAM_HOC, '2024-2025') as nam_hoc,
                    SUM(m.SO_TIN_CHI) as tong_tin_chi,
                    SUM(
                        ISNULL(((bd.DIEM_QT * bd.HESO_QT + bd.DIEM_CK * bd.HESO_CK) / (bd.HESO_QT + bd.HESO_CK)) * m.SO_TIN_CHI, 0)
                    ) as tong_diem,
                    COUNT(*) as so_mon
                FROM BANGDIEM bd
                JOIN MONHOC m ON bd.ID_MON = m.ID_MON
                WHERE bd.MSSV = ? AND bd.DIEM_QT IS NOT NULL AND bd.DIEM_CK IS NOT NULL
                GROUP BY bd.KY_HOC_THUC_TE, bd.NAM_HOC
                ORDER BY bd.NAM_HOC, bd.KY_HOC_THUC_TE
            """, (self.current_mssv,))
           
            results = self.cursor.fetchall()
            gpa_list = []
            for row in results:
                gpa = round(row[3] / row[2], 2) if row[2] and row[2] > 0 else 0
                gpa_list.append({
                    'hoc_ky': row[0],
                    'nam_hoc': row[1],
                    'tong_tin_chi': row[2],
                    'gpa': gpa,
                    'so_mon': row[4]
                })
            return gpa_list
        except Exception as e:
            print(f"Lỗi get_semester_gpa_list: {e}")
            return []


    # ========== PHƯƠNG THỨC CHO GPA APP ==========
    def get_grades(self, hoc_ky=None, nam_hoc=None):
        """Lấy danh sách điểm chi tiết (có ID_DIEM)"""
        if hoc_ky and nam_hoc:
            self.cursor.execute("""
                SELECT bd.ID_DIEM, m.TEN_MON, m.SO_TIN_CHI,
                    bd.DIEM_QT, bd.DIEM_CK, bd.HESO_QT, bd.HESO_CK,
                    bd.KY_HOC_THUC_TE, bd.NAM_HOC
                FROM BANGDIEM bd
                JOIN MONHOC m ON bd.ID_MON = m.ID_MON
                WHERE bd.MSSV = ? AND bd.KY_HOC_THUC_TE = ? AND bd.NAM_HOC = ?
                ORDER BY bd.KY_HOC_THUC_TE, m.TEN_MON
            """, (self.current_mssv, hoc_ky, nam_hoc))
        elif hoc_ky:
            self.cursor.execute("""
                SELECT bd.ID_DIEM, m.TEN_MON, m.SO_TIN_CHI,
                    bd.DIEM_QT, bd.DIEM_CK, bd.HESO_QT, bd.HESO_CK,
                    bd.KY_HOC_THUC_TE, bd.NAM_HOC
                FROM BANGDIEM bd
                JOIN MONHOC m ON bd.ID_MON = m.ID_MON
                WHERE bd.MSSV = ? AND bd.KY_HOC_THUC_TE = ?
                ORDER BY m.TEN_MON
            """, (self.current_mssv, hoc_ky))
        else:
            self.cursor.execute("""
                SELECT bd.ID_DIEM, m.TEN_MON, m.SO_TIN_CHI,
                    bd.DIEM_QT, bd.DIEM_CK, bd.HESO_QT, bd.HESO_CK,
                    bd.KY_HOC_THUC_TE, bd.NAM_HOC
                FROM BANGDIEM bd
                JOIN MONHOC m ON bd.ID_MON = m.ID_MON
                WHERE bd.MSSV = ?
                ORDER BY bd.NAM_HOC DESC, bd.KY_HOC_THUC_TE DESC, m.TEN_MON
            """, (self.current_mssv,))
        return self.cursor.fetchall()


    def add_grade(self, id_mon, diem_qt, diem_ck, heso_qt, heso_ck, hoc_ky, ten_mon=None, so_tin_chi=3, nam_hoc="2024-2025"):
        """Thêm bảng điểm mới"""
        try:
            # Nếu có tên môn và không có id_mon, tạo môn mới
            if ten_mon and not id_mon:
                self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TEN_MON = ?", (ten_mon,))
                exist = self.cursor.fetchone()
                if exist:
                    id_mon = exist[0]
                else:
                    import time
                    id_mon = f"MON{int(time.time())}"
                    self.cursor.execute("""
                        INSERT INTO MONHOC (ID_MON, TEN_MON, SO_TIN_CHI)
                        VALUES (?, ?, ?)
                    """, (id_mon, ten_mon, so_tin_chi))
                    self.conn.commit()
           
            if id_mon:
                self.cursor.execute("""
                    INSERT INTO BANGDIEM (MSSV, ID_MON, KY_HOC_THUC_TE, NAM_HOC, DIEM_QT, HESO_QT, DIEM_CK, HESO_CK)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (self.current_mssv, id_mon, hoc_ky, nam_hoc, diem_qt, heso_qt, diem_ck, heso_ck))
                self.conn.commit()
                print(f"Thêm điểm thành công cho môn: {ten_mon}")
                return True
            return False
        except Exception as e:
            print(f"Lỗi add_grade: {e}")
            return False
        
    # Thêm vào database.py (trước method close)

    def load_all_targets(self):
        """Tải tất cả mục tiêu GPA theo học kỳ (chỉ lấy những kỳ đã nhập)"""
        try:
            self.cursor.execute("""
                SELECT HOC_KY, GPA_TARGET FROM MUCTIEU_HOCKY
                WHERE MSSV = ? AND GPA_TARGET IS NOT NULL
            """, (self.current_mssv,))
            results = self.cursor.fetchall()
            targets = {}
            for row in results:
                targets[row[0]] = row[1]
            return targets
        except Exception as e:
            print(f"Lỗi load_all_targets: {e}")
            return {}

    def set_target_by_semester(self, hoc_ky, gpa_target):
        """Cập nhật mục tiêu GPA theo học kỳ"""
        try:
            if gpa_target is None:
                # Xóa mục tiêu
                self.cursor.execute("""
                    DELETE FROM MUCTIEU_HOCKY
                    WHERE MSSV = ? AND HOC_KY = ?
                """, (self.current_mssv, hoc_ky))
            else:
                self.cursor.execute("""
                    UPDATE MUCTIEU_HOCKY SET GPA_TARGET = ?
                    WHERE MSSV = ? AND HOC_KY = ?
                """, (gpa_target, self.current_mssv, hoc_ky))
                if self.cursor.rowcount == 0:
                    self.cursor.execute("""
                        INSERT INTO MUCTIEU_HOCKY (MSSV, HOC_KY, GPA_TARGET)
                        VALUES (?, ?, ?)
                    """, (self.current_mssv, hoc_ky, gpa_target))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi set_target_by_semester: {e}")
            return False
    
    # ========== ĐÓNG KẾT NỐI ==========
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("🔌 Đã đóng kết nối database")