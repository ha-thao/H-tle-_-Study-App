# gpa_app.py - ĐÃ SỬA LỖI FONT + BẢNG PHAO CỨU SINH THEO EXCEL
import customtkinter as ctk
from tkinter import messagebox, Toplevel
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class GPAApp(ctk.CTkFrame):
    def __init__(self, parent, db, mssv, ho_ten, theme):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mssv = mssv
        self.ho_ten = ho_ten
        self.theme = theme

        
        self.bg_color = "#FDF6E3"
        self.accent_color = self.c("#3F51B5")
        self.card_color = "#FFFFFF"
        
        self.gpa_subjects = []
        self.target_gpa_by_semester = self.db.load_all_targets()
        self.long_term_target_gpa = 3.7
        self.filter_ky = 1
        self.current_gpa_view = "dashboard"
        self.next_id = 1
        
        self.semester_var = ctk.StringVar(value="Học kỳ 1")
        
        self.load_grades()
        self.setup_ui()

    def c(self, hex_code):
        return self.theme.get(hex_code, hex_code)
    
    def load_grades(self):
        """Tải dữ liệu điểm từ database"""
        grades = self.db.get_grades()
        self.gpa_subjects = []
        max_id = 0
        for grade in grades:
            if len(grade) >= 9:
                # (id_diem, ten_mon, so_tin_chi, diem_qt, diem_ck, heso_qt, heso_ck, hoc_ky, nam_hoc)
                id_diem, ten_mon, tin_chi, diem_qt, diem_ck, heso_qt, heso_ck, hoc_ky, nam_hoc = grade[:9]
                self.gpa_subjects.append({
                    "id": id_diem,
                    "name": ten_mon,
                    "ky": hoc_ky,
                    "tc": tin_chi,
                    "dqt": diem_qt if diem_qt else 0,
                    "dck": diem_ck if diem_ck else 0,
                    "hs_qt": heso_qt if heso_qt else 0.5,
                    "hs_ck": heso_ck if heso_ck else 0.5,
                    "nam_hoc": nam_hoc
                })
                if id_diem > max_id:
                    max_id = id_diem
        self.next_id = max_id + 1
    
    def compute_diem_tb(self, dqt, dck, hs_qt, hs_ck):
        """Tính điểm trung bình môn (thang 10)"""
        tong_heso = hs_qt + hs_ck
        if tong_heso == 0:
            return 0
        return (dqt * hs_qt + dck * hs_ck) / tong_heso
    
    def diem_thang4(self, diem_tb):
        """Quy đổi điểm thang 10 sang thang 4 và điểm chữ"""
        if diem_tb >= 9.0:
            return 4.0, "A+"
        elif diem_tb >= 8.5:
            return 4.0, "A"
        elif diem_tb >= 8.0:
            return 3.5, "B+"
        elif diem_tb >= 7.0:
            return 3.0, "B"
        elif diem_tb >= 6.5:
            return 2.5, "C+"
        elif diem_tb >= 5.5:
            return 2.0, "C"
        elif diem_tb >= 5.0:
            return 1.5, "D+"
        elif diem_tb >= 4.0:
            return 1.0, "D"
        elif diem_tb >= 3.0:
            return 0.5, "F+"
        else:
            return 0.0, "F"
    
    def get_xep_loai(self, gpa):
        """Xếp loại theo GPA"""
        if gpa >= 3.6:
            return "Xuất sắc"
        elif gpa >= 3.2:
            return "Giỏi"
        elif gpa >= 2.5:
            return "Khá"
        elif gpa >= 2.0:
            return "Trung bình"
        else:
            return "Yếu"
    
    def get_total_credits(self, ky=None):
        """Lấy tổng tín chỉ"""
        total = 0
        for s in self.gpa_subjects:
            if ky is None or s["ky"] == ky:
                total += s["tc"]
        return total
    
    def compute_gpa_by_semester(self, ky=None):
        """Tính GPA theo học kỳ (thang 4)"""
        total_credits = 0
        total_weighted = 0.0
        for s in self.gpa_subjects:
            if ky is None or s["ky"] == ky:
                diem_tb = self.compute_diem_tb(s["dqt"], s["dck"], s["hs_qt"], s["hs_ck"])
                diem_4, _ = self.diem_thang4(diem_tb)
                total_credits += s["tc"]
                total_weighted += diem_4 * s["tc"]
        return round(total_weighted / total_credits, 2) if total_credits > 0 else 0.0
    
    def setup_ui(self):
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(fill="both", expand=True)
        self.render_gpa_view()
    
    def render_gpa_view(self):
        for w in self.main_view.winfo_children():
            w.destroy()
        
        header = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 10))
        
        ctk.CTkLabel(header, text="THEO DÕI GPA", font=("Garet Variable", 32, "bold"), 
                     text_color=self.accent_color).pack(side="left", padx=10)
        
        tab_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        tab_frame.pack(fill="x", padx=40, pady=10)
        
        tabs = [
            ("📈 Dashboard", "dashboard"),
            ("📋 Kết quả học kỳ", "ketqua_hocky"),
            ("📝 Bảng điểm", "bangdiem_hocky"),
            ("🆘 Phao cứu sinh", "phaocuu_sinh")
        ]
        
        for text, key in tabs:
            active = (self.current_gpa_view == key)
            btn = ctk.CTkButton(tab_frame, text=text,
                                fg_color=self.accent_color if active else "white",
                                hover_color=self.c("#D1D5F0"),
                                text_color="white" if active else self.accent_color,
                                border_color=self.accent_color,
                                border_width=1 if not active else 0,
                                corner_radius=10, height=35,
                                font=("Garet Variable", 13),
                                command=lambda k=key: self.change_view(k))
            btn.pack(side="left", padx=5)
        
        scrollable = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        scrollable.pack(fill="both", expand=True, padx=40, pady=10)
        
        if self.current_gpa_view == "dashboard":
            self.draw_dashboard(scrollable)
        elif self.current_gpa_view == "ketqua_hocky":
            self.draw_ketqua(scrollable)
        elif self.current_gpa_view == "bangdiem_hocky":
            self.draw_bangdiem(scrollable)
        elif self.current_gpa_view == "phaocuu_sinh":
            self.draw_phaocuu(scrollable)
    
    def change_view(self, view):
        self.current_gpa_view = view
        self.render_gpa_view()
    
    def draw_dashboard(self, parent):
        main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        if not self.gpa_subjects:
            ctk.CTkLabel(main_frame, text="📭 Chưa có dữ liệu điểm nào.\nVui lòng thêm môn học trong 'Bảng điểm'!", 
                        font=("Garet Variable", 18, "bold"), text_color="gray").pack(expand=True, pady=50)
            return
        
        total_credits = self.get_total_credits()
        total_credits_needed = 122
        progress = min(total_credits / total_credits_needed, 1.0)
        overall_gpa = self.compute_gpa_by_semester()
        target_gpa = self.long_term_target_gpa
        xep_loai = self.get_xep_loai(overall_gpa)
        
        # 3 thẻ thông tin
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)
        
        # Card GPA
        card_gpa = ctk.CTkFrame(info_frame, fg_color=self.card_color, corner_radius=15)
        card_gpa.pack(side="left", padx=10, fill="both", expand=True)
        ctk.CTkLabel(card_gpa, text="GPA Tích lũy", font=("Garet Variable", 14, "bold"), text_color="gray").pack(pady=(10, 5))
        ctk.CTkLabel(card_gpa, text=f"{overall_gpa:.2f}", font=("Garet Variable", 32, "bold"), text_color=self.accent_color).pack()
        ctk.CTkLabel(card_gpa, text=xep_loai, font=("Garet Variable", 12), text_color="orange").pack(pady=(0, 10))
        
        # Card Tín chỉ
        card_cred = ctk.CTkFrame(info_frame, fg_color=self.card_color, corner_radius=15)
        card_cred.pack(side="left", padx=10, fill="both", expand=True)
        ctk.CTkLabel(card_cred, text="Tín chỉ đã hoàn thành", font=("Garet Variable", 14, "bold"), text_color="gray").pack(pady=(10, 5))
        ctk.CTkLabel(card_cred, text=f"{total_credits} / {total_credits_needed}", font=("Garet Variable", 24, "bold"), text_color=self.accent_color).pack()
        bar = ctk.CTkProgressBar(card_cred, width=200, height=12, corner_radius=6, fg_color=self.c("#E0E0E0"), progress_color=self.accent_color)
        bar.pack(pady=5)
        bar.set(progress)
        
        # Card Mục tiêu
        card_target = ctk.CTkFrame(info_frame, fg_color=self.card_color, corner_radius=15)
        card_target.pack(side="left", padx=10, fill="both", expand=True)
        ctk.CTkLabel(card_target, text="Mục tiêu GPA cuối khóa", font=("Garet Variable", 14, "bold"), text_color="gray").pack(pady=(10, 5))
        ctk.CTkLabel(card_target, text=f"{target_gpa:.2f}", font=("Garet Variable", 24, "bold"), text_color=self.accent_color).pack()
        ctk.CTkButton(card_target, text="Đặt lại", fg_color=self.accent_color, height=30, width=80,
                      font=("Garet Variable", 13), hover_color=self.c("#D1D5F0"), command=self.set_target).pack(pady=5)
        
        # Biểu đồ 1: Thống kê điểm chữ
        chart_frame1 = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15)
        chart_frame1.pack(fill="x", pady=10, padx=10)
        
        if self.gpa_subjects:
            # Đếm số lượng môn theo điểm chữ
            grade_counts = {"A+": 0, "A": 0, "B+": 0, "B": 0, "C+": 0, "C": 0, "D+": 0, "D": 0, "F+": 0, "F": 0}
            for s in self.gpa_subjects:
                diem_tb = self.compute_diem_tb(s["dqt"], s["dck"], s["hs_qt"], s["hs_ck"])
                _, chu = self.diem_thang4(diem_tb)
                if chu in grade_counts:
                    grade_counts[chu] += 1
            
            # Lọc bỏ những loại không có
            labels = [k for k, v in grade_counts.items() if v > 0]
            values = [v for v in grade_counts.values() if v > 0]
            
            if labels:
                fig1 = Figure(figsize=(6, 4), dpi=90)
                ax1 = fig1.add_subplot(111)
                colors = ['#2ECC71', '#27AE60', '#3498DB', '#2980B9', '#F39C12', 
                          '#E67E22', '#E74C3C', '#C0392B', '#95A5A6', '#7F8C8D']
                ax1.bar(labels, values, color=colors[:len(labels)])
                ax1.set_title("Thống kê số lượng môn theo điểm chữ", fontsize=12)
                ax1.set_ylabel("Số môn")
                fig1.tight_layout()
                canvas1 = FigureCanvasTkAgg(fig1, master=chart_frame1)
                canvas1.draw()
                canvas1.get_tk_widget().pack(pady=10)
        
        # Biểu đồ 2: GPA theo học kỳ
        chart_frame2 = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=15)
        chart_frame2.pack(fill="both", expand=True, pady=10, padx=10)
        
        if self.gpa_subjects:
            fig2 = Figure(figsize=(6, 3), dpi=90)
            ax2 = fig2.add_subplot(111)
            all_kys = sorted(set(s["ky"] for s in self.gpa_subjects))
            actual_gpas = [self.compute_gpa_by_semester(ky) for ky in all_kys]
            target_gpas = [self.target_gpa_by_semester.get(ky, 3.5) for ky in all_kys]
            
            ax2.plot(all_kys, actual_gpas, marker='o', label='GPA thực tế', color="blue", linewidth=2, markersize=8)
            ax2.plot(all_kys, target_gpas, marker='s', label='GPA mục tiêu', color='red', linewidth=2, markersize=8, linestyle='--')
            ax2.set_title("So sánh GPA thực tế vs Mục tiêu", fontsize=12)
            ax2.set_xlabel("Học kỳ")
            ax2.set_ylabel("GPA (thang 4)")
            ax2.legend()
            ax2.grid(True, linestyle='--', alpha=0.7)
            fig2.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, master=chart_frame2)
            canvas2.draw()
            canvas2.get_tk_widget().pack(pady=10)
    
    def draw_ketqua(self, parent):
        """Bảng tổng hợp kết quả theo học kỳ (dàn đều 2 bên)"""
        semesters = sorted(set(s["ky"] for s in self.gpa_subjects))
        if not semesters:
            semesters = [1, 2, 3, 4, 5, 6, 7, 8]
        
        # Frame chính - tăng padx để có khoảng trống 2 bên
        main_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Frame chứa bảng để căn giữa
        table_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        table_container.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Độ rộng từng cột (px) - tổng cộng khoảng 910px
        col_widths = [110, 130, 85, 110, 80, 150, 140, 150]
        headers = ["Học kỳ", "GPA dự định", "Tổng TC", "GPA đạt được", "Số môn", "Xếp loại", "Hoàn thành", "Cơ hội HB"]
        
        # Header
        header_frame = ctk.CTkFrame(table_container, fg_color=self.accent_color, corner_radius=10)
        header_frame.pack(pady=(0, 10))
        
        for col, (text, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(header_frame, text=text, font=("Garet Variable", 13, "bold"), 
                        text_color="white", width=width, anchor="center").grid(row=0, column=col, padx=2, pady=10)
        
        # Dữ liệu
        for row, ky in enumerate(semesters):
            total_cred = self.get_total_credits(ky)
            actual_gpa = self.compute_gpa_by_semester(ky)
            target_gpa = self.target_gpa_by_semester.get(ky, None)
            so_mon = len([sub for sub in self.gpa_subjects if sub["ky"] == ky])
            xep_loai = self.get_xep_loai(actual_gpa)
            hoan_thanh = "✅ Hoàn thành" if target_gpa is not None and actual_gpa >= target_gpa else "❌ Chưa đạt"
            co_hoc_bong = "🏆 Cơ hội cao" if actual_gpa >= 3.2 else "⚠️ Cần cố gắng"
            
            row_frame = ctk.CTkFrame(table_container, fg_color="#F8F9FA" if row % 2 == 0 else "white", corner_radius=8)
            row_frame.pack(pady=3)
            
            # Học kỳ
            ctk.CTkLabel(row_frame, text=f"Học kỳ {ky}", font=("Garet Variable", 13), 
                        width=col_widths[0], anchor="center").grid(row=0, column=0, padx=2, pady=8)
            
            # GPA dự định Entry
            if target_gpa is not None:
                target_var = ctk.StringVar(value=f"{target_gpa:.2f}")
            else:
                target_var = ctk.StringVar(value="")
            
            target_entry = ctk.CTkEntry(row_frame, textvariable=target_var, width=col_widths[1]-15, height=32,
                                        justify="center", font=("Garet Variable", 13))
            target_entry.grid(row=0, column=1, padx=2, pady=5)
            
            def save_target(event=None, k=ky, var=target_var, entry=target_entry):
                try:
                    val_text = var.get().strip()
                    if not val_text:
                        if k in self.target_gpa_by_semester:
                            del self.target_gpa_by_semester[k]
                            self.db.set_target_by_semester(k, None)
                        self.render_gpa_view()
                        return
                    
                    new_val = float(val_text)
                    if 0 <= new_val <= 4:
                        self.target_gpa_by_semester[k] = new_val
                        self.db.set_target_by_semester(k, new_val)
                        self.render_gpa_view()
                    else:
                        messagebox.showwarning("Lỗi nhập GPA", "GPA mục tiêu phải từ 0.0 đến 4.0")
                        old_val = self.target_gpa_by_semester.get(k, None)
                        if old_val is not None:
                            var.set(f"{old_val:.2f}")
                        else:
                            var.set("")
                        entry.focus()
                except ValueError:
                    messagebox.showerror("Lỗi định dạng", "Vui lòng nhập số hợp lệ (ví dụ: 3.5)")
                    old_val = self.target_gpa_by_semester.get(k, None)
                    if old_val is not None:
                        var.set(f"{old_val:.2f}")
                    else:
                        var.set("")
                    entry.focus()
            
            target_entry.bind("<FocusOut>", save_target)
            target_entry.bind("<Return>", save_target)
            
            # Các cột còn lại
            ctk.CTkLabel(row_frame, text=str(total_cred), width=col_widths[2], anchor="center").grid(row=0, column=2, padx=2, pady=8)
            ctk.CTkLabel(row_frame, text=f"{actual_gpa:.2f}", font=("Garet Variable", 13, "bold"),
                        text_color=self.accent_color, width=col_widths[3], anchor="center").grid(row=0, column=3, padx=2, pady=8)
            ctk.CTkLabel(row_frame, text=str(so_mon), width=col_widths[4], anchor="center").grid(row=0, column=4, padx=2, pady=8)
            ctk.CTkLabel(row_frame, text=xep_loai, width=col_widths[5], anchor="center").grid(row=0, column=5, padx=2, pady=8)
            ctk.CTkLabel(row_frame, text=hoan_thanh, width=col_widths[6], anchor="center").grid(row=0, column=6, padx=2, pady=8)
            ctk.CTkLabel(row_frame, text=co_hoc_bong, width=col_widths[7], anchor="center").grid(row=0, column=7, padx=2, pady=8)
    def update_target_gpa(self, ky, value):
        try:
            if not value or value.strip() == "":
                if ky in self.target_gpa_by_semester:
                    del self.target_gpa_by_semester[ky]
                    self.db.set_target_by_semester(ky, None)
            else:
                val = float(value)
                if 0 <= val <= 4:
                    self.target_gpa_by_semester[ky] = val
                    self.db.set_target_by_semester(ky, val)
                else:
                    messagebox.showwarning("Lỗi", "GPA phải từ 0 đến 4")
                    return
            self.render_gpa_view()
        except:
            messagebox.showerror("Lỗi", "Vui lòng nhập số")
    
    def draw_bangdiem(self, parent):
        """Bảng điểm chi tiết (bỏ cột hệ số QT và CK)"""
        filtered = [s for s in self.gpa_subjects if s["ky"] == self.filter_ky]
        
        # Frame chứa dropdown và nút thêm (cùng hàng)
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(fill="x", pady=10, padx=10)
        
        # Bên trái: Chọn học kỳ (7 kỳ)
        left_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        left_frame.pack(side="left")
        
        ctk.CTkLabel(left_frame, text="Chọn học kỳ:", font=("Garet Variable", 14, "bold")).pack(side="left", padx=5)
        
        all_semesters = [1, 2, 3, 4, 5, 6, 7, 8]
        sem_str = [f"Học kỳ {k}" for k in all_semesters]
        
        opt = ctk.CTkOptionMenu(left_frame, values=sem_str, 
                                dropdown_font=("Garet Variable", 13), font=("Garet Variable", 13), 
                                fg_color="#F0F0F0", text_color="black",
                                button_color=self.accent_color,
                                button_hover_color=self.c("#2E3A6E"), 
                                dropdown_hover_color=self.c("#D1D5F0"),
                                variable=self.semester_var, command=lambda val: self.change_ky(int(val.split(" ")[-1])))
        opt.pack(side="left", padx=10)
        
        # Bên phải: Nút thêm môn
        ctk.CTkButton(control_frame, text="+ Thêm môn học", fg_color="#27AE60", 
                      font=("Garet Variable", 13), hover_color=self.c("#D1D5F0"), command=self.add_subject).pack(side="right", padx=10)
        
        # Bảng điểm (đã lược bỏ cột hệ số)
        table_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        headers = ["STT", "Tên học phần", "TC", "Điểm QT", "Điểm CK", "Điểm TB (10)", "Điểm chữ", "Thang 4", "Chi tiết"]
        for col, txt in enumerate(headers):
            ctk.CTkLabel(table_frame, text=txt, font=("Garet Variable", 11, "bold"),
                        fg_color=self.accent_color, text_color="white",
                        corner_radius=5, padx=5, pady=5).grid(row=0, column=col, padx=2, pady=5, sticky="ew")
        
        for i, s in enumerate(filtered, start=1):
            diem_tb = self.compute_diem_tb(s["dqt"], s["dck"], s["hs_qt"], s["hs_ck"])
            diem_4, chu = self.diem_thang4(diem_tb)
            
            color_map = {"A+": "#2ECC71", "A": "#27AE60", "B+": "#3498DB", "B": "#2980B9",
                        "C+": "#F39C12", "C": "#E67E22", "D+": "#E74C3C", "D": "#C0392B",
                        "F+": "#95A5A6", "F": "#7F8C8D"}
            chu_color = color_map.get(chu, "black")
            
            ctk.CTkLabel(table_frame, text=str(i), font=("Garet Variable", 11)).grid(row=i, column=0, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=s["name"], font=("Garet Variable", 11), wraplength=150).grid(row=i, column=1, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=str(s["tc"]), font=("Garet Variable", 11)).grid(row=i, column=2, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=f"{s['dqt']:.1f}", font=("Garet Variable", 11)).grid(row=i, column=3, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=f"{s['dck']:.1f}", font=("Garet Variable", 11)).grid(row=i, column=4, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=f"{diem_tb:.1f}", font=("Garet Variable", 11)).grid(row=i, column=5, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=chu, font=("Garet Variable", 11, "bold"), text_color=chu_color).grid(row=i, column=6, padx=2, pady=3)
            ctk.CTkLabel(table_frame, text=f"{diem_4:.2f}", font=("Garet Variable", 11)).grid(row=i, column=7, padx=2, pady=3)
            ctk.CTkButton(table_frame, text="✎", width=40, height=25, fg_color="#FF9800", hover_color=self.c("#D1D5F0"),
                          font=("Garet Variable", 13), command=lambda sub=s: self.edit_subject(sub)).grid(row=i, column=8, padx=2, pady=3)
        
        # Tổng kết
        gpa_ky = self.compute_gpa_by_semester(self.filter_ky)
        total_cred_ky = self.get_total_credits(self.filter_ky)
        summary_frame = ctk.CTkFrame(table_frame, fg_color=self.c("#E9EBF8"), corner_radius=8)
        summary_frame.grid(row=len(filtered) + 1, column=0, columnspan=9, pady=10, sticky="ew")
        
        ctk.CTkLabel(summary_frame, text=f"📊 GPA học kỳ: {gpa_ky:.2f}   |   Tổng tín chỉ: {total_cred_ky}   |   Xếp loại: {self.get_xep_loai(gpa_ky)}",
                    font=("Garet Variable", 13, "bold"), text_color=self.accent_color).pack(pady=8)
        
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)

    def get_subjects_by_major(self):
        """Lấy danh sách môn học trong chương trình đào tạo của sinh viên"""
        try:
            id_nganh = self.db.get_student_nganh()
            if not id_nganh:
                return []
            
            # SỬA: Dùng cursor từ db thay vì self.cursor
            self.db.cursor.execute("""
                SELECT m.ID_MON, m.TEN_MON, m.SO_TIN_CHI, ct.HOC_KY_DU_KIEN
                FROM CHUONGTRINH_DAOTAO ct
                JOIN MONHOC m ON ct.ID_MON = m.ID_MON
                WHERE ct.ID_NGANH = ?
                ORDER BY ct.HOC_KY_DU_KIEN, m.TEN_MON
            """, (id_nganh,))
            return self.db.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi lấy môn học: {e}")
            return []
        
    def add_subject(self):
        """Thêm môn học mới - có ô nhập học kỳ thực tế"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm môn học")
        dialog.geometry("450x700")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="THÊM MÔN HỌC", font=("Garet Variable", 18, "bold"), 
                    text_color=self.accent_color).pack(pady=20)
        
        # Lấy danh sách môn học theo ngành
        all_subjects = self.get_subjects_by_major()
        
        # Lọc môn theo học kỳ đang chọn (gợi ý)
        subjects = [s for s in all_subjects if s[3] == self.filter_ky]
        subject_names = [f"{s[1]}" for s in subjects] if subjects else []
        
        if not subject_names:
            ctk.CTkLabel(dialog, text=f"⚠️ Không có môn học nào trong học kỳ {self.filter_ky}", 
                        font=("Garet Variable", 12), text_color="red").pack(pady=10)
        else:
            ctk.CTkLabel(dialog, text=f"Học kỳ dự kiến: {self.filter_ky}", 
                        font=("Garet Variable", 12), text_color="gray").pack(anchor="w", padx=40)
            
            ctk.CTkLabel(dialog, text="Chọn môn học", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
            subject_var = ctk.StringVar()
            subject_combo = ctk.CTkOptionMenu(dialog, values=subject_names, variable=subject_var, fg_color="white", text_color="black",
                                   font=("Garet Variable", 13), 
                                   button_color=self.accent_color,       
                                   button_hover_color=self.c("#2E3A6E"),  
                                   dropdown_hover_color=self.c("#D1D5F0"),
                                   dropdown_font=("Garet Variable", 13),width=350)
            subject_combo.pack(pady=(5, 15))
        
        # ===== Ô NHẬP HỌC KỲ THỰC TẾ =====
        ctk.CTkLabel(dialog, text="Học kỳ thực tế (số)", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        ky_entry = ctk.CTkEntry(dialog, placeholder_text="VD: 1,2,3,4,5,6,7", font=("Garet Variable", 13), width=350)
        ky_entry.insert(0, str(self.filter_ky))
        ky_entry.pack(pady=(5, 15))
        # =================================
        
        # Năm học
        ctk.CTkLabel(dialog, text="Năm học", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        nam_hoc_entry = ctk.CTkEntry(dialog, placeholder_text="VD: 2024-2025", font=("Garet Variable", 13), width=350)
        nam_hoc_entry.insert(0, "2024-2025")
        nam_hoc_entry.pack(pady=(5, 15))
        
        # Điểm quá trình
        ctk.CTkLabel(dialog, text="Điểm quá trình (0-10)", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        dqt_entry = ctk.CTkEntry(dialog, placeholder_text="0-10", font=("Garet Variable", 13), width=350)
        dqt_entry.pack(pady=(5, 15))
        
        # Hệ số quá trình
        ctk.CTkLabel(dialog, text="Hệ số quá trình (0-1)", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        hsqt_entry = ctk.CTkEntry(dialog, placeholder_text="0-1", font=("Garet Variable", 13), width=350)
        hsqt_entry.insert(0, "0.5")
        hsqt_entry.pack(pady=(5, 15))
        
        # Điểm cuối kỳ
        ctk.CTkLabel(dialog, text="Điểm cuối kỳ (0-10)", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        dck_entry = ctk.CTkEntry(dialog, placeholder_text="0-10", font=("Garet Variable", 13), width=350)
        dck_entry.pack(pady=(5, 15))
        
        # Hệ số cuối kỳ
        ctk.CTkLabel(dialog, text="Hệ số cuối kỳ (0-1)", font=("Garet Variable", 12, "bold")).pack(anchor="w", padx=40)
        hsck_entry = ctk.CTkEntry(dialog, placeholder_text="0-1", font=("Garet Variable", 13), width=350)
        hsck_entry.insert(0, "0.5")
        hsck_entry.pack(pady=(5, 15))
        
        def save():
            try:
                if not subject_names:
                    messagebox.showwarning("Lỗi", f"Không có môn học nào trong học kỳ {self.filter_ky}!")
                    return
                
                selected = subject_var.get()
                if not selected:
                    messagebox.showwarning("Lỗi", "Vui lòng chọn môn học!")
                    return
                
                subject_name = selected
                ky = int(ky_entry.get())
                
                if ky < 1 or ky > 7:
                    messagebox.showwarning("Lỗi", "Học kỳ thực tế phải từ 1 đến 7!")
                    return
                
                nam_hoc = nam_hoc_entry.get().strip()
                dqt = float(dqt_entry.get())
                hsqt = float(hsqt_entry.get())
                dck = float(dck_entry.get())
                hsck = float(hsck_entry.get())
                
                id_mon = None
                for s in all_subjects:
                    if s[1] == subject_name:
                        id_mon = s[0]
                        break
                
                if not id_mon:
                    messagebox.showerror("Lỗi", "Không tìm thấy ID môn học!")
                    return
                
                if not (0 <= dqt <= 10):
                    messagebox.showwarning("Lỗi", "Điểm quá trình phải từ 0-10")
                    return
                if not (0 <= dck <= 10):
                    messagebox.showwarning("Lỗi", "Điểm cuối kỳ phải từ 0-10")
                    return
                
                result = self.db.add_grade(id_mon, dqt, dck, hsqt, hsck, ky, subject_name, 3, nam_hoc)
                if result:
                    self.load_grades()
                    dialog.destroy()
                    self.render_gpa_view()
                    messagebox.showinfo("Thành công", f"Đã thêm môn {subject_name} vào học kỳ {ky}")
                else:
                    messagebox.showerror("Lỗi", "Thêm môn thất bại!")
            except ValueError as e:
                messagebox.showerror("Lỗi", f"Vui lòng nhập đúng định dạng số: {e}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {e}")
        
        ctk.CTkButton(dialog, text="Lưu", fg_color="#27AE60", font=("Garet Variable", 13), command=save).pack(pady=20)
    
    def edit_subject(self, subject):
        """Sửa hoặc xóa môn học (có label hướng dẫn từng ô)"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết môn học")
        dialog.geometry("450x450")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=subject["name"], font=("Garet Variable", 18, "bold"), 
                     text_color=self.accent_color).pack(pady=20)
        
        # Frame chứa các ô nhập có label
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Điểm quá trình
        ctk.CTkLabel(form_frame, text="Điểm quá trình:", font=("Garet Variable", 12, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        dqt_entry = ctk.CTkEntry(form_frame, width=200, font=("Garet Variable", 13))
        dqt_entry.insert(0, str(subject["dqt"]))
        dqt_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Hệ số quá trình
        ctk.CTkLabel(form_frame, text="Hệ số quá trình (0-1):", font=("Garet Variable", 12, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        hsqt_entry = ctk.CTkEntry(form_frame, width=200, font=("Garet Variable", 13))
        hsqt_entry.insert(0, str(subject["hs_qt"]))
        hsqt_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Điểm cuối kỳ
        ctk.CTkLabel(form_frame, text="Điểm cuối kỳ:", font=("Garet Variable", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        dck_entry = ctk.CTkEntry(form_frame, width=200, font=("Garet Variable", 13))
        dck_entry.insert(0, str(subject["dck"]))
        dck_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Hệ số cuối kỳ
        ctk.CTkLabel(form_frame, text="Hệ số cuối kỳ (0-1):", font=("Garet Variable", 12, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        hsck_entry = ctk.CTkEntry(form_frame, width=200, font=("Garet Variable", 13))
        hsck_entry.insert(0, str(subject["hs_ck"]))
        hsck_entry.grid(row=3, column=1, pady=5, padx=10)
        
        def update():
            try:
                dqt = float(dqt_entry.get())
                hsqt = float(hsqt_entry.get())
                dck = float(dck_entry.get())
                hsck = float(hsck_entry.get())
                # Cập nhật điểm và hệ số (cần sửa database method nếu muốn lưu hệ số)
                # Ở đây chỉ cập nhật điểm QT và CK (giữ nguyên hệ số cũ nếu database chỉ có 2 cột điểm)
                # Nếu muốn cập nhật cả hệ số, cần sửa phương thức update_grade trong database.py
                self.db.update_grade(subject["id"], dqt, dck)
                # Nếu database hỗ trợ cập nhật hệ số, bạn có thể thêm code ở đây
                self.load_grades()
                dialog.destroy()
                self.render_gpa_view()
                messagebox.showinfo("Thành công", "Đã cập nhật điểm")
            except ValueError:
                messagebox.showerror("Lỗi", "Vui lòng nhập đúng định dạng số")
        
        def delete():
            if messagebox.askyesno("Xác nhận", f"Xóa môn {subject['name']}?"):
                self.db.delete_grade(subject["id"])
                self.load_grades()
                dialog.destroy()
                self.render_gpa_view()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Cập nhật", fg_color="#27AE60", font=("Garet Variable", 13), command=update).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Xóa", fg_color="#E74C3C", font=("Garet Variable", 13), command=delete).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Hủy", fg_color="gray", font=("Garet Variable", 13), command=dialog.destroy).pack(side="left", padx=10)
    
    def change_ky(self, ky):
        self.filter_ky = ky
        self.render_gpa_view()

    # -------------------- PHAO CỨU SINH (SỬA THEO EXCEL) --------------------
    def draw_phaocuu(self, parent):
        """Phao cứu sinh - tính bảng theo công thức Excel"""
        total_credits_needed = 122
        completed_credits = self.get_total_credits()
        remaining_credits = total_credits_needed - completed_credits
        target_gpa = self.long_term_target_gpa
        current_gpa = self.compute_gpa_by_semester()
        
        # Tính GPA cần đạt cho các môn còn lại (need)
        if remaining_credits > 0:
            current_weighted = sum(
                self.diem_thang4(self.compute_diem_tb(s["dqt"], s["dck"], s["hs_qt"], s["hs_ck"]))[0] * s["tc"]
                for s in self.gpa_subjects
            )
            need_gpa = (target_gpa * total_credits_needed - current_weighted) / remaining_credits
            need_gpa = max(0, min(need_gpa, 4.0))
            message = f"Để đạt GPA mục tiêu {target_gpa:.2f}, các môn còn lại ({remaining_credits} TC) cần đạt trung bình {need_gpa:.2f} (thang 4)."
        else:
            need_gpa = 0
            message = "✅ Bạn đã hoàn thành tất cả các môn học!"
        
        main_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="🆘 PHAO CỨU SINH", font=("Garet Variable", 28, "bold"), 
                    text_color=self.accent_color).pack(pady=20)
        ctk.CTkLabel(main_frame, text=message, font=("Garet Variable", 14), wraplength=700, justify="center").pack(pady=10)
        
        if remaining_credits > 0:
            # Bảng gợi ý điểm theo đúng công thức Excel
            table_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            table_frame.pack(pady=10, padx=20, fill="x")
            
            # Tiêu đề cột
            headers = ["Loại điểm", "Thang 4", "Số tín chỉ tối đa"]
            for col, txt in enumerate(headers):
                ctk.CTkLabel(table_frame, text=txt, font=("Garet Variable", 11, "bold"),
                            fg_color=self.accent_color, text_color="white",
                            corner_radius=5, padx=10, pady=8).grid(row=0, column=col, sticky="ew", padx=2, pady=2)
            
            # Dữ liệu các loại điểm (gộp A/A+)
            grades = [
                ("A / A+", 4.0), ("B+", 3.5), ("B", 3.0), 
                ("C+", 2.5), ("C", 2.0), ("D+", 1.5), ("D", 1.0), 
                ("F+", 0.5), ("F", 0.0)
            ]
            
            for i, (grade_name, grade_val) in enumerate(grades, start=1):
                # Công thức tính số tín chỉ tối đa
                if need_gpa >= 4.0:
                    max_credits = 0
                else:
                    if grade_val == 4.0:
                        # Với điểm A/A+ (4.0), nếu need_gpa < 4 thì không giới hạn số tín chỉ
                        max_credits = remaining_credits
                    else:
                        max_credits = remaining_credits * (4 - need_gpa) / (4 - grade_val)
                        if max_credits > remaining_credits:
                            max_credits = remaining_credits
                        max_credits = int(max_credits)
                        if max_credits < 0:
                            max_credits = 0
                
                ctk.CTkLabel(table_frame, text=grade_name, font=("Garet Variable", 13)).grid(row=i, column=0, padx=2, pady=4)
                ctk.CTkLabel(table_frame, text=f"{grade_val:.1f}", font=("Garet Variable", 13)).grid(row=i, column=1, padx=2, pady=4)
                
                # Màu sắc cho A/A+
                text_color = self.accent_color if max_credits > 0 else "gray"
                if grade_name == "A / A+":
                    text_color = "#F39C12"  # Màu cam nổi bật
                    
                ctk.CTkLabel(table_frame, text=str(max_credits), font=("Garet Variable", 13, "bold"),
                            text_color=text_color).grid(row=i, column=2, padx=2, pady=4)
            
            table_frame.grid_columnconfigure(0, weight=1)
            table_frame.grid_columnconfigure(1, weight=1)
            table_frame.grid_columnconfigure(2, weight=2)
            
            # Note đẹp hơn
            note_frame = ctk.CTkFrame(main_frame, fg_color="#F0F4FC", corner_radius=15, border_width=1, border_color=self.accent_color)
            note_frame.pack(pady=20, padx=20, fill="x")
            
            # Icon và tiêu đề note
            note_header = ctk.CTkFrame(note_frame, fg_color="transparent")
            note_header.pack(fill="x", padx=15, pady=(15, 5))
            ctk.CTkLabel(note_header, text="📌", font=("Garet Variable", 18)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(note_header, text="HƯỚNG DẪN SỬ DỤNG", font=("Garet Variable", 13, "bold"), 
                        text_color=self.accent_color).pack(side="left")
            
            # Nội dung note
            note_content = ctk.CTkFrame(note_frame, fg_color="transparent")
            note_content.pack(fill="x", padx=15, pady=(5, 15))
            
            notes = [
                "🎯 A / A+ (4.0) - Có thể nhận toàn bộ số tín chỉ còn lại",
                "📊 Các con số là tối đa, nên đặt mục tiêu thấp hơn 10-15% để an toàn",
                "💡 GPA càng cao, số môn được điểm thấp càng ít",
                "🔄 Cập nhật điểm thường xuyên để được tư vấn chính xác nhất"
            ]
            
            for note in notes:
                ctk.CTkLabel(note_content, text=note, font=("Garet Variable", 12), 
                            text_color="#555", anchor="w", justify="left").pack(anchor="w", pady=3)
        
        ctk.CTkButton(main_frame, font=("Garet Variable", 14), text="Đặt lại mục tiêu GPA", fg_color=self.accent_color, height=40, 
                     corner_radius=10, hover_color=self.c("#D1D5F0"), command=self.set_target).pack(pady=20)
    
    def adjust_layout(self):
        """Điều chỉnh layout khi sidebar thay đổi"""
        self.render_gpa_view()
    
    def set_target(self):
        # Tạo dialog tùy chỉnh
        dialog = ctk.CTkToplevel(self)
        dialog.title("Đặt mục tiêu GPA")
        dialog.geometry("400x250")
        dialog.attributes("-topmost", True)
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        
        # Căn giữa màn hình
        dialog.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 200
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 110
        dialog.geometry(f"+{x}+{y}")
        
        # Frame chính
        main_frame = ctk.CTkFrame(dialog, fg_color=self.c("#FFFFFF"), corner_radius=20)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label
        ctk.CTkLabel(main_frame, text="Nhập GPA mục tiêu cuối khóa (0-4):", 
                    font=("Garet Variable", 14, "bold"),
                    text_color=self.accent_color).pack(pady=(20, 15))
        
        # Entry
        entry = ctk.CTkEntry(main_frame, font=("Garet Variable", 14), width=250, height=40,
                            justify="center", fg_color=self.c("#F0F0F0"))
        entry.pack(pady=10)
        entry.focus()
        
        # Frame chứa nút
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def on_ok():
            value = entry.get().strip()
            if value:
                try:
                    val = float(value)
                    if 0 <= val <= 4:
                        self.long_term_target_gpa = val
                        self.db.set_gpa_target(val)
                        dialog.destroy()  # Đóng dialog TRƯỚC
                        messagebox.showinfo("Thành công", f"Đã đặt mục tiêu GPA là {val}")
                        self.render_gpa_view()
                    else:
                        messagebox.showwarning("Lỗi", "GPA phải từ 0 đến 4")
                        entry.delete(0, 'end')
                        entry.focus()
                except:
                    messagebox.showerror("Lỗi", "Vui lòng nhập số")
                    entry.delete(0, 'end')
                    entry.focus()
            else:
                messagebox.showwarning("Lỗi", "Vui lòng nhập GPA")
                entry.focus()
        
        def on_cancel():
            dialog.destroy()
        
        # Nút OK
        ok_btn = ctk.CTkButton(btn_frame, text="OK", width=100, height=35,
                            fg_color=self.accent_color,
                            hover_color=self.c("#D1D5F0"),
                            font=("Garet Variable", 13, "bold"),
                            command=on_ok)
        ok_btn.pack(side="left", padx=10)
        
        # Nút Cancel
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=100, height=35,
                                fg_color=self.c("#95A5A6"),
                                hover_color=self.c("#7F8C8D"),
                                font=("Garet Variable", 13),
                                command=on_cancel)
        cancel_btn.pack(side="left", padx=10)
        
        # Bắt phím Enter
        entry.bind("<Return>", lambda e: on_ok())
        # Bắt phím Esc
        dialog.bind("<Escape>", lambda e: on_cancel())
        