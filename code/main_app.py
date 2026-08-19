# main_app.py
import customtkinter as ctk
from tkinter import messagebox
from database import Database

# Import các app con
from study_app import StudyAppPro
from training_program import TrainingProgramApp
from checklist_app import GraduationChecklistApp
from ai_advisor import AIAdvisorApp
from lab_app import LabBookingApp
from gpa_app import GPAApp
from login_app import LoginFrame
from themes import THEMES

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hútle - Hệ thống Quản lý Học tập")
        self.geometry("1400x900")
        
        from themes import THEMES
        self.theme = THEMES["Phân tích dữ liệu"] 
        self.configure(fg_color=self.theme.get("#FDF6E3"))
        self.db = Database()
        self.current_frame = None
        self.current_user = None
        self.current_content = None
        self.sidebar_visible = True
        
        # Hiển thị màn hình login
        self.show_login()
    
    def c(self, hex_code):
        """Hàm trợ giúp dịch màu từ theme"""
        if hasattr(self, 'theme') and self.theme:
            return self.theme.get(hex_code, hex_code)
        return hex_code
    
    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = LoginFrame(self, self.db, self.theme)
        self.current_frame.pack(fill="both", expand=True)
    
    def login_success(self, mssv, ho_ten):
        """Được gọi khi đăng nhập thành công"""
        self.current_user = mssv
        self.ho_ten = ho_ten
        self.db.set_current_user(mssv)
        
        # Lấy tên ngành từ DB
        try:
            student_info = self.db.get_student_info()
            ten_nganh = student_info[3] if student_info else "Phân tích dữ liệu"
        except:
            ten_nganh = "Phân tích dữ liệu"
        
        # Chọn bộ theme
        self.theme = THEMES.get(ten_nganh, THEMES["Phân tích dữ liệu"])
        accent_color = self.theme.get("#3F51B5", "#3F51B5")
        bg_color = self.theme.get("#FDF6E3", "#FDF6E3")
        white_color = self.theme.get("#FFFFFF", "#FFFFFF")
        
        # Xóa màn hình login
        if self.current_frame:
            self.current_frame.destroy()
        
        # Đổi màu nền chính
        self.configure(fg_color=bg_color)
        
        # === MÀN HÌNH WELCOME - CHIẾM TOÀN BỘ CỬA SỔ ===
        # Frame chính (card trắng ở giữa)
        self.welcome_card = ctk.CTkFrame(self, fg_color=white_color, corner_radius=30)
        self.welcome_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.55, relheight=0.6)
        
        # Vòng tròn icon
        icon_frame = ctk.CTkFrame(self.welcome_card, fg_color=accent_color, width=120, height=120, corner_radius=60)
        icon_frame.pack(pady=(50, 20))
        icon_frame.pack_propagate(False)
        
        self.welcome_icon = ctk.CTkLabel(icon_frame, text="", font=("Garet Variable", 10, "bold"), text_color="white")
        self.welcome_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Labels
        self.welcome_name = ctk.CTkLabel(self.welcome_card, text="", font=("Garet Variable", 28, "bold"), text_color=accent_color)
        self.welcome_name.pack(pady=(10, 5))
        
        self.welcome_major = ctk.CTkLabel(self.welcome_card, text="", font=("Garet Variable", 18), text_color="gray")
        self.welcome_major.pack(pady=(0, 20))
        
        sub_label = ctk.CTkLabel(self.welcome_card, text="Chào mừng bạn đến với Hútle",
                                 font=("Garet Variable", 14, "bold"), text_color=self.theme.get("#95A5A6", "#95A5A6"))
        sub_label.pack(pady=(10, 30))
        
        # Progress bar
        self.welcome_progress = ctk.CTkProgressBar(self.welcome_card, width=350, height=10,
                                                    fg_color=self.theme.get("#E0E0E0", "#E0E0E0"),
                                                    progress_color=accent_color)
        self.welcome_progress.pack(pady=10)
        self.welcome_progress.set(0)
        
        # Bắt đầu animation
        self.animate_welcome_icon(10)
    
    def animate_welcome_icon(self, size=10):
        """Animation icon welcome phóng to"""
        if size < 60:
            self.welcome_icon.configure(text="🎉", font=("Garet Variable", size, "bold"))
            self.after(30, lambda: self.animate_welcome_icon(size + 4))
        else:
            full_name = f"Xin chào, {self.ho_ten}!"
            full_major = f"Ngành {self.get_ten_nganh()}"
            
            def type_name(idx=0):
                if idx <= len(full_name):
                    self.welcome_name.configure(text=full_name[:idx])
                    self.after(50, lambda: type_name(idx + 1))
                else:
                    def type_major(idx2=0):
                        if idx2 <= len(full_major):
                            self.welcome_major.configure(text=full_major[:idx2])
                            self.after(50, lambda: type_major(idx2 + 1))
                        else:
                            self.animate_welcome_progress(0)
                    type_major()
            type_name()
    
    def animate_welcome_progress(self, val=0):
        """Animation progress bar chạy"""
        if val <= 1.0:
            self.welcome_progress.set(val)
            self.after(20, lambda: self.animate_welcome_progress(val + 0.02))
        else:
            self.after(500, self.finish_welcome)
    
    def finish_welcome(self):
        """Kết thúc welcome, chuyển sang main UI"""
        # Xóa card welcome
        self.welcome_card.destroy()
        # Tạo giao diện chính
        self.setup_main_ui()
        # Hiển thị mặc định Lớp học
        self.show_study()
    
    def get_ten_nganh(self):
        """Lấy tên ngành hiện tại"""
        try:
            student_info = self.db.get_student_info()
            return student_info[3] if student_info else "Phân tích dữ liệu"
        except:
            return "Phân tích dữ liệu"
    
    def setup_main_ui(self):
        """Tạo giao diện chính với sidebar và content frame"""
        
        # Toolbar chứa nút toggle
        self.toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)
        
        # Nút toggle
        self.btn_toggle = ctk.CTkButton(self.toolbar, text="◀", width=40, height=40,
                                        fg_color=self.c("#3F51B5"), text_color="white",
                                        corner_radius=8, font=("Garet Variable", 18, "bold"),
                                        command=self.toggle_sidebar)
        self.btn_toggle.pack(side="left", padx=10, pady=5)
        
        # Lấy tên ngành của sinh viên
        try:
            student_info = self.db.get_student_info()
            if student_info and len(student_info) > 3:
                ten_nganh = student_info[3]
            else:
                ten_nganh = "Sinh viên"
        except:
            ten_nganh = "Sinh viên"
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, fg_color=self.c("#E9EBF8"), width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="HÚTLE", font=("Garet Variable", 33, "bold"),
                     text_color=self.c("#3F51B5")).pack(pady=(40, 30))
        
        # User card
        user_card = ctk.CTkFrame(self.sidebar, fg_color="white", corner_radius=20)
        user_card.pack(fill="x", padx=20, pady=10)
        
        # Avatar (chữ cái đầu)
        initial = self.ho_ten[0].upper() if self.ho_ten else "U"
        ctk.CTkLabel(user_card, text=initial, fg_color=self.c("#3F51B5"), text_color="white",
                     width=45, height=45, corner_radius=12, font=("Garet Variable", 18, "bold")).pack(side="left", padx=15, pady=15)
        
        # Thông tin user
        info_frame = ctk.CTkFrame(user_card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=15)
        
        # Họ tên
        ctk.CTkLabel(info_frame, text=self.ho_ten, font=("Garet Variable", 14, "bold"),
                     text_color="#2C3E50", anchor="w").pack(anchor="w")
        
        # MSSV và Ngành
        ctk.CTkLabel(info_frame, text=f"{self.current_user}\n{ten_nganh}", font=("Garet Variable", 11),
                     text_color="#7F8C8D", justify="left").pack(anchor="w")
        
        # Menu buttons
        menus = [
            ("📚 Lớp học của tôi", self.show_study),
            ("📖 Chương trình học", self.show_training),
            ("📊 Theo dõi GPA", self.show_gpa),
            ("✅ Check List", self.show_checklist),
            ("🤖 AI Advisor", self.show_ai),
            ("🔬 Book phòng lab", self.show_lab),
            ("🚪 Đăng xuất", self.logout)
        ]
        
        self.menu_btns = {}
        for text, command in menus:
            btn = ctk.CTkButton(self.sidebar, text=f"  {text}", anchor="w", height=45,
                                fg_color="transparent", text_color="#5D6D7E",
                                hover_color=self.c("#D1D5F0"), corner_radius=12,
                                font=("Garet Variable", 14), command=command)
            btn.pack(fill="x", pady=4, padx=20)
            self.menu_btns[text] = btn
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True)
    
    def toggle_sidebar(self):
        """Ẩn/hiện sidebar"""
        if not hasattr(self, 'sidebar'):
            return
        
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
            self.btn_toggle.configure(text="☰")
        else:
            self.sidebar.pack(side="left", fill="y", before=self.content_frame)
            self.sidebar_visible = True
            self.btn_toggle.configure(text="◀")
        
        self.content_frame.update_idletasks()
        if self.current_content and hasattr(self.current_content, 'adjust_layout'):
            self.current_content.adjust_layout()
    
    def clear_content(self):
        """Xóa nội dung content frame"""
        if self.current_content:
            try:
                self.current_content.destroy()
            except:
                pass
        for w in self.content_frame.winfo_children():
            w.destroy()
    
    def highlight_menu(self, selected_text):
        """Highlight menu được chọn"""
        for text, btn in self.menu_btns.items():
            if text == selected_text:
                btn.configure(fg_color="white", text_color=self.c("#3F51B5"), font=("Garet Variable", 14, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#5D6D7E", font=("Garet Variable", 14, "normal"))
    
    # ==================== CÁC MODULE ====================
    
    def show_study(self):
        self.clear_content()
        self.highlight_menu("📚 Lớp học của tôi")
        app = StudyAppPro(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def show_training(self):
        self.clear_content()
        self.highlight_menu("📖 Chương trình học")
        app = TrainingProgramApp(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def show_gpa(self):
        self.clear_content()
        self.highlight_menu("📊 Theo dõi GPA")
        app = GPAApp(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def show_checklist(self):
        self.clear_content()
        self.highlight_menu("✅ Check List")
        app = GraduationChecklistApp(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def show_ai(self):
        self.clear_content()
        self.highlight_menu("🤖 AI Advisor")
        app = AIAdvisorApp(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def show_lab(self):
        self.clear_content()
        self.highlight_menu("🔬 Book phòng lab")
        app = LabBookingApp(self.content_frame, self.db, self.current_user, self.ho_ten, self.theme)
        app.pack(fill="both", expand=True)
        self.current_content = app
    
    def logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            if hasattr(self, 'sidebar'):
                self.sidebar.destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()
            if hasattr(self, 'content_frame'):
                self.content_frame.destroy()
            if hasattr(self, 'welcome_card'):
                self.welcome_card.destroy()
            self.show_login()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()