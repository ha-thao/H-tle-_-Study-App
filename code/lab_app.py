# lab_app.py - ĐÃ SỬA + THÊM THEME
import customtkinter as ctk
from tkinter import messagebox
import calendar
import random
from datetime import datetime


class LabBookingApp(ctk.CTkFrame):
    def __init__(self, parent, db, mssv, ho_ten, theme):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mssv = mssv
        self.ho_ten = ho_ten
        self.theme = theme

        # Lấy màu từ theme
        self.bg_color = self.c("#FDF6E3")
        self.sidebar_color = self.c("#E9EBF8")
        self.accent_color = self.c("#3F51B5")
        self.card_color = self.c("#FFFFFF")
        self.folder_color = self.c("#D1D5F0")
        self.success_color = "#2ECC71"
        self.summary_bg = self.c("#1A237E")
        self.text_dark = self.c("#2C3E50")
        self.disabled_color = self.c("#B0BCE6")
        self.danger_color = "#E74C3C"
        
        # Lấy ngày hiện tại theo định dạng SQL
        today = datetime.now()
        today_sql = today.strftime("%Y-%m-%d")
        today_display = today.strftime("%d/%m/%Y")
        
        # Trạng thái đặt chỗ hiện tại
        self.booking_data = {
            "date_sql": today_sql,
            "date_display": today_display,
            "slot": None,
            "slot_db": None,
            "reason": "--Xin hãy chọn lý do--",
            "people": 1,
            "members_list": []
        }
        
        self.current_booking_id = None
        self.view_state = "LAB_STEP1"
        self.slot_frames = []

        self.setup_ui()
    
    def c(self, hex_code):
        """Lấy màu từ theme"""
        if self.theme:
            return self.theme.get(hex_code, hex_code)
        return hex_code
    
    def setup_ui(self):
        self.workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace.pack(fill="both", expand=True)
        self.render_view()
    
    def render_view(self):
        for w in self.workspace.winfo_children():
            w.destroy()
        
        if self.view_state == "LAB_STEP1":
            self.draw_lab_step1()
        elif self.view_state == "LAB_STEP2":
            self.draw_lab_step2()
        elif self.view_state == "LAB_SUCCESS":
            self.draw_lab_success()
        elif self.view_state == "LAB_HISTORY":
            self.draw_lab_history()
    
    def draw_lab_step1(self):
        # Lưu vị trí scroll cũ
        scroll_pos = 0
        if hasattr(self, 'main_container') and self.main_container.winfo_exists():
            try:
                canvas = self.main_container._parent_canvas
                scroll_pos = canvas.yview()[0] if canvas else 0
            except:
                pass
        
        # Xóa container cũ
        if hasattr(self, 'main_container') and self.main_container.winfo_exists():
            self.main_container.destroy()
        
        # Tạo container mới
        self.main_container = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=(70, 40), pady=20)
        
        # ========== HEADER ==========
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="OpenLab", font=("Garet Variable", 42, "bold"), 
                     text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header, text="Lịch sử đặt lab", 
                      fg_color=self.card_color, text_color="black", 
                      border_width=1, border_color=self.c("#DDDDDD"), 
                      height=40, corner_radius=12, font=("Garet Variable", 13),
                      hover_color=self.folder_color, command=self.show_history).pack(side="right", pady=10)
        
        # ========== THÔNG TIN PHÒNG + GIỚI THIỆU ==========
        info_frame = ctk.CTkFrame(self.main_container, fg_color=self.card_color, corner_radius=20, 
                                  border_width=1, border_color=self.c("#E0E0E0"))
        info_frame.pack(fill="x", pady=(10, 15), padx=5)
        
        # Phòng
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(row1, text="📍 Phòng 1509 - UEH Cơ sở B", font=("Garet Variable", 15, "bold"), 
                     text_color=self.accent_color).pack()
        
        # Giới thiệu
        intro_text = """OpenLab là Phòng thí nghiệm mở thuộc Trường Đại học Sư phạm Kỹ thuật TP.HCM, do PGS.TS. Nguyễn Trường Thịnh thành lập từ năm 2010.
OpenLab có ba mục tiêu chính: thúc đẩy nghiên cứu cơ bản về AI & Robotics; hợp tác với cộng đồng doanh nghiệp trong các dự án ứng dụng công nghệ vào doanh nghiệp; và cung cấp giáo dục khoa học thông qua các nghiên cứu sau đại học."""
        ctk.CTkLabel(info_frame, text=intro_text, font=("Garet Variable", 12), 
                     text_color="gray", wraplength=950, justify="left").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Email
        ctk.CTkLabel(info_frame, text="📧 Email: 3itech@ueh.edu.vn", font=("Garet Variable", 12, "bold"), 
                     text_color=self.accent_color).pack(anchor="w", padx=20, pady=(0, 15))
        
        # ========== THIẾT BỊ ==========
        ctk.CTkLabel(self.main_container, text="🛠️ Thiết bị có sẵn trong phòng lab", 
                     font=("Garet Variable", 14, "bold"), text_color="gray").pack(anchor="w", pady=(15, 10))
        
        device_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        device_row.pack(fill="x", pady=5)
        
        for i in range(4):
            device_row.grid_columnconfigure(i, weight=1)
        
        devices = [
            ("🎛️", "GPU", "NVIDIA RTX 4090 x 10"),
            ("☁️", "SERVER", "Lambda Stack AI Server"),
            ("📽️", "MÁY CHIẾU", "EPSON Full HD 4K"),
            ("🔌", "Ổ CẮM", "Ổ cắm nguồn ổn áp 220V")
        ]
        
        for i, (icon, title, desc) in enumerate(devices):
            d_card = ctk.CTkFrame(device_row, fg_color=self.card_color, height=120, corner_radius=20, 
                                  border_width=1, border_color=self.c("#E0E0E0"))
            d_card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            d_card.grid_propagate(False)
            
            ctk.CTkLabel(d_card, text=icon, font=("Garet Variable", 38)).pack(pady=(20, 5))
            ctk.CTkLabel(d_card, text=title, font=("Garet Variable", 12, "bold"), text_color="gray").pack()
            ctk.CTkLabel(d_card, text=desc, font=("Garet Variable", 10), text_color=self.accent_color).pack(pady=(3, 15))
        
        # ========== CHỌN NGÀY GIỜ ==========
        content_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_f.pack(fill="both", expand=True, pady=20)
        
        left_f = ctk.CTkFrame(content_f, fg_color="transparent")
        left_f.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(left_f, text="📅 Chọn thời gian thực hành", font=("Garet Variable", 18, "bold")).pack()
        
        self.btn_date_picker = ctk.CTkButton(left_f, 
                                             text=f"{self.booking_data['date_display']}  📅",
                                             fg_color=self.card_color, text_color="black", 
                                             hover_color=self.c("#F0F0F0"),
                                             height=45, width=220, corner_radius=12, border_width=1,
                                             border_color=self.c("#DDDDDD"), font=("Garet Variable", 14, "bold"),
                                             command=self.open_calendar_popup)
        self.btn_date_picker.pack(pady=15)
        
        slots_data = [("7:30 - 10:30", "7:30-10:30"), ("12:30 - 15:30", "12:30-15:30"), ("16:30 - 19:30", "16:30-19:30")]
        self.slot_frames = []
        
        # Lấy thông tin thời gian
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        selected_date = datetime.strptime(self.booking_data["date_sql"], "%Y-%m-%d").date()
        today_date = datetime.now().date()

        for display_time, db_time in slots_data:
            is_available = self.db.check_available_lab(self.booking_data["date_sql"], db_time)
            
            # Xác định trạng thái
            if selected_date < today_date:
                # Ngày trong quá khứ
                status = "Đã qua ngày"
                is_booked = True
                can_select = False
                bg_color = "#E8E8E8"
                text_color_status = "#A0A0A0"
                fg_color_status = "#E8E8E8"
                time_color = "#A0A0A0"
            elif selected_date == today_date:
                # Ngày hôm nay - kiểm tra giờ
                if "7:30" in display_time:
                    end_hour, end_minute = 10, 30
                elif "12:30" in display_time:
                    end_hour, end_minute = 15, 30
                else:
                    end_hour, end_minute = 19, 30
                
                if current_hour > end_hour or (current_hour == end_hour and current_minute >= end_minute):
                    status = "Đã qua giờ"
                    is_booked = True
                    can_select = False
                    bg_color = "#F2F4F4"
                    text_color_status = "#95A5A6"
                    fg_color_status = "#F0F0F0"
                    time_color = "#7F8C8D"
                elif not is_available:
                    status = "Đã đặt"
                    is_booked = True
                    can_select = False
                    bg_color = self.folder_color
                    text_color_status = self.accent_color
                    fg_color_status = self.c("#E9EBF8")
                    time_color = self.text_dark
                else:
                    status = "Còn trống"
                    is_booked = False
                    can_select = True
                    bg_color = self.card_color
                    text_color_status = self.success_color
                    fg_color_status = self.c("#E8F8F5")
                    time_color = "black"
            else:
                # Ngày tương lai
                if not is_available:
                    status = "Đã đặt"
                    is_booked = True
                    can_select = False
                    bg_color = self.folder_color
                    text_color_status = self.accent_color
                    fg_color_status = self.c("#E9EBF8")
                    time_color = self.text_dark
                else:
                    status = "Còn trống"
                    is_booked = False
                    can_select = True
                    bg_color = self.card_color
                    text_color_status = self.success_color
                    fg_color_status = self.c("#E8F8F5")
                    time_color = "black"
            
            is_selected = self.booking_data["slot"] == display_time
            
            f = ctk.CTkFrame(left_f, fg_color=bg_color, height=70, corner_radius=20,
                            border_width=3 if is_selected else 0, 
                            border_color=self.accent_color if is_selected else self.card_color)
            f.pack(fill="x", pady=8)
            f.pack_propagate(False)
            
            self.slot_frames.append({
                "frame": f,
                "time": display_time,
                "is_booked": is_booked
            })
            
            ctk.CTkLabel(f, text="🕒", font=("Garet Variable", 20)).pack(side="left", padx=25)
            ctk.CTkLabel(f, text=display_time, font=("Garet Variable", 15, "bold"), 
                        text_color=time_color).pack(side="left")
            
            st_lbl = ctk.CTkLabel(f, text=status, font=("Garet Variable", 12, "bold"),
                                  text_color=text_color_status, fg_color=fg_color_status,
                                  width=110, height=35, corner_radius=12)
            st_lbl.pack(side="right", padx=25)
            
            if can_select:
                f.configure(cursor="hand2")
                f.bind("<Button-1>", lambda e, t=display_time, db_t=db_time: self.select_slot(t, db_t))
        
        # ========== NỘI QUY ==========
        right_f = ctk.CTkFrame(content_f, fg_color=self.card_color, width=300, height=350, corner_radius=20, 
                              border_width=1, border_color=self.c("#E0E0E0"))
        right_f.pack(side="right", padx=(30, 0))
        right_f.pack_propagate(False)
        
        ctk.CTkLabel(right_f, text="📋 NỘI QUY PHÒNG LAB", font=("Garet Variable", 20, "bold"), 
                     text_color=self.accent_color).pack(pady=(50, 12))
        
        rules_text = "✓ Không mang đồ ăn, thức uống\n\n✓ Vệ sinh sạch sẽ sau khi sử dụng\n\n✓ Sắp xếp thiết bị đúng vị trí\n\n✓ Giữ gìn trật tự, không đùa giỡn\n\n✓ Báo cáo nếu thiết bị hư hỏng\n\n✓ Tắt máy tính trước khi ra về"
        ctk.CTkLabel(right_f, text=rules_text, font=("Garet Variable", 13), justify="left", 
                     padx=20, wraplength=260).pack()
        
        # ========== NÚT TIẾP THEO ==========
        btn_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_f.pack(fill="x", pady=(20, 0))
        
        can_next = self.booking_data["slot"] is not None
        self.btn_next_step = ctk.CTkButton(btn_f, text="Tiếp theo ➔", 
                                           height=55, width=200, corner_radius=18,
                                           font=("Garet Variable", 16, "bold"),
                                           hover_color=self.accent_color if can_next else self.disabled_color,
                                           fg_color=self.accent_color if can_next else self.disabled_color,
                                           state="normal" if can_next else "disabled",
                                           command=self.go_to_step2)
        self.btn_next_step.pack(side="right")
        
        # Khôi phục vị trí scroll
        if scroll_pos > 0:
            self.main_container.after(50, lambda: self._restore_scroll(scroll_pos))
    
    def _restore_scroll(self, scroll_pos):
        """Khôi phục vị trí scroll"""
        try:
            if hasattr(self, 'main_container') and self.main_container.winfo_exists():
                canvas = self.main_container._parent_canvas
                if canvas:
                    canvas.yview_moveto(scroll_pos)
        except:
            pass
    
    def open_calendar_popup(self, year=None, month=None):
        # Đóng popup cũ nếu có
        if hasattr(self, "cal_pop") and self.cal_pop is not None:
            try:
                self.cal_pop.destroy()
            except:
                pass
        
        # Lấy ngày đang chọn từ booking_data
        current_date_str = self.booking_data["date_sql"]
        selected_day = None
        selected_month = None
        selected_year = None
        
        if current_date_str:
            try:
                current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
                selected_day = current_date.day
                selected_month = current_date.month
                selected_year = current_date.year
            except:
                pass
        
        now = datetime.now()
        
        # Xác định năm và tháng hiển thị
        if year is None:
            if selected_year is not None:
                year = selected_year
                month = selected_month
            else:
                year = now.year
                month = now.month
        else:
            # Nếu có year, month được truyền vào thì giữ nguyên
            pass
        
        # Đảm bảo month trong khoảng 1-12
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        
        self.cal_pop = ctk.CTkToplevel(self)
        self.cal_pop.title("Chọn ngày")
        self.cal_pop.geometry("400x450")
        self.cal_pop.attributes("-topmost", True)
        self.cal_pop.configure(fg_color="white")
        self.cal_pop.transient(self)
        self.cal_pop.grab_set()
        self.cal_pop.focus_force()
        
        self.cal_pop.update_idletasks()
        
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 200
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 200
        self.cal_pop.geometry(f"+{x}+{y}")
        
        # Header
        header_f = ctk.CTkFrame(self.cal_pop, fg_color="transparent")
        header_f.pack(pady=(20, 10), fill="x", padx=30)
        
        # Nút prev (tháng trước)
        btn_prev = ctk.CTkButton(header_f, text="<", width=30, fg_color=self.folder_color, text_color="black", 
                                 hover_color=self.disabled_color, font=("Garet Variable", 13))
        btn_prev.pack(side="left")
        
        # Label tháng/năm
        month_label = ctk.CTkLabel(header_f, text=f"Tháng {month} / {year}", font=("Garet Variable", 18, "bold"), 
                                   text_color=self.accent_color)
        month_label.pack(side="left", expand=True)
        
        # Nút next (tháng sau)
        btn_next = ctk.CTkButton(header_f, text=">", width=30, fg_color=self.folder_color, text_color="black", 
                                 hover_color=self.disabled_color, font=("Garet Variable", 13))
        btn_next.pack(side="right")
        
        # Hàm chuyển tháng
        def go_prev():
            new_month = month - 1
            new_year = year
            if new_month < 1:
                new_month = 12
                new_year = year - 1
            self.cal_pop.destroy()
            self.open_calendar_popup(new_year, new_month)
        
        def go_next():
            new_month = month + 1
            new_year = year
            if new_month > 12:
                new_month = 1
                new_year = year + 1
            self.cal_pop.destroy()
            self.open_calendar_popup(new_year, new_month)
        
        btn_prev.configure(command=go_prev)
        btn_next.configure(command=go_next)
        
        # Lịch
        cal_obj = calendar.monthcalendar(year, month)
        grid = ctk.CTkFrame(self.cal_pop, fg_color="transparent")
        grid.pack(padx=25, pady=10)
        
        days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        for i, d in enumerate(days):
            ctk.CTkLabel(grid, text=d, font=("Garet Variable", 12, "bold"), width=45).grid(row=0, column=i, pady=(0, 5))
        
        today_date = datetime.now().date()
        
        for r, week in enumerate(cal_obj):
            for c, day in enumerate(week):
                if day != 0:
                    current_date = datetime(year, month, day).date()
                    is_past = current_date < today_date
                    is_selected = (selected_day == day and selected_month == month and selected_year == year)
                    is_today = (day == now.day and month == now.month and year == now.year)
                    
                    if is_past:
                        btn = ctk.CTkButton(grid, text=str(day), width=42, height=42,
                                            fg_color="gray", text_color="white",
                                            hover_color="#555555", corner_radius=12,
                                            font=("Garet Variable", 13), state="disabled")
                    else:
                        if is_selected:
                            btn = ctk.CTkButton(grid, text=str(day), width=42, height=42,
                                                fg_color=self.accent_color, text_color="white",
                                                hover_color=self.c("#2E3A6E"), corner_radius=12,
                                                font=("Garet Variable", 13, "bold"),
                                                command=lambda d=day, m=month, y=year: self.set_date(d, m, y))
                        elif is_today:
                            btn = ctk.CTkButton(grid, text=str(day), width=42, height=42,
                                                fg_color=self.folder_color, text_color=self.accent_color,
                                                hover_color=self.disabled_color, corner_radius=12,
                                                font=("Garet Variable", 13, "bold"),
                                                command=lambda d=day, m=month, y=year: self.set_date(d, m, y))
                        else:
                            btn = ctk.CTkButton(grid, text=str(day), width=42, height=42,
                                                fg_color="#F0F0F0", text_color="black",
                                                hover_color=self.folder_color, corner_radius=12,
                                                font=("Garet Variable", 13),
                                                command=lambda d=day, m=month, y=year: self.set_date(d, m, y))
                    btn.grid(row=r + 1, column=c, padx=3, pady=3)
    
    def set_date(self, day, month, year):
        selected_date = datetime(year, month, day).date()
        today = datetime.now().date()
        
        if selected_date < today:
            messagebox.showwarning("Không hợp lệ", "Không thể đặt lab vào ngày trong quá khứ!")
            return
        
        date_sql = f"{year}-{month:02d}-{day:02d}"
        date_display = f"{day:02d}/{month:02d}/{year}"
        
        self.booking_data["date_sql"] = date_sql
        self.booking_data["date_display"] = date_display
        self.booking_data["slot"] = None
        self.booking_data["slot_db"] = None
        
        # Đóng popup
        if hasattr(self, "cal_pop") and self.cal_pop is not None:
            try:
                self.cal_pop.destroy()
            except:
                pass
            self.cal_pop = None
        
        # Cập nhật lại toàn bộ giao diện
        self.render_view()
    
    def clear_all_slots_border(self):
        """Xóa border của tất cả các slot"""
        try:
            for slot in self.slot_frames:
                slot["frame"].configure(border_width=0, border_color=self.c("#FFFFFF"))  # Thay bằng màu trắng
        except:
            pass
    
    def select_slot(self, slot_display, slot_db):
        self.booking_data["slot"] = slot_display
        self.booking_data["slot_db"] = slot_db
        
        # Bật nút tiếp theo
        if hasattr(self, 'btn_next_step'):
            self.btn_next_step.configure(fg_color=self.accent_color, state="normal")
        
        # Cập nhật border trực tiếp (không render lại)
        self.update_slot_ui(slot_display)

    def update_slot_ui(self, selected_slot):
        """Cập nhật border của slot được chọn - dùng list đã lưu"""
        try:
            for slot in self.slot_frames:
                if slot["time"] == selected_slot:
                    slot["frame"].configure(border_width=3, border_color=self.accent_color)
                else:
                    slot["frame"].configure(border_width=0, border_color=self.c("#FFFFFF"))  # Thay "transparent" bằng màu trắng
        except Exception as e:
            print(f"Lỗi update border: {e}")
    
    def update_slots_border(self, selected_slot=None):
        """Cập nhật border cho các slot mà không render lại toàn bộ"""
        try:
            # Tìm container chứa các slot
            for child in self.main_container.winfo_children():
                if isinstance(child, ctk.CTkFrame) and child != self.btn_next_step:
                    for frame in child.winfo_children():
                        if isinstance(frame, ctk.CTkFrame):
                            for item in frame.winfo_children():
                                if isinstance(item, ctk.CTkFrame) and item.winfo_children():
                                    for label in item.winfo_children():
                                        if isinstance(label, ctk.CTkLabel):
                                            text = label.cget("text")
                                            if "7:30" in text or "12:30" in text or "16:30" in text:
                                                if selected_slot and text == selected_slot:
                                                    item.configure(border_width=3, border_color=self.accent_color)
                                                else:
                                                    item.configure(border_width=0, border_color="transparent")
        except:
            pass
    
    def go_to_step2(self):
        self.view_state = "LAB_STEP2"
        self.render_view()
    
    def draw_lab_step2(self):
        container = ctk.CTkFrame(self.workspace, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60, pady=40)
        
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="OpenLab", font=("Garet Variable", 42, "bold"), text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header, 
                      text="Lịch sử đặt lab", 
                      fg_color="white", 
                      text_color=self.accent_color, 
                      border_width=1, 
                      border_color=self.c("#DDDDDD"), 
                      hover_color=self.folder_color, 
                      height=40, 
                      corner_radius=12, 
                      font=("Garet Variable", 13, "bold"),
                      command=self.show_history).pack(side="right", pady=10)
        
        content_box = ctk.CTkFrame(container, fg_color="transparent")
        content_box.pack(fill="both", expand=True)
        
        left_panel = ctk.CTkFrame(content_box, fg_color="white", corner_radius=30)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        inner_left = ctk.CTkFrame(left_panel, fg_color="transparent")
        inner_left.pack(padx=40, pady=35, fill="both", expand=True)
        
        ctk.CTkLabel(inner_left, text="Thông tin chi tiết", font=("Garet Variable", 24, "bold")).pack(anchor="w", pady=(0, 25))
        
        ctk.CTkLabel(inner_left, text="LÝ DO ĐẶT LAB", font=("Garet Variable", 11, "bold"), text_color="gray").pack(anchor="w")
        self.reason_var = ctk.StringVar(value=self.booking_data["reason"])
        reason_opt = ctk.CTkOptionMenu(inner_left, 
                                      values=["Làm đồ án môn học", "Nghiên cứu khoa học", "Học nhóm", "Tự học"], 
                                      font=("Garet Variable", 13), 
                                      dropdown_font=("Garet Variable", 13),
                                      variable=self.reason_var, 
                                      fg_color="#F0F0F0", 
                                      text_color="black",
                                      button_color=self.accent_color,        # Màu nút mũi tên theo ngành
                                      button_hover_color=self.c("#2E3A6E"),   # Màu đậm khi rê chuột vào mũi tên
                                      dropdown_hover_color=self.c("#D1D5F0"), # Màu nhạt khi chọn trong danh sách
                                      height=45, 
                                      corner_radius=12, 
                                      command=self.update_reason)
        reason_opt.pack(fill="x", pady=(5, 20))
        
        ctk.CTkLabel(inner_left, text="SỐ LƯỢNG NGƯỜI ĐẶT LAB  *Tối đa 10 người/lượt", font=("Garet Variable", 11, "bold"), text_color="gray").pack(anchor="w")
        count_f = ctk.CTkFrame(inner_left, fg_color="#F0F0F0", height=50, corner_radius=12)
        count_f.pack(fill="x", pady=(5, 20))
        count_f.pack_propagate(False)
        
        ctk.CTkButton(count_f, text="-", width=40, height=40,
                      fg_color=self.folder_color, # Màu nhạt theo ngành
                      text_color=self.accent_color, # Đổi sang màu chính cho nổi bật
                      hover_color=self.c("#B0BCE6"), # Hiệu ứng khi rê chuột
                      corner_radius=10,
                      font=("Garet Variable", 20, "bold"),
                      command=lambda: self.update_count(-1)).pack(side="left", padx=10, pady=5)

        # Nhãn hiển thị con số ở giữa
        self.lbl_p_count = ctk.CTkLabel(count_f, text=str(self.booking_data["people"]), 
                                        font=("Garet Variable", 18, "bold"),
                                        text_color=self.text_dark) # Màu chữ tối cho rõ
        self.lbl_p_count.pack(side="left", expand=True)

        # Nút tăng (+)
        ctk.CTkButton(count_f, text="+", width=40, height=40,
                      fg_color=self.folder_color, 
                      text_color=self.accent_color, 
                      hover_color=self.c("#B0BCE6"),
                      corner_radius=10,
                      font=("Garet Variable", 20, "bold"),
                      command=lambda: self.update_count(1)).pack(side="right", padx=10, pady=5)
        
        self.lbl_mssv_hint = ctk.CTkLabel(inner_left, text=f"THÔNG TIN THÀNH VIÊN (Cần nhập đủ {self.booking_data['people']} người, VD: {self.mssv} - {self.ho_ten})",
                                          font=("Garet Variable", 11, "bold"), text_color="gray")
        self.lbl_mssv_hint.pack(anchor="w")
        
        self.mssv_box = ctk.CTkTextbox(inner_left, fg_color="#F0F0F0", height=120, corner_radius=15, font=("Garet Variable", 14))
        self.mssv_box.pack(fill="both", expand=True, pady=(5, 0))
        self.mssv_box.insert("0.0", f"{self.mssv} - {self.ho_ten}")
        self.mssv_box.bind("<KeyRelease>", self.sync_data_realtime)
        
        self.summary_panel = ctk.CTkFrame(content_box, fg_color=self.summary_bg, width=380, corner_radius=30)
        self.summary_panel.pack(side="right", fill="y")
        self.summary_panel.pack_propagate(False)
        self.draw_confirmation_sidebar()
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(side="right", pady=(25, 0))
        
        ctk.CTkButton(btn_frame, text="Quay lại", 
                      height=55, width=140, corner_radius=18,
                      fg_color="white", 
                      text_color=self.accent_color, # Dùng màu ngành cho chữ
                      border_width=1, 
                      border_color=self.c("#DDDDDD"), 
                      hover_color=self.folder_color, # Hiệu ứng hover nhạt
                      font=("Garet Variable", 16, "bold"), 
                      command=self.go_back_to_step1).pack(side="left", padx=(0, 15))
        
        # Nút Xác nhận đặt lab
        self.btn_confirm_booking = ctk.CTkButton(btn_frame, text="Xác nhận đặt lab", 
                                                 height=55, width=240, corner_radius=18,
                                                 # Áp dụng màu chính của ngành
                                                 fg_color=self.accent_color,
                                                 hover_color=self.c("#2E3A6E"), # Màu đậm khi hover
                                                 font=("Garet Variable", 18, "bold"), 
                                                 command=self.process_booking)
        self.btn_confirm_booking.pack(side="left", fill="x", expand=True)
        
        self.sync_data_realtime()
    
    def draw_confirmation_sidebar(self):
        for w in self.summary_panel.winfo_children():
            w.destroy()
        
        inner = ctk.CTkFrame(self.summary_panel, fg_color="transparent")
        inner.pack(padx=35, pady=30, fill="both", expand=True)
        
        ctk.CTkLabel(inner, text="👤  Xác nhận thông tin", text_color="white", font=("Garet Variable", 20, "bold")).pack(anchor="w", pady=(0, 25))
        
        slot_display = self.booking_data["slot"]
        
        details = [
            ("NGƯỜI ĐẶT", self.ho_ten),
            ("THỜI GIAN", f"{slot_display} | {self.booking_data['date_display']}"),
            ("SỐ LƯỢNG", f"{self.booking_data['people']} người")
        ]
        
        for label, val in details:
            ctk.CTkLabel(inner, text=label, text_color=self.c("#9FA8DA"), font=("Garet Variable", 10, "bold")).pack(anchor="w")
            ctk.CTkLabel(inner, text=val, text_color="white", font=("Garet Variable", 14, "bold"), wraplength=300, justify="left").pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(inner, text="DANH SÁCH THÀNH VIÊN", text_color=self.c("#9FA8DA"), font=("Garet Variable", 10, "bold")).pack(anchor="w", pady=(10, 5))
        
        mem_frame = ctk.CTkScrollableFrame(inner, fg_color="transparent", height=150)
        mem_frame.pack(fill="x")
        
        if not self.booking_data.get("members_list"):
            ctk.CTkLabel(mem_frame, text="*Vui lòng nhập đúng định dạng:\n[MSSV] - [Họ và Tên]\n(VD: 31251... - Nguyễn Văn A)",
                         text_color=self.c("#C5CAE9"), font=("Garet Variable", 12, "italic"), justify="left").pack(anchor="w")
        else:
            for i, mem in enumerate(self.booking_data["members_list"]):
                ctk.CTkLabel(mem_frame, text=f"{i+1}. {mem}", text_color="white", font=("Garet Variable", 12, "bold")).pack(anchor="w", pady=2)
        
        ctk.CTkLabel(inner, text="Vui lòng có mặt trước 5 phút giờ\nđặt lab để xác nhận!",
                     text_color=self.c("#C5CAE9"), font=("Garet Variable", 12, "italic"), justify="center").pack(side="bottom", pady=20)
    
    def update_reason(self, val):
        self.booking_data["reason"] = val
        self.sync_data_realtime()
    
    def update_count(self, delta):
        nv = self.booking_data["people"] + delta
        if 1 <= nv <= 10:
            self.booking_data["people"] = nv
            self.lbl_p_count.configure(text=str(nv))
            self.lbl_mssv_hint.configure(text=f"THÔNG TIN THÀNH VIÊN (Cần nhập đủ {nv} người, VD: {self.mssv} - {self.ho_ten})")
            self.sync_data_realtime()
    
    def sync_data_realtime(self, event=None):
        raw_text = self.mssv_box.get("1.0", "end-1c").strip()
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        is_valid_format = True
        parsed_members = []
        
        for line in lines:
            if "-" in line:
                parts = line.split("-", 1)
                mssv_part = parts[0].strip()
                name_part = parts[1].strip()
                if len(mssv_part) > 0 and len(name_part) > 0:
                    parsed_members.append(f"{mssv_part} - {name_part}")
                else:
                    is_valid_format = False
            else:
                is_valid_format = False
        
        self.booking_data["members_list"] = parsed_members
        self.draw_confirmation_sidebar()
        
        has_reason = self.booking_data["reason"] != "--Xin hãy chọn lý do--"
        has_correct_count = (len(parsed_members) == self.booking_data["people"])
        
        if has_reason and is_valid_format and has_correct_count:
            self.btn_confirm_booking.configure(fg_color=self.accent_color, state="normal")
        else:
            self.btn_confirm_booking.configure(fg_color=self.disabled_color, state="disabled")
    
    def go_back_to_step1(self):
        self.view_state = "LAB_STEP1"
        self.render_view()
    
    def process_booking(self):
        """Tạo ID đặt phòng: olab + ca + ngày + tháng + 2 số cuối năm"""
        
        ngay_dat = self.booking_data["date_sql"]
        date_obj = datetime.strptime(ngay_dat, "%Y-%m-%d")
        ngay = date_obj.day
        thang = date_obj.month
        nam_2so = date_obj.year % 100
        
        khung_gio = self.booking_data.get("slot_db", self.booking_data["slot"])
        if "7:30" in khung_gio:
            ca = "a"
        elif "12:30" in khung_gio:
            ca = "b"
        elif "16:30" in khung_gio:
            ca = "c"
        else:
            ca = "x"
        
        self.current_booking_id = f"olab{ca}{ngay:02d}{thang:02d}{nam_2so:02d}"
        
        so_thanh_vien = self.booking_data["people"]
        ds_tv = "\n".join(self.booking_data["members_list"])
        
        # Truyền thêm booking_code
        self.db.add_booking(ngay_dat, khung_gio, so_thanh_vien, ds_tv, self.current_booking_id)
        
        self.view_state = "LAB_SUCCESS"
        self.render_view()
    
    def draw_lab_success(self):
        container = ctk.CTkFrame(self.workspace, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60, pady=40)
        
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="OpenLab", font=("Garet Variable", 42, "bold"), text_color=self.text_dark).pack(side="left")
        ctk.CTkButton(header, text="Lịch sử đặt lab", fg_color="white", text_color="black", border_width=1,
                      border_color="gray", height=40, corner_radius=12, font=("Garet Variable", 13),
                      command=self.show_history).pack(side="right")
        
        # Card chính
        f = ctk.CTkFrame(container, fg_color="white", corner_radius=45)
        f.pack(expand=True, fill="both", pady=20)
        
        # Frame icon (vòng tròn xanh)
        self.icon_frame = ctk.CTkFrame(f, fg_color=self.success_color, width=140, height=140, corner_radius=70)
        self.icon_frame.pack(pady=(60, 20))
        self.icon_frame.pack_propagate(False)
        
        # Label tick (sẽ chạy animation)
        self.tick_label = ctk.CTkLabel(self.icon_frame, text="", font=("Garet Variable", 10, "bold"), text_color="white")
        self.tick_label.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(f, text="Đã ghi nhận lịch đặt lab!", font=("Garet Variable", 28, "bold")).pack(pady=(10, 10))
        ctk.CTkLabel(f, text=f"Mã đặt phòng: {self.current_booking_id}", font=("Garet Variable", 20), text_color="gray").pack(pady=(0, 30))
        
        # Nút bấm
        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(side="bottom", anchor="e", padx=40, pady=40)
        
        ctk.CTkButton(btns, text="Huỷ lịch đặt lab", fg_color="white", text_color=self.danger_color,
                      border_width=1, border_color=self.danger_color, hover_color=self.c("#FDEDEC"),
                      height=50, width=170, corner_radius=18, font=("Garet Variable", 15, "bold"),
                      command=self.cancel_booking).pack(side="left", padx=(0, 15))
        ctk.CTkButton(btns, text="Về trang đặt lab", fg_color=self.accent_color, text_color="white", hover_color=self.c("#E9EBF8"),
                      height=50, width=200, corner_radius=18, font=("Garet Variable", 15, "bold"),
                      command=self.reset_and_go_home).pack(side="left")
        
        # Chạy animation
        self.animate_tick(10)
    
    def animate_tick(self, current_size):
        """Animation phóng to dấu tick"""
        if current_size < 70:
            current_size += 6
            if hasattr(self, "tick_label") and self.tick_label.winfo_exists():
                self.tick_label.configure(text="✓", font=("Garet Variable", current_size, "bold"))
                self.after(30, lambda: self.animate_tick(current_size))
    
    def cancel_booking(self):
        """Hủy lịch đặt lab đang hoạt động của user hiện tại"""
        bookings = self.db.get_my_bookings()
        if bookings:
            # Chỉ lấy booking ĐANG HOẠT ĐỘNG (TRANGTHAI=1)
            active_bookings = [b for b in bookings if b[5] == 1]
            if active_bookings:
                latest_booking = active_bookings[0]
                booking_id = latest_booking[0]
                self.db.cancel_booking(booking_id)
                messagebox.showinfo("Thành công", "Đã hủy lịch đặt lab!")
            else:
                messagebox.showwarning("Thông báo", "Bạn không có lịch đặt lab đang hoạt động!")
        else:
            messagebox.showwarning("Thông báo", "Bạn chưa có lịch đặt lab nào!")
        
        self.reset_and_go_home()
    
    def show_history(self):
        self.view_state = "LAB_HISTORY"
        self.render_view()
    
    def draw_lab_history(self):
        container = ctk.CTkFrame(self.workspace, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=80, pady=60)
        ctk.CTkLabel(container, text="OpenLab", font=("Garet Variable", 45, "bold")).pack(anchor="w")
        ctk.CTkLabel(container, text="LỊCH SỬ ĐẶT LAB", font=("Garet Variable", 20, "bold"), text_color=self.accent_color).pack(anchor="w", pady=(0, 45))
        
        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        bookings = self.db.get_my_bookings()
        
        if not bookings:
            ctk.CTkLabel(scroll, text="Chưa có lịch đặt lab nào", font=("Garet Variable", 14), text_color="gray").pack(pady=50)
        else:
            for item in bookings:
                booking_id = item[0]
                ngay_dat = item[1]
                khung_gio = item[2]
                so_thanh_vien = item[3]
                ds_tv = item[4]
                trangthai = item[5]
                booking_code = item[6] if len(item) > 6 else None  # Lấy mã đẹp nếu có
                
                try:
                    if isinstance(ngay_dat, datetime):
                        display_date = ngay_dat.strftime("%d/%m/%Y")
                    else:
                        date_obj = datetime.strptime(str(ngay_dat), "%Y-%m-%d")
                        display_date = date_obj.strftime("%d/%m/%Y")
                except:
                    display_date = str(ngay_dat)
                
                status_text = "Đã xác nhận" if trangthai == 1 else "Đã hủy"
                status_color = self.success_color if trangthai == 1 else self.danger_color
                status_bg = self.c("#E8F8F5") if trangthai == 1 else self.c("#FDEDEC")
                
                # Hiển thị mã đẹp (booking_code) nếu có, nếu không thì hiển thị ID số
                display_id = booking_code if booking_code else f"ID: {booking_id}"
                
                card = ctk.CTkFrame(scroll, fg_color="white", height=130, corner_radius=30)
                card.pack(fill="x", pady=15)
                card.pack_propagate(False)
                ctk.CTkLabel(card, text="📝", font=("Garet Variable", 45), width=100).pack(side="left", padx=25)
                mid = ctk.CTkFrame(card, fg_color="transparent")
                mid.pack(side="left", fill="y", pady=25)
                ctk.CTkLabel(mid, text=f"OpenLab ID: {display_id}", font=("Garet Variable", 20, "bold")).pack(anchor="w")
                ctk.CTkLabel(mid, text=f"📅 {display_date}   🕒 {khung_gio}   👤 {so_thanh_vien} người",
                            font=("Garet Variable", 15), text_color="gray").pack(anchor="w")
                ctk.CTkButton(card, text=status_text, 
                            fg_color=status_bg,
                            text_color=status_color,
                            hover=False, 
                            width=160, height=48, corner_radius=18,
                            font=("Garet Variable", 15, "bold")).pack(side="right", padx=40)
        
        ctk.CTkButton(container, text="Quay lại", 
                      fg_color=self.accent_color, 
                      text_color="white", 
                      hover_color=self.c("#2E3A6E"),
                      height=55, width=220,
                      corner_radius=18, 
                      font=("Garet Variable", 16, "bold"), 
                      command=self.reset_and_go_home).pack(side="right", pady=20)
    
    def reset_and_go_home(self):
        today = datetime.now()
        self.booking_data = {
            "date_sql": today.strftime("%Y-%m-%d"),
            "date_display": today.strftime("%d/%m/%Y"),
            "slot": None,
            "slot_db": None,
            "reason": "--Xin hãy chọn lý do--",
            "people": 1,
            "members_list": []
        }
        self.view_state = "LAB_STEP1"
        self.render_view()

    def adjust_layout(self):
        self.update_idletasks()
        if self.view_state == "LAB_STEP1":
            self.draw_lab_step1()
        elif self.view_state == "LAB_STEP2":
            self.draw_lab_step2()
        elif self.view_state == "LAB_SUCCESS":
            self.draw_lab_success()
        elif self.view_state == "LAB_HISTORY":
            self.draw_lab_history()