# checklist_app.py - Bản đơn giản nhất, chắc chắn chạy
import customtkinter as ctk
from tkinter import messagebox


ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")




class GraduationChecklistApp(ctk.CTkFrame):
    def __init__(self, parent, db, mssv, ho_ten, theme):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.mssv = mssv
        self.ho_ten = ho_ten
        self.theme = theme


        self.accent_color = self.c("#3F51B5")
        self.cat_colors = {
            "Học tập": "#4CAF50",
            "Chứng chỉ": "#2196F3",
            "Cuộc thi": "#FF9800",
            "Khác": "#9C27B0"
        }


        self.tasks = []
        self.categories = ["Tất cả", "Học tập", "Chứng chỉ", "Cuộc thi", "Khác"]
        self.current_filter = "Tất cả"
        self.search_text = ""


        self.setup_ui()
        self.load_tasks()
       
    def c(self, hex_code):
        return self.theme.get(hex_code, hex_code)

    def load_tasks(self):
        try:
            rows = self.db.get_checklist()
            self.tasks = []
            for row in rows:
                check_id = row[0]
                danh_muc = row[1]
                ten_muc_tieu = row[2]
                ketqua = row[3] if row[3] else ""
               
                if ketqua == "Hoàn thành" or ketqua == "Done" or "|" in ketqua:
                    completed = True
                    actual = ketqua.split("|")[-1] if "|" in ketqua else ketqua
                    expected = ketqua.split("|")[0] if "|" in ketqua else ""
                else:
                    completed = False
                    actual = ""
                    expected = ketqua
               
                self.tasks.append({
                    "id": check_id,
                    "category": danh_muc,
                    "title": ten_muc_tieu,
                    "expected": expected,
                    "actual": actual,
                    "completed": completed
                })
            print(f"Loaded {len(self.tasks)} tasks")
        except Exception as e:
            print(f"Lỗi load_tasks: {e}")
            self.tasks = []
       
        self.render_tasks()


    def save_task(self, task):
        """Lưu task vào database"""
        try:
            # Lưu expected|actual
            actual = task["actual"] if task["completed"] else ""
            save_data = f"{task['expected']}|{actual}"
            hoan_thanh = 1 if task["completed"] else 0
           
            # Cập nhật cả KETQUA và HOAN_THANH
            self.db.cursor.execute("""
                UPDATE CHECKLIST
                SET KETQUA = ?, HOAN_THANH = ?
                WHERE ID_CHECK = ? AND MSSV = ?
            """, (save_data, hoan_thanh, task["id"], self.mssv))
            self.db.conn.commit()
            print(f"Saved task {task['id']}: completed={task['completed']}")
        except Exception as e:
            print(f"Lỗi save_task: {e}")


    def add_new_task(self, category, title, expected):
        """Thêm task mới"""
        try:
            self.db.cursor.execute("""
                INSERT INTO CHECKLIST (MSSV, DANH_MUC, TEN_MUC_TIEU, KETQUA, HOAN_THANH)
                VALUES (?, ?, ?, ?, 0)
            """, (self.mssv, category, title, expected))
            self.db.conn.commit()
            new_id = self.db.cursor.execute("SELECT @@IDENTITY").fetchone()[0]
            return new_id
        except Exception as e:
            print(f"Lỗi add_new_task: {e}")
            return None


    def delete_task_db(self, task_id):
        """Xóa task"""
        try:
            self.db.cursor.execute("DELETE FROM CHECKLIST WHERE ID_CHECK = ? AND MSSV = ?", (task_id, self.mssv))
            self.db.conn.commit()
        except Exception as e:
            print(f"Lỗi delete_task_db: {e}")


    def update_stats(self):
        """Tính phần trăm cho từng danh mục và tổng thể"""
        print("=== UPDATE STATS ===")
        
        # Tính % từng danh mục
        for cat in self.categories[1:]:
            cat_tasks = [t for t in self.tasks if t["category"] == cat]
            if cat_tasks:
                completed = len([t for t in cat_tasks if t["completed"]])
                percent = int((completed / len(cat_tasks)) * 100)
            else:
                percent = 100  # Không có mục tiêu -> 100% hoàn thành
            
            print(f"{cat}: {percent}%")
            
            if cat in self.cat_perc_labels:
                self.cat_perc_labels[cat].configure(text=f"{percent}%")
                self.cat_bars[cat].set(percent / 100)
        
        # Tính % tổng thể (trung bình các danh mục)
        active_cats = 0
        total_percent = 0
        for cat in self.categories[1:]:
            cat_tasks = [t for t in self.tasks if t["category"] == cat]
            if cat_tasks:
                active_cats += 1
                completed = len([t for t in cat_tasks if t["completed"]])
                total_percent += int((completed / len(cat_tasks)) * 100)
            # Nếu không có task, vẫn tính là 100% cho danh mục đó
            else:
                active_cats += 1
                total_percent += 100
        
        overall = int(total_percent / active_cats) if active_cats > 0 else 100
        print(f"Overall: {overall}%")
        
        if self.total_perc_label:
            self.total_perc_label.configure(text=f"{overall}%")
            self.total_bar.set(overall / 100)


    def toggle_task(self, task):
        task["completed"] = not task["completed"]
        if task["completed"]:
            task["actual"] = "Hoàn thành"
            save_data = f"{task['expected']}|{task['actual']}" if task['expected'] else "Hoàn thành"
        else:
            task["actual"] = ""
            save_data = task["expected"] if task['expected'] else ""
       
        try:
            self.db.update_checklist_result(task["id"], save_data)
        except Exception as e:
            print(f"Lỗi save: {e}")
       
        self.update_stats()
        self.render_tasks()


    # ==================== UI ====================
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)


        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))


        ctk.CTkLabel(header_frame, text="CHECKLIST RA TRƯỜNG",
                    font=("Garet Variable", 28, "bold"),
                    text_color=self.accent_color).pack(side="left")


        self.total_perc_label = ctk.CTkLabel(header_frame, text="0%",
                                            font=("Garet Variable", 32, "bold"),
                                            text_color=self.accent_color)
        self.total_perc_label.pack(side="right")


        # Progress bar tổng
        self.total_bar = ctk.CTkProgressBar(self.main_frame, height=8, corner_radius=4,
                                            fg_color="#E0E0E0", progress_color=self.accent_color)
        self.total_bar.pack(fill="x", pady=(0, 20))
        self.total_bar.set(0)


        # 4 thẻ danh mục
        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", border_color=self.c("#E0E0E0"))
        cards_frame.pack(fill="x", pady=10)
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
            
        self.cat_perc_labels = {}
        self.cat_bars = {}


        for i, cat in enumerate(self.categories[1:]):
            card = ctk.CTkFrame(cards_frame, fg_color=self.c("#FFFFFF"), corner_radius=15,
                                border_width=1, border_color=self.c("#E0E0E0"))
            card.grid(row=0, column=i, padx=5, sticky="nsew")


            ctk.CTkLabel(card, text=cat.upper(), font=("Garet Variable", 11, "bold"),
                        text_color=self.cat_colors.get(cat, self.accent_color)).pack(
                        pady=(12, 0), anchor="w", padx=15)


            perc_lbl = ctk.CTkLabel(card, text="0%", font=("Garet Variable", 22, "bold"),
                                    text_color=self.cat_colors.get(cat, self.accent_color))
            perc_lbl.pack(anchor="e", padx=15, pady=(5, 0))
           
            bar = ctk.CTkProgressBar(card, fg_color=self.c("#E0E0E0"),
                                    progress_color=self.cat_colors.get(cat, self.accent_color),
                                    height=6, corner_radius=3)
            bar.set(0)
            bar.pack(fill="x", padx=15, pady=(8, 15))
           
            self.cat_perc_labels[cat] = perc_lbl
            self.cat_bars[cat] = bar
            print(f"Đã tạo label cho {cat}")


        # Filter
        filter_frame = ctk.CTkFrame(self.main_frame, fg_color=self.c("#FFFFFF"), corner_radius=15,
                                    border_width=1, border_color=self.c("#E0E0E0"))
        filter_frame.pack(fill="x", pady=15)


        row1 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 10))


        ctk.CTkLabel(row1, text="Lọc theo:", font=("Garet Variable", 12, "bold")).pack(side="left")


        self.cat_menu = ctk.CTkOptionMenu(row1, values=self.categories,
                                        fg_color=self.c("#F0F0F0"), text_color="black", font=("Garet Variable", 13), dropdown_font=("Garet Variable", 13),
                                        button_color=self.accent_color, width=140,
                                        button_hover_color=self.c("#2E3A6E"),
                                        command=self.on_filter_change)
        self.cat_menu.pack(side="left", padx=10)


        ctk.CTkButton(row1, text="+ Thêm mục tiêu", fg_color=self.c("#27AE60"),
                    width=140, corner_radius=20, font=("Garet Variable", 13),
                    hover_color=self.c("#2E3A6E"),
                    command=self.open_add_modal).pack(side="right")


        row2 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(0, 15))


        ctk.CTkLabel(row2, text="Tìm kiếm:", font=("Garet Variable", 12, "bold")).pack(side="left")


        self.search_entry = ctk.CTkEntry(row2, placeholder_text="Nhập từ khóa...",
                                        font=("Garet Variable", 13),
                                        fg_color=self.c("#F0F0F0"), border_width=0, height=35)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.search_entry.bind("<Return>", lambda e: self.on_search())


        ctk.CTkButton(row2, text="🔍 Tìm kiếm", fg_color=self.accent_color,
                    width=100, corner_radius=20, font=("Garet Variable", 13),
                    hover_color=self.c("#2E3A6E"),
                    command=self.on_search).pack(side="right")


        # Header bảng
        table_header = ctk.CTkFrame(self.main_frame, fg_color=self.accent_color, corner_radius=10)
        table_header.pack(fill="x", pady=(10, 2))


        headers = ["", "MỤC TIÊU", "KẾT QUẢ", ""]
        header_widths = [50, 400, 130, 60]
        for col, (text, width) in enumerate(zip(headers, header_widths)):
            sticky_val = "w" if col == 1 else "ew"
            ctk.CTkLabel(table_header, text=text, font=("Garet Variable", 12, "bold"),
                        text_color="white", width=width).grid(
                        row=0, column=col, padx=10, pady=8, sticky=sticky_val)
        table_header.grid_columnconfigure(1, weight=1)


        # Container tasks
        self.tasks_container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.tasks_container.pack(fill="both", expand=True, pady=5)


        self.render_tasks()


    def on_filter_change(self, value):
        self.current_filter = value
        self.render_tasks()


    def on_search(self):
        self.search_text = self.search_entry.get().lower()
        self.render_tasks()


    def render_tasks(self):
        self.update_stats()

        for w in self.tasks_container.winfo_children():
            w.destroy()


        filtered = [t for t in self.tasks
                    if (self.current_filter == "Tất cả" or t["category"] == self.current_filter)
                    and (not self.search_text or self.search_text in t["title"].lower())]


        if not filtered:
            ctk.CTkLabel(self.tasks_container, text="📭 Không có mục tiêu nào",
                         font=("Garet Variable", 14), text_color="gray").pack(pady=50)
            return


        for i, task in enumerate(filtered):
            self.create_task_row(task, i)


    def create_task_row(self, task, index):
        bg_color = self.c("#F8F9FA") if index % 2 == 0 else self.c("#FFFFFF")
        row = ctk.CTkFrame(self.tasks_container, fg_color=bg_color, corner_radius=8, height=70)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)


        # Checkbox
        cb = ctk.CTkCheckBox(row, text="", width=20, checkbox_width=20, checkbox_height=20,
                             border_color=self.accent_color, fg_color=self.accent_color,
                             command=lambda t=task: self.toggle_task(t))
        if task["completed"]:
            cb.select()
        cb.grid(row=0, column=0, padx=(15, 5), pady=5)


        # Title
        title_color = "#A0A0A0" if task["completed"] else "#2C3E50"
        title_font = ("Garet Variable", 13, "bold", "overstrike") if task["completed"] else ("Garet Variable", 13, "bold")


        title_frame = ctk.CTkFrame(row, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=5)


        title_lbl = ctk.CTkLabel(title_frame, text=task["title"], font=title_font,
                                 text_color=title_color, anchor="w")
        title_lbl.pack(side="left")


        if task["expected"]:
            expected_lbl = ctk.CTkLabel(title_frame, text=f"  →  {task['expected']}",
                                        font=("Garet Variable", 11, "italic"),
                                        text_color="#A0A0A0", anchor="w")
            expected_lbl.pack(side="left")


        # Category
        cat_lbl = ctk.CTkLabel(row, text=f"📁 {task['category']}",
                               font=("Garet Variable", 10), text_color="#7F8C8D")
        cat_lbl.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 5))


        # Result
        result_text = task["actual"] if task["actual"] else "⋯"
        result_color = self.accent_color if task["completed"] else "#B0B0B0"
        result_lbl = ctk.CTkLabel(row, text=result_text, font=("Garet Variable", 12, "bold"),
                                  text_color=result_color, width=130)
        result_lbl.grid(row=0, column=2, padx=10, pady=5, rowspan=2)


        # Edit button
        edit_btn = ctk.CTkButton(row, text="✎", width=35, height=30,
                                 fg_color="transparent", text_color="#FF9800",
                                 hover_color="#F0F0F0", font=("Garet Variable", 14),
                                 command=lambda t=task: self.open_edit_modal(t))
        edit_btn.grid(row=0, column=3, padx=(5, 15), pady=5, rowspan=2)


        row.grid_columnconfigure(1, weight=1)


    # ==================== MODAL ====================
    def open_add_modal(self):
        self.show_modal("THÊM MỤC TIÊU MỚI")


    def open_edit_modal(self, task):
        self.show_modal("CHỈNH SỬA MỤC TIÊU", task)


    def show_modal(self, title, task=None):
        modal = ctk.CTkToplevel(self)
        modal.title(title)
        modal.geometry("550x600")
        modal.attributes("-topmost", True)
        modal.transient(self)
        modal.grab_set()
        modal.focus_force()


        modal.update_idletasks()
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 275
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 300
        modal.geometry(f"+{x}+{y}")


        container = ctk.CTkFrame(modal, fg_color=self.c("#FFFFFF"), corner_radius=30,
                                 border_width=2, border_color=self.accent_color)
        container.pack(fill="both", expand=True, padx=15, pady=15)


        header = ctk.CTkFrame(container, fg_color=self.accent_color, height=60, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=title, font=("Garet Variable", 18, "bold"),
                     text_color="white").pack(pady=15)


        form = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=20)


        # Category
        ctk.CTkLabel(form, text="📂 DANH MỤC", font=("Garet Variable", 12, "bold"),
                     text_color=self.accent_color).pack(anchor="w", pady=(0, 5))


        cat_var = ctk.StringVar(value=task["category"] if task else "Học tập")
        cat_menu = ctk.CTkOptionMenu(form, values=self.categories[1:], variable=cat_var, font=("Garet Variable", 13), dropdown_font=("Garet Variable", 13), text_color="black",
                                     fg_color=self.c("#F0F0F0"), button_color=self.accent_color,button_hover_color=self.c("#2E3A6E"),
                                     dropdown_hover_color=self.c("#D1D5F0"),
                                     width=400)
        cat_menu.pack(pady=(0, 15))


        # Title
        ctk.CTkLabel(form, text="🎯 MỤC TIÊU", font=("Garet Variable", 12, "bold"),
                     text_color=self.accent_color).pack(anchor="w", pady=(0, 5))


        title_entry = ctk.CTkEntry(form, placeholder_text="Nhập mục tiêu...",
                                   font=("Garet Variable", 13),
                                   fg_color=self.c("#F8F9FA"), border_width=1, border_color=self.c("#E0E0E0"),
                                   corner_radius=12, height=45, width=400)
        if task:
            title_entry.insert(0, task["title"])
        title_entry.pack(pady=(0, 15))


        # Expected result
        ctk.CTkLabel(form, text="📊 KẾT QUẢ KỲ VỌNG", font=("Garet Variable", 12, "bold"),
                     text_color=self.accent_color).pack(anchor="w", pady=(0, 5))


        exp_entry = ctk.CTkEntry(form, placeholder_text="VD: IELTS 7.0",
                                 font=("Garet Variable", 13),
                                 fg_color=self.c("#F8F9FA"), border_width=1, border_color=self.c("#E0E0E0"),
                                 corner_radius=12, height=45, width=400)
        if task and task["expected"]:
            exp_entry.insert(0, task["expected"])
        exp_entry.pack(pady=(0, 15))


        # Actual result (only for edit)
        actual_entry = None
        if task:
            ctk.CTkLabel(form, text="✅ KẾT QUẢ THỰC TẾ", font=("Garet Variable", 12, "bold"),
                         text_color=self.accent_color).pack(anchor="w", pady=(10, 5))
            actual_entry = ctk.CTkEntry(form, placeholder_text="Nhập kết quả thực tế...",
                                        font=("Garet Variable", 13),
                                        fg_color=self.c("#F8F9FA"), border_width=1, border_color=self.c("#E0E0E0"),
                                        corner_radius=12, height=45, width=400)
            if task["actual"]:
                actual_entry.insert(0, task["actual"])
            actual_entry.pack(pady=(0, 15))


        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=30)


        def save():
            cat = cat_var.get()
            title_text = title_entry.get().strip()
            expected = exp_entry.get().strip()


            if not title_text:
                messagebox.showwarning("Lỗi", "Vui lòng nhập mục tiêu!")
                return


            if task:
                # Update
                task["category"] = cat
                task["title"] = title_text
                task["expected"] = expected
                if actual_entry:
                    task["actual"] = actual_entry.get().strip()
                    task["completed"] = task["actual"] != ""
                self.save_task(task)
            else:
                # Add new
                new_id = self.add_new_task(cat, title_text, expected)
                if new_id:
                    self.tasks.append({
                        "id": new_id,
                        "category": cat,
                        "title": title_text,
                        "expected": expected,
                        "actual": "",
                        "completed": False
                    })


            self.update_stats()
            self.render_tasks()
            modal.destroy()
            messagebox.showinfo("Thành công", f"Đã {title.lower()}!")


        if task:
            del_btn = ctk.CTkButton(btn_frame, text="🗑 XÓA", fg_color="transparent", text_color="#E74C3C",
                                    border_width=2, border_color="#E74C3C", height=45, corner_radius=25,
                                    font=("Garet Variable", 13),
                                    hover_color=self.c("#2E3A6E"),
                                    command=lambda: self.delete_and_close(task, modal))
            del_btn.pack(side="left", fill="x", expand=True, padx=10)


        cancel_btn = ctk.CTkButton(btn_frame, text="HỦY", fg_color="transparent", text_color="gray",
                                   border_width=2, border_color="gray", height=45, corner_radius=25,
                                   font=("Garet Variable", 13), hover_color=self.c("#2E3A6E"),
                                   command=modal.destroy)
        cancel_btn.pack(side="left", fill="x", expand=True, padx=10)


        save_btn = ctk.CTkButton(btn_frame, text="LƯU", fg_color=self.accent_color,
                                 height=45, corner_radius=25, font=("Garet Variable", 13, "bold"),
                                 hover_color=self.c("#2E3A6E"),
                                 command=save)
        save_btn.pack(side="left", fill="x", expand=True, padx=10)


    def delete_and_close(self, task, modal):
        modal.destroy()
        if messagebox.askyesno("Xác nhận", f"Xóa mục tiêu '{task['title']}'?"):
            self.delete_task_db(task["id"])
            self.tasks.remove(task)
            self.update_stats()
            self.render_tasks()


    def adjust_layout(self):
        self.update_idletasks()
        self.render_tasks()