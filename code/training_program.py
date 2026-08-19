# training_program.py
import customtkinter as ctk

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class TrainingProgramApp(ctk.CTkFrame):
    def __init__(self, parent, db, mssv, ho_ten, theme):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mssv = mssv
        self.ho_ten = ho_ten
        self.theme = theme

        
        # Lấy thông tin ngành của sinh viên hiện tại
        self.id_nganh = self.db.get_student_nganh()
        self.nganh_info = self.db.get_nganh_info() if self.id_nganh else None
        
        # Lấy dữ liệu chương trình đào tạo
        self.program_data = []
        self.completed_subjects = []
        
        if self.id_nganh:
            self.program_data = self.db.get_chuong_trinh_dao_tao()
            self.completed_subjects = self.db.get_completed_subjects()
        
        self.setup_ui()
    
    def c(self, hex_code):
        return self.theme.get(hex_code, hex_code)
    
    def setup_ui(self):
        # Main container
        main_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(30, 10))
        
        ctk.CTkLabel(header, text="CHƯƠNG TRÌNH HỌC", 
                     font=("Garet Variable", 32, "bold"), 
                     text_color=self.c("#3F51B5")).pack(anchor="w")
        
        # Kiểm tra nếu không có ngành
        if not self.id_nganh:
            error_frame = ctk.CTkFrame(main_container, fg_color=self.c("#FFFFFF"), corner_radius=15)
            error_frame.pack(fill="both", expand=True, padx=40, pady=50)
            ctk.CTkLabel(error_frame, text="⚠️ Không tìm thấy thông tin ngành học", 
                         font=("Garet Variable", 18, "bold"), text_color="#E74C3C").pack(expand=True)
            ctk.CTkLabel(error_frame, text="Vui lòng liên hệ phòng đào tạo để cập nhật thông tin ngành.", 
                         font=("Garet Variable", 13), text_color="gray").pack()
            return
        
        # Tên ngành
        if self.nganh_info:
            ten_nganh = self.nganh_info[0] if self.nganh_info[0] else "Chưa cập nhật"
            ctk.CTkLabel(header, text=ten_nganh, 
                         font=("Garet Variable", 20, "bold"), 
                         text_color="#2C3E50").pack(anchor="w", pady=(10, 5))
            
            # Giới thiệu ngành
            if len(self.nganh_info) > 1 and self.nganh_info[1]:
                intro_frame = ctk.CTkFrame(main_container, fg_color=self.c("#FFFFFF"), corner_radius=15)
                intro_frame.pack(fill="x", padx=40, pady=10)
                ctk.CTkLabel(intro_frame, text=self.nganh_info[1], 
                             font=("Garet Variable", 13), wraplength=900, justify="left",
                             padx=20, pady=15).pack()
        
        # Thông tin hệ đào tạo
        info_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        info_frame.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(info_frame, text="Hệ đào tạo: Đại học chính quy (Cử nhân)", 
                     font=("Garet Variable", 13, "bold"), text_color=self.c("#3F51B5")).pack(side="left", padx=(0, 30))
        ctk.CTkLabel(info_frame, text="Chương trình: Chuẩn", 
                     font=("Garet Variable", 13, "bold"), text_color=self.c("#3F51B5")).pack(side="left")
        
        # Bảng dữ liệu
        self.create_table(main_container)
    
    def create_table(self, parent):
        # Khung chứa bảng
        table_container = ctk.CTkFrame(parent, fg_color=self.c("#FFFFFF"), corner_radius=15, 
                                        border_width=1, border_color=self.c("#E0E0E0"))
        table_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        if not self.program_data:
            ctk.CTkLabel(table_container, text="📭 Không có dữ liệu chương trình đào tạo", 
                         font=("Garet Variable", 14), text_color="gray").pack(pady=50)
            return
        
        # Header bảng
        headers = ["Học kỳ", "Loại học phần", "Tên học phần"]
        for col, header in enumerate(headers):
            lbl = ctk.CTkLabel(table_container, text=header, font=("Garet Variable", 14, "bold"),
                               fg_color=self.c("#E9EBF8"), text_color=self.c("#3F51B5"), corner_radius=5,
                               padx=20, pady=10)
            lbl.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Xử lý dữ liệu từ database
        rows_data = []
        for m in self.program_data:
            if len(m) >= 5:
                mon_id, ten_mon, so_tc, hoc_ky, loai_mon = m[0], m[1], m[2], m[3], m[4]
            else:
                mon_id, ten_mon, so_tc, hoc_ky = m[0], m[1], m[2], m[3]
                loai_mon = "Bắt buộc"
            
            rows_data.append({
                "hoc_ky": hoc_ky,
                "loai_mon": loai_mon,
                "ten_mon": ten_mon,
                "so_tc": so_tc,
                "id": mon_id,
                "completed": mon_id in self.completed_subjects
            })
        
        # Sắp xếp theo học kỳ
        rows_data.sort(key=lambda x: x["hoc_ky"])
        
        # Vẽ bảng
        row_idx = 1
        current_ky = None
        
        for i, item in enumerate(rows_data):
            ky = item["hoc_ky"]
            loai = item["loai_mon"]
            ten = item["ten_mon"]
            completed = item["completed"]
            
            text_color = "#A0A0A0" if completed else "#2C3E50"
            font_style = ("Garet Variable", 13, "normal")  # Bỏ overstrike
        
            # Cột Học kỳ
            if ky != current_ky:
                current_ky = ky
                ky_total_credits = sum(item2["so_tc"] for item2 in rows_data if item2["hoc_ky"] == ky)
                ky_label = ctk.CTkLabel(table_container, text=f"Học kỳ {ky}\n({ky_total_credits} TC)",
                                        font=("Garet Variable", 13, "bold"), text_color=self.c("#3F51B5"),
                                        fg_color="#F5F5F5", corner_radius=5)
                ky_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            else:
                empty_label = ctk.CTkLabel(table_container, text="", fg_color=self.c("#F8F9FA"))
                empty_label.grid(row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            
            # Cột Loại học phần
            loai_color = "#2ECC71" if loai == "Bắt buộc" else "#F39C12"
            loai_label = ctk.CTkLabel(table_container, text=loai, font=("Garet Variable", 12, "bold"),
                                      text_color=loai_color, fg_color=self.c("#F8F9FA"), corner_radius=5)
            loai_label.grid(row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            
            # Cột Tên học phần
            ten_text = f"✓ {ten}" if completed else ten
            ten_label = ctk.CTkLabel(table_container, text=ten_text, font=font_style,
                                      text_color=text_color, fg_color=self.c("#F8F9FA"), corner_radius=5,
                                      anchor="w", padx=10)
            ten_label.grid(row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            
            row_idx += 1
        
        # Cấu hình cột
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_columnconfigure(1, weight=1)
        table_container.grid_columnconfigure(2, weight=4)
        
        # Tổng kết
        total_credits = sum(item["so_tc"] for item in rows_data)
        completed_credits = sum(item["so_tc"] for item in rows_data if item["completed"])
        completed_percent = int(completed_credits / total_credits * 100) if total_credits > 0 else 0
        
        summary_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        summary_frame.grid(row=row_idx, column=0, columnspan=3, sticky="ew", pady=15)
        
        ctk.CTkLabel(summary_frame, text=f"📊 Tiến độ hoàn thành: {completed_credits}/{total_credits} tín chỉ ({completed_percent}%)",
                     font=("Garet Variable", 14, "bold"), text_color=self.c("#3F51B5")).pack()
        
        progress_bar = ctk.CTkProgressBar(summary_frame, width=450, height=12, corner_radius=6, progress_color=self.c("#3F51B5"))
        progress_bar.pack(pady=8)
        progress_bar.set(completed_percent / 100 if completed_percent > 0 else 0)
    
    def adjust_layout(self):
        self.update_idletasks()
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()