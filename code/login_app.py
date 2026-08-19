# login_app.py
import customtkinter as ctk
from tkinter import messagebox
from database import Database

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, db=None, theme=None):
        super().__init__(parent)
        self.theme = theme
        self.parent = parent
        self.db = db if db else Database()
        
        self.configure(fg_color="#FDF6E3")
        
        # Container chính
        container = ctk.CTkFrame(self, fg_color="white", corner_radius=30)
        container.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Tabview
        self.tabview = ctk.CTkTabview(container, fg_color="white",
                                       segmented_button_fg_color=self.c("#E9EBF8"),
                                       segmented_button_selected_color=self.c("#3F51B5"))
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        self.tabview.add("ĐĂNG NHẬP")
        self.tabview.add("ĐĂNG KÝ")
        self.tabview._segmented_button.configure(font=("Garet Variable", 13, "bold"))
        
        # === TAB ĐĂNG NHẬP ===
        self.setup_login_tab()
        
        # === TAB ĐĂNG KÝ ===
        self.setup_signup_tab()
        
        # Load danh sách ngành
        self.load_nganh_list()
    
    def c(self, hex_code):
        if self.theme:
            return self.theme.get(hex_code, hex_code)
        return hex_code
    
    def setup_login_tab(self):
        login_tab = self.tabview.tab("ĐĂNG NHẬP")
        
        ctk.CTkLabel(login_tab, text="Chào mừng đến với Hútle",
                    font=("Garet Variable", 16, "bold"), text_color=self.c("#3F51B5")).pack(pady=(40, 25))
        
        self.login_entry = ctk.CTkEntry(login_tab, placeholder_text="Email hoặc MSSV", font=("Garet Variable", 13),
                                        width=320, height=45, corner_radius=12)
        self.login_entry.pack(pady=10)
        
        self.login_password = ctk.CTkEntry(login_tab, placeholder_text="Mật khẩu", font=("Garet Variable", 13),
                                           show="*", width=320, height=45, corner_radius=12)
        self.login_password.pack(pady=10)
        
        self.login_password.update()
        self.login_password.bind("<Return>", lambda e: self.do_login())
        
        ctk.CTkButton(login_tab, text="Đăng nhập", fg_color=self.c("#3F51B5"), hover_color=self.c("#2E3A6E"), font=("Garet Variable", 16),
                    height=45, corner_radius=20, command=self.do_login).pack(pady=20, fill="x", padx=50)
        
        ctk.CTkLabel(login_tab, text="Chưa có tài khoản? Tạo tài khoản mới",
                    font=("Garet Variable", 16), text_color="gray").pack(pady=10)
        ctk.CTkButton(login_tab, text="Tạo tài khoản mới", fg_color="transparent",
                    text_color=self.c("#3F51B5"), hover_color=self.c("#D1D5F0"), border_width=1, border_color=self.c("#3F51B5"), font=("Garet Variable", 15),
                    height=40, corner_radius=20,
                    command=lambda: self.tabview.set("ĐĂNG KÝ")).pack(fill="x", padx=50)
        
    def setup_signup_tab(self):
        signup_tab = self.tabview.tab("ĐĂNG KÝ")
        
        ctk.CTkLabel(signup_tab, text="Tạo tài khoản mới",
                     font=("Garet Variable", 20, "bold"), text_color=self.c("#3F51B5")).pack(pady=(30, 20))
        
        self.signup_name = ctk.CTkEntry(signup_tab, placeholder_text="Họ và tên", font=("Garet Variable", 13),
                                        width=320, height=40, corner_radius=12)
        self.signup_name.pack(pady=8)
        
        self.signup_email = ctk.CTkEntry(signup_tab, placeholder_text="Email", font=("Garet Variable", 13),
                                         width=320, height=40, corner_radius=12)
        self.signup_email.pack(pady=8)
        
        self.signup_mssv = ctk.CTkEntry(signup_tab, placeholder_text="MSSV", font=("Garet Variable", 13),
                                        width=320, height=40, corner_radius=12)
        self.signup_mssv.pack(pady=8)
        
        self.signup_password = ctk.CTkEntry(signup_tab, placeholder_text="Mật khẩu", font=("Garet Variable", 13),
                                            show="*", width=320, height=40, corner_radius=12)
        self.signup_password.pack(pady=8)
        
        self.signup_confirm = ctk.CTkEntry(signup_tab, placeholder_text="Xác nhận mật khẩu", font=("Garet Variable", 13),
                                           show="*", width=320, height=40, corner_radius=12)
        self.signup_confirm.pack(pady=8)
        
        # Chọn ngành
        self.signup_nganh = ctk.CTkOptionMenu(signup_tab, values=[], width=320,
                                              font=("Garet Variable", 13), text_color="black",
                                              fg_color="light gray", button_color=self.c("#3F51B5"),      
                                              button_hover_color=self.c("#2E3A6E"), 
                                              dropdown_hover_color=self.c("#D1D5F0"))
        self.signup_nganh.pack(pady=8)
        
        ctk.CTkButton(signup_tab, text="Đăng ký", fg_color=self.c("#3F51B5"), font=("Garet Variable", 16),
                     height=40, corner_radius=20, command=self.do_signup).pack(pady=20, fill="x", padx=50)
    
    def load_nganh_list(self):
        nganh_list = self.db.get_nganh_list()
        nganh_values = [f"{n[0]} - {n[1]}" for n in nganh_list]
        self.signup_nganh.configure(values=nganh_values)
        if nganh_values:
            self.signup_nganh.set(nganh_values[0])
    
    def do_login(self):
        email_or_mssv = self.login_entry.get().strip()
        pwd = self.login_password.get()
        
        if not email_or_mssv or not pwd:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Email/MSSV và mật khẩu!")
            return
        
        result = self.db.login(email_or_mssv, pwd)
        if result:
            mssv, ho_ten, email, id_nganh = result
            self.db.set_current_user(mssv)
            self.parent.login_success(mssv, ho_ten)
        else:
            messagebox.showerror("Lỗi", "Email/MSSV hoặc mật khẩu không đúng!")
    
    def do_signup(self):
        ho_ten = self.signup_name.get().strip()
        email = self.signup_email.get().strip()
        mssv = self.signup_mssv.get().strip()
        pwd = self.signup_password.get()
        confirm = self.signup_confirm.get()
        nganh_str = self.signup_nganh.get()
        
        if not all([ho_ten, email, mssv, pwd]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ thông tin!")
            return
        
        if pwd != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        
        if len(mssv) < 10:
            messagebox.showwarning("Lỗi", "MSSV phải có ít nhất 10 ký tự!")
            return
        
        id_nganh = nganh_str.split(" - ")[0] if nganh_str else ""
        
        success, message = self.db.register(mssv, ho_ten, email, pwd, id_nganh)
        
        if success:
            messagebox.showinfo("Thành công", message + "\nVui lòng đăng nhập!")
            self.tabview.set("ĐĂNG NHẬP")
            self.signup_name.delete(0, 'end')
            self.signup_email.delete(0, 'end')
            self.signup_mssv.delete(0, 'end')
            self.signup_password.delete(0, 'end')
            self.signup_confirm.delete(0, 'end')
        else:
            messagebox.showerror("Lỗi", message)