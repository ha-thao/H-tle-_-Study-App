# ai_advisor.py - ĐÃ SỬA LỖI FONT
import customtkinter as ctk
from groq import Groq
import threading

# ================== CẤU HÌNH API GROQ ==================
API_KEY = "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"
MODEL_NAME = "llama-3.3-70b-versatile"
# =======================================================

try:
    client = Groq(api_key=API_KEY)
    model_ok = True
except Exception as e:
    model_ok = False
    client = None

# Ngữ cảnh AI (System Prompt)
AI_CONTEXT = """
Bạn là 3i AI Advisor, trợ lý học tập thông minh thuộc Hútle App.
Nhiệm vụ: Tư vấn lộ trình học tập, đặt mục tiêu, định hướng kỹ năng cho sinh viên Việt Nam.
Thông tin: {user_name}, {user_year}, Ngành {user_major}.
Hãy trả lời nhiệt tình, chi tiết, sử dụng định dạng danh sách để dễ theo dõi.
"""


class AIAdvisorApp(ctk.CTkFrame):
    def __init__(self, parent, db, mssv, ho_ten, theme):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mssv = mssv
        self.ho_ten = ho_ten
        self.theme = theme

        
        # Lấy thông tin ngành của sinh viên từ database
        self.user_name = ho_ten
        self.user_major = self.get_student_major()
        self.user_year = self.get_student_year()
        
        # Bảng màu
        self.bg_color = "#FDF6E3"
        self.sidebar_color = self.c("#E9EBF8")
        self.accent_color = self.c("#3F51B5")
        self.bubble_ai = "#FFFFFF"
        self.bubble_user = self.c("#D1D5F0")
        self.text_main = "#2C3E50"
        
        self.setup_ui()
        self.after(600, self.greeting_message)

    def c(self, hex_code):
        return self.theme.get(hex_code, hex_code)
    
    def get_student_major(self):
        """Lấy tên ngành của sinh viên từ database"""
        info = self.db.get_student_info()
        if info:
            return info[3]  # TEN_NGANH
        return "Công nghệ thông tin"
    
    def get_student_year(self):
        """Xác định năm học dựa trên số học kỳ đã học"""
        grades = self.db.get_grades()
        semesters = set()
        for grade in grades:
            if len(grade) >= 7 and grade[6]:  # hoc_ky
                semesters.add(grade[6])
        
        so_ky = len(semesters)
        if so_ky <= 2:
            return "Năm nhất"
        elif so_ky <= 4:
            return "Năm hai"
        elif so_ky <= 6:
            return "Năm ba"
        else:
            return "Năm cuối"
    
    def setup_ui(self):
        # Main chat area
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(self.main_view, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(20, 10))
        
        ctk.CTkLabel(header, text="3i AI ADVISOR", font=("Garet Variable", 32, "bold"),
                     text_color=self.accent_color).pack(side="left")
        
        # Khung chứa hội thoại
        self.chat_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="transparent")
        self.chat_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Thanh chọn năm học nhanh
        quick_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        quick_frame.pack(fill="x", padx=40, pady=10)
        for y in ["Năm nhất", "Năm hai", "Năm ba", "Năm cuối"]:
            btn = ctk.CTkButton(quick_frame, text=y, width=90, height=30, corner_radius=15,
                                fg_color="white", text_color=self.accent_color, border_width=1,
                                border_color=self.sidebar_color, hover_color=self.sidebar_color,
                                font=("Garet Variable", 13), command=lambda val=y: self.update_year(val))
            btn.pack(side="left", padx=5)
        
        # Khu vực nhập liệu
        input_container = ctk.CTkFrame(self.main_view, fg_color="white", height=70, corner_radius=30)
        input_container.pack(fill="x", padx=40, pady=(0, 30))
        
        self.user_input = ctk.CTkEntry(input_container, placeholder_text="Hỏi advisor về lộ trình học tập...",
                                       height=50, border_width=0, fg_color="transparent", font=("Garet Variable", 14))
        self.user_input.pack(side="left", expand=True, fill="x", padx=20)
        self.user_input.bind("<Return>", self.send_message)
        
        self.send_btn = ctk.CTkButton(input_container, text="Gửi ➔", width=90, height=45, corner_radius=22,
                                      fg_color=self.accent_color, hover_color=self.c("#2E3A6E"), 
                                      font=("Garet Variable", 13), command=self.send_message)
        self.send_btn.pack(side="right", padx=10)
    
    def add_message(self, sender, text):
        is_ai = (sender == "AI")
        row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row.pack(fill="x", pady=10, padx=10)
        
        if is_ai:
            avatar_ai = ctk.CTkLabel(row, text="🤖", font=("Garet Variable", 22), width=40, height=40,
                                    fg_color=self.sidebar_color, corner_radius=20)
            avatar_ai.pack(side="left", anchor="s", padx=(0, 10))
            bubble = ctk.CTkFrame(row, fg_color=self.bubble_ai, corner_radius=20, 
                                border_width=1, border_color=self.c("#E0E0E0"))
            bubble.pack(side="left", anchor="w")
            txt_color = self.text_main
        else:
            bubble = ctk.CTkFrame(row, fg_color=self.bubble_user, corner_radius=20)
            bubble.pack(side="right", anchor="e")
            txt_color = self.accent_color
        
        # Xóa dấu **
        clean_text = text.replace('**', '')
        
        msg_lbl = ctk.CTkLabel(bubble, text=clean_text.strip(), wraplength=550, justify="left",
                            font=("Garet Variable", 14), text_color=txt_color, padx=15, pady=12)
        msg_lbl.pack()
        
        bubble.update_idletasks()
        self.after(10, lambda: self.chat_frame._parent_canvas.yview_moveto(1.0))
    
    def greeting_message(self):
        self.add_message("AI", f"Chào {self.user_name}! 👋 Mình là 3i AI Advisor. "
                               f"Hôm nay mình có thể giúp gì cho sinh viên {self.user_year} ngành {self.user_major} không?")
    
    def send_message(self, event=None):
        query = self.user_input.get().strip()
        if not query or not model_ok:
            if not model_ok:
                self.add_message("AI", "⚠️ Lỗi kết nối API. Vui lòng kiểm tra lại!")
            return
        self.add_message("Bạn", query)
        self.user_input.delete(0, "end")
        threading.Thread(target=self.get_ai_response, args=(query,), daemon=True).start()
    
    def get_ai_response(self, user_query):
        try:
            full_context = AI_CONTEXT.format(user_name=self.user_name, 
                                            user_year=self.user_year, 
                                            user_major=self.user_major)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": full_context}, 
                         {"role": "user", "content": user_query}],
                temperature=0.7
            )
            reply = response.choices[0].message.content
            self.after(0, lambda: self.add_message("AI", reply))
        except Exception as e:
            self.after(0, lambda: self.add_message("AI", f"Hệ thống đang bận một chút! ({str(e)})"))
    
    def update_year(self, year):
        self.user_year = year
        self.add_message("AI", f"Đã ghi nhận thay đổi: Bạn là sinh viên {year}. Hãy đặt câu hỏi nhé!")
    
    def adjust_layout(self):
        """Điều chỉnh layout khi sidebar thay đổi"""
        self.update_idletasks()
        # Chat frame tự động resize, không cần làm gì thêm
        pass