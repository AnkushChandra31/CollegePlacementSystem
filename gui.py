import os
import smtplib
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from company import Company
from notification import send_email
from placement_system import PlacementSystem

FONT = "Segoe UI"
GLASS = "#FFFFFF"
GLASS_ALT = "#F7F7F7"
GLASS_LIGHT = "#EAEAEA"
FIELD = "#FFFFFF"
BORDER = "#D8D8D8"
BORDER_DIM = "#C6C6C6"
TEXT = "#202020"
MUTED = "#666666"
PINK = "#4A4A4A"
PINK_HOVER = "#303030"
CYAN = "#555555"
AMBER = "#666666"
VIOLET = "#505050"
VIOLET_BTN = "#3F3F3F"
VIOLET_HOVER = "#252525"
GREEN = "#2F6B3E"
RED = "#A33C3C"
BG_STOPS = ["#F6F6F6", "#F6F6F6"]
ORBS = []


def to_rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(v) for v in rgb)


def blend(first, second, amount):
    a, b = to_rgb(first), to_rgb(second)
    return to_hex([a[i] + (b[i] - a[i]) * amount for i in range(3)])


def gradient_color(stops, position):
    scaled = max(0.0, min(1.0, position)) * (len(stops) - 1)
    index = min(int(scaled), len(stops) - 2)
    return blend(stops[index], stops[index + 1], scaled - index)


def round_rect(canvas, x1, y1, x2, y2, radius, **options):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
        x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **options)


class Backdrop(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent, highlightthickness=0, bd=0)
        self.bind("<Configure>", self.paint)

    def paint(self, event=None):
        width, height = self.winfo_width(), self.winfo_height()
        if width < 10 or height < 10:
            return
        self.delete("all")
        for y in range(0, height, 4):
            self.create_rectangle(0, y, width, y + 4, fill=gradient_color(BG_STOPS, y / height), outline="")
        for fx, fy, radius, color in ORBS:
            base = gradient_color(BG_STOPS, fy)
            cx, cy = fx * width, fy * height
            for scale, amount in [(1.0, 0.16), (0.74, 0.26), (0.48, 0.38)]:
                r = radius * scale
                self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=blend(base, color, amount), outline="")


class Glass(tk.Frame):
    def __init__(self, parent, accent=VIOLET):
        super().__init__(parent, bg=GLASS, highlightbackground=BORDER, highlightthickness=1)
        tk.Frame(self, bg=accent, height=3).pack(fill="x")
        self.body = tk.Frame(self, bg=GLASS)
        self.body.pack(fill="both", expand=True, padx=16, pady=12)


class Pill(tk.Canvas):
    def __init__(self, parent, text, command, bg=GLASS, fill=PINK, hover=PINK_HOVER, fg=TEXT, width=170, height=38, size=10):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command, self.fill, self.hover, self.fg = text, command, fill, hover, fg
        self.w, self.h, self.size, self.enabled = width, height, size, True
        self.render(self.fill)
        self.bind("<Enter>", lambda _e: self.render(self.hover))
        self.bind("<Leave>", lambda _e: self.render(self.fill))
        self.bind("<Button-1>", self.click)

    def render(self, color):
        self.delete("all")
        if not self.enabled:
            color = "#BDBDBD"
        round_rect(self, 1, 1, self.w - 1, self.h - 1, self.h // 2, fill=color, outline="")
        self.create_text(self.w // 2, self.h // 2, text=self.text, fill=self.fg, font=(FONT, self.size, "bold"))

    def click(self, _event):
        if self.enabled and self.command:
            self.command()

    def restyle(self, fill, hover):
        self.fill, self.hover = fill, hover
        self.render(fill)

    def set_enabled(self, flag):
        self.enabled = flag
        self.render(self.fill)


class PlacementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Placement System")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 660)
        self.root.configure(bg="#F6F6F6")
        self.system = PlacementSystem()
        self.selected_students = []
        self.current_company = None
        self.student_fields = {}
        self.student_entries = {}
        self.company_fields = {}
        self.company_entries = {}
        self.pages = {}
        self.nav = {}
        self.active = None
        self.status_var = tk.StringVar(value="Ready")
        self.search_var = tk.StringVar()

        self.setup_styles()
        self.backdrop = Backdrop(self.root)
        self.backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        self.build_header()
        self.build_status()
        self.build_students_page()
        self.build_company_page()
        self.build_results_page()
        self.search_var.trace_add("write", lambda *_: self.refresh_students())
        self.refresh_students()
        self.update_preview()
        self.root.bind("<Configure>", self.on_resize)
        self.show_page("students")

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Glass.Treeview", background=GLASS, fieldbackground=GLASS, foreground=TEXT,
                        rowheight=30, borderwidth=0, font=(FONT, 10))
        style.configure("Glass.Treeview.Heading", background=VIOLET_BTN, foreground=TEXT,
                        font=(FONT, 10, "bold"), relief="flat", padding=(6, 7))
        style.map("Glass.Treeview", background=[("selected", PINK)], foreground=[("selected", TEXT)])
        style.map("Glass.Treeview.Heading", background=[("active", VIOLET_HOVER)])
        style.configure("Glass.Vertical.TScrollbar", background=GLASS_LIGHT, troughcolor=FIELD, bordercolor=GLASS,
                        arrowcolor=TEXT, lightcolor=GLASS_LIGHT, darkcolor=GLASS_LIGHT)

    def build_header(self):
        self.header = tk.Frame(self.root, bg=GLASS, highlightbackground=BORDER, highlightthickness=1)
        left = tk.Frame(self.header, bg=GLASS)
        left.pack(side="left", padx=18)
        tk.Label(left, text="✦ PlaceHub", bg=GLASS, fg=TEXT, font=(FONT, 16, "bold")).pack(anchor="w", pady=(8, 0))
        tk.Label(left, text="College Placement System", bg=GLASS, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        right = tk.Frame(self.header, bg=GLASS)
        right.pack(side="right", padx=14)
        for key, text in [("results", "Shortlist"), ("company", "Company"), ("students", "Students")]:
            pill = Pill(right, text, lambda k=key: self.show_page(k), bg=GLASS, fill=GLASS_LIGHT, hover="#D8D8D8", width=130)
            pill.pack(side="right", padx=4, pady=12)
            self.nav[key] = pill

    def build_status(self):
        self.status = tk.Label(self.root, textvariable=self.status_var, bg="#EAEAEA", fg=MUTED,
                               anchor="w", padx=16, font=(FONT, 9))

    def make_entry(self, parent, variable, show=None, width=None):
        options = {"width": width} if width else {}
        return tk.Entry(parent, textvariable=variable, show=show, font=(FONT, 10), bg=FIELD, fg=TEXT,
                        insertbackground=TEXT, relief="flat", highlightthickness=1,
                        highlightbackground=BORDER_DIM, highlightcolor=PINK, **options)

    def build_form(self, parent, rows, store, entries):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        for r, row in enumerate(rows):
            span = 2 if len(row) == 1 else 1
            for c, (label, default) in enumerate(row):
                padx = (0, 0) if span == 2 else ((0, 6) if c == 0 else (6, 0))
                tk.Label(parent, text=label.upper(), bg=GLASS, fg=MUTED, font=(FONT, 8, "bold"),
                         anchor="w").grid(row=r * 2, column=c, columnspan=span, sticky="w", padx=padx, pady=(8, 2))
                variable = tk.StringVar(value=default)
                entry = self.make_entry(parent, variable)
                entry.grid(row=r * 2 + 1, column=c, columnspan=span, sticky="ew", padx=padx, ipady=6)
                store[label] = variable
                entries[label] = entry

    def make_table(self, parent, columns):
        wrap = tk.Frame(parent, bg=GLASS)
        wrap.pack(fill="both", expand=True, pady=(8, 0))
        tree = ttk.Treeview(wrap, columns=[c[0] for c in columns], show="headings",
                            selectmode="browse", style="Glass.Treeview")
        for column, title, width in columns:
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="center")
        tree.tag_configure("odd", background=GLASS_ALT)
        tree.tag_configure("even", background=GLASS)
        scrollbar = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview, style="Glass.Vertical.TScrollbar")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def make_stat(self, title, accent):
        card = Glass(self.root, accent)
        tk.Label(card.body, text=title.upper(), bg=GLASS, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")
        value = tk.Label(card.body, text="0", bg=GLASS, fg=accent, font=(FONT, 24, "bold"))
        value.pack(anchor="w")
        return card, value

    def build_students_page(self):
        form = Glass(self.root, PINK)
        tk.Label(form.body, text="New Student", bg=GLASS, fg=TEXT, font=(FONT, 14, "bold")).pack(anchor="w")
        tk.Label(form.body, text="Saved straight to the database", bg=GLASS, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        grid = tk.Frame(form.body, bg=GLASS)
        grid.pack(fill="x")
        rows = [
            [("Student ID", ""), ("CGPA", "")],
            [("Name", "")],
            [("Email", "")],
            [("Backlogs", "0"), ("Branch", "BCA")],
            [("Skills (comma separated)", "Python")],
        ]
        self.build_form(grid, rows, self.student_fields, self.student_entries)
        Pill(form.body, "＋  Save Student", self.add_student, bg=GLASS, width=230).pack(anchor="w", pady=(16, 0))

        total_card, self.total_label = self.make_stat("Total students", PINK)
        avg_card, self.avg_label = self.make_stat("Average CGPA", CYAN)
        branch_card, self.branch_label = self.make_stat("Branches", AMBER)

        table_card = Glass(self.root, VIOLET)
        head = tk.Frame(table_card.body, bg=GLASS)
        head.pack(fill="x")
        tk.Label(head, text="Stored Students", bg=GLASS, fg=TEXT, font=(FONT, 14, "bold")).pack(side="left")
        self.make_entry(head, self.search_var, width=24).pack(side="right", ipady=4)
        tk.Label(head, text="⌕ Search", bg=GLASS, fg=MUTED, font=(FONT, 9)).pack(side="right", padx=(0, 8))
        self.student_table = self.make_table(table_card.body, [
            ("id", "ID", 60), ("name", "Name", 150), ("cgpa", "CGPA", 60),
            ("backlogs", "Backlogs", 70), ("branch", "Branch", 80), ("skills", "Skills", 200),
        ])

        self.pages["students"] = [
            (form, 0, 0, 0.34, 1), (total_card, 0.34, 0, 0.22, 0.23), (avg_card, 0.56, 0, 0.22, 0.23),
            (branch_card, 0.78, 0, 0.22, 0.23), (table_card, 0.34, 0.23, 0.66, 0.77),
        ]

    def build_company_page(self):
        form = Glass(self.root, CYAN)
        tk.Label(form.body, text="Company Requirements", bg=GLASS, fg=TEXT, font=(FONT, 14, "bold")).pack(anchor="w")
        tk.Label(form.body, text="Students who meet every rule are shortlisted automatically",
                 bg=GLASS, fg=MUTED, font=(FONT, 9)).pack(anchor="w")
        grid = tk.Frame(form.body, bg=GLASS)
        grid.pack(fill="x")
        rows = [
            [("Company", "TCS"), ("Job Role", "Software Developer")],
            [("Minimum CGPA", "7.5"), ("Maximum Backlogs", "0")],
            [("Branch", "BCA"), ("Required Skills", "Python")],
        ]
        self.build_form(grid, rows, self.company_fields, self.company_entries)
        Pill(form.body, "🔎  Find Eligible Students", self.shortlist_students, bg=GLASS,
             fill=VIOLET_BTN, hover=VIOLET_HOVER, width=260, height=42).pack(anchor="w", pady=(20, 0))

        preview = Glass(self.root, AMBER)
        tk.Label(preview.body, text="LIVE PREVIEW", bg=GLASS, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")
        self.pv_company = tk.StringVar()
        self.pv_role = tk.StringVar()
        self.pv_details = tk.StringVar()
        self.pv_count = tk.StringVar(value="0")
        tk.Label(preview.body, textvariable=self.pv_company, bg=GLASS, fg=TEXT, font=(FONT, 22, "bold")).pack(anchor="w", pady=(6, 0))
        tk.Label(preview.body, textvariable=self.pv_role, bg=GLASS, fg=CYAN, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(preview.body, textvariable=self.pv_details, bg=GLASS, fg=MUTED, font=(FONT, 10),
                 justify="left").pack(anchor="w", pady=(12, 0))

        match = Glass(self.root, GREEN)
        tk.Label(match.body, text="MATCHING STUDENTS RIGHT NOW", bg=GLASS, fg=MUTED, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(match.body, textvariable=self.pv_count, bg=GLASS, fg=GREEN, font=(FONT, 38, "bold")).pack(anchor="w")
        tk.Label(match.body, text="Updates as you type. Press Find to open the shortlist.",
                 bg=GLASS, fg=MUTED, font=(FONT, 9)).pack(anchor="w")

        for variable in self.company_fields.values():
            variable.trace_add("write", self.update_preview)

        self.pages["company"] = [(form, 0, 0, 0.55, 1), (preview, 0.55, 0, 0.45, 0.58), (match, 0.55, 0.58, 0.45, 0.42)]

    def build_results_page(self):
        table_card = Glass(self.root, VIOLET)
        head = tk.Frame(table_card.body, bg=GLASS)
        head.pack(fill="x")
        tk.Label(head, text="Eligible Students", bg=GLASS, fg=TEXT, font=(FONT, 14, "bold")).pack(side="left")
        self.results_summary = tk.StringVar(value="No shortlist yet")
        self.results_label = tk.Label(head, textvariable=self.results_summary, bg=GLASS, fg=MUTED, font=(FONT, 10, "bold"))
        self.results_label.pack(side="right")
        self.results = self.make_table(table_card.body, [
            ("id", "Student ID", 90), ("name", "Name", 190), ("cgpa", "CGPA", 80), ("email", "Email", 320),
        ])

        email_card = Glass(self.root, PINK)
        body = email_card.body
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        tk.Label(body, text="YOUR GMAIL", bg=GLASS, fg=MUTED, font=(FONT, 8, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(body, text="GMAIL APP PASSWORD", bg=GLASS, fg=MUTED, font=(FONT, 8, "bold")).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.sender_var = tk.StringVar(value=os.getenv("PLACEMENT_SENDER_EMAIL", ""))
        self.password_var = tk.StringVar(value=os.getenv("PLACEMENT_EMAIL_APP_PASSWORD", ""))
        self.make_entry(body, self.sender_var).grid(row=1, column=0, sticky="ew", ipady=6, pady=(2, 0))
        self.password_entry = self.make_entry(body, self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", ipady=6, padx=(10, 0), pady=(2, 0))
        self.show_pw = tk.BooleanVar(value=False)
        tk.Checkbutton(body, text="Show", variable=self.show_pw, command=self.toggle_password, bg=GLASS, fg=TEXT,
                       selectcolor=FIELD, activebackground=GLASS, activeforeground=TEXT, bd=0,
                       highlightthickness=0, font=(FONT, 9)).grid(row=1, column=2, padx=10)
        self.send_button = Pill(body, "✉  Send Emails", self.send_shortlist_emails, bg=GLASS)
        self.send_button.grid(row=1, column=3, padx=(0, 8), pady=(2, 0))
        Pill(body, "Clear", self.clear_results, bg=GLASS, fill=GLASS_LIGHT, hover="#D8D8D8", width=100).grid(row=1, column=4, pady=(2, 0))

        self.pages["results"] = [(table_card, 0, 0, 1, 0.76), (email_card, 0, 0.76, 1, 0.24)]

    def on_resize(self, event):
        if event.widget is self.root:
            self.layout()

    def layout(self):
        width, height = self.root.winfo_width(), self.root.winfo_height()
        if width < 200 or self.active is None:
            return
        self.header.place(x=24, y=18, width=width - 48, height=62)
        self.status.place(x=0, y=height - 26, width=width, height=26)
        gap = 16
        left, top = 24, 98
        area_w = width - 48
        area_h = height - top - 26 - 18
        for widget, fx, fy, fw, fh in self.pages[self.active]:
            widget.place(x=int(left + fx * (area_w + gap)), y=int(top + fy * (area_h + gap)),
                         width=int(fw * (area_w + gap) - gap), height=int(fh * (area_h + gap) - gap))

    def show_page(self, key):
        for name, items in self.pages.items():
            if name != key:
                for item in items:
                    item[0].place_forget()
        self.active = key
        for name, pill in self.nav.items():
            if name == key:
                pill.restyle(PINK, PINK_HOVER)
            else:
                pill.restyle(GLASS_LIGHT, "#D8D8D8")
        self.layout()

    def toggle_password(self):
        self.password_entry.configure(show="" if self.show_pw.get() else "*")

    def build_company(self):
        fields = self.company_fields
        skills = [s.strip() for s in fields["Required Skills"].get().split(",") if s.strip()]
        company_name = fields["Company"].get().strip()
        job_role = fields["Job Role"].get().strip()
        branch = fields["Branch"].get().strip()
        min_cgpa = float(fields["Minimum CGPA"].get())
        max_backlogs = int(fields["Maximum Backlogs"].get())
        if not company_name or not job_role or not branch or not skills:
            raise ValueError("Complete all company criteria fields.")
        if not 0 <= min_cgpa <= 10 or max_backlogs < 0:
            raise ValueError("Enter a CGPA from 0 to 10 and non-negative backlogs.")
        return Company(company_name, job_role, min_cgpa, max_backlogs, branch, skills)

    def update_preview(self, *_):
        fields = self.company_fields
        self.pv_company.set(fields["Company"].get().strip() or "Company")
        self.pv_role.set(fields["Job Role"].get().strip() or "Job role")
        self.pv_details.set(
            f"Min CGPA:  {fields['Minimum CGPA'].get().strip() or '-'}\n"
            f"Max backlogs:  {fields['Maximum Backlogs'].get().strip() or '-'}\n"
            f"Branch:  {fields['Branch'].get().strip() or '-'}\n"
            f"Skills:  {fields['Required Skills'].get().strip() or '-'}"
        )
        try:
            self.pv_count.set(str(len(self.system.preview_shortlist(self.build_company()))))
        except Exception:
            self.pv_count.set("–")

    def add_student(self):
        try:
            name = self.student_fields["Name"].get().strip()
            email = self.student_fields["Email"].get().strip()
            skills = [s.strip() for s in self.student_fields["Skills (comma separated)"].get().split(",") if s.strip()]
            if not name:
                raise ValueError("Enter the student's name.")
            if "@" not in email or email.startswith("@") or email.endswith("@"):
                raise ValueError("Enter a valid email address.")
            cgpa = float(self.student_fields["CGPA"].get())
            if not 0 <= cgpa <= 10:
                raise ValueError("CGPA must be between 0 and 10.")
            self.system.add_student(
                int(self.student_fields["Student ID"].get()), name, email, cgpa,
                int(self.student_fields["Backlogs"].get()),
                self.student_fields["Branch"].get().strip(), skills,
            )
        except (ValueError, sqlite3.IntegrityError) as error:
            messagebox.showerror("Invalid student details", str(error))
            return

        self.refresh_students()
        self.update_preview()
        self.status_var.set(f"Student '{name}' saved to the database.")
        for field in ("Student ID", "Name", "Email", "CGPA"):
            self.student_fields[field].set("")
        self.student_entries["Student ID"].focus_set()

    def refresh_students(self):
        students = list(self.system.get_students())
        self.total_label.configure(text=str(len(students)))
        average = sum(float(s.cgpa) for s in students) / len(students) if students else None
        self.avg_label.configure(text=f"{average:.2f}" if average is not None else "–")
        self.branch_label.configure(text=str(len({s.branch for s in students})))

        query = self.search_var.get().strip().lower()
        for item in self.student_table.get_children():
            self.student_table.delete(item)
        shown = 0
        for student in students:
            haystack = " ".join([str(student.student_id), student.name, student.branch, *student.skills]).lower()
            if query and query not in haystack:
                continue
            self.student_table.insert("", tk.END, tags=("odd" if shown % 2 else "even",), values=(
                student.student_id, student.name, student.cgpa, student.backlogs,
                student.branch, ", ".join(student.skills),
            ))
            shown += 1

    def shortlist_students(self):
        try:
            company = self.build_company()
        except ValueError as error:
            messagebox.showerror("Invalid company criteria", str(error))
            return

        self.clear_results()
        self.current_company = company
        self.selected_students = self.system.shortlist(company)
        for index, student in enumerate(self.selected_students):
            self.results.insert("", tk.END, tags=("odd" if index % 2 else "even",),
                                values=(student.student_id, student.name, student.cgpa, student.email))
        count = len(self.selected_students)
        self.results_summary.set(f"{count} eligible for {self.company_fields['Company'].get().strip()}")
        self.results_label.configure(fg=GREEN if count else RED)
        self.status_var.set(f"Shortlist complete: {count} student(s) matched.")
        self.show_page("results")
        if not self.selected_students:
            messagebox.showinfo("Shortlist complete", "No stored students meet the criteria.")

    def send_shortlist_emails(self):
        if not self.selected_students or self.current_company is None:
            messagebox.showerror("No shortlist", "Shortlist students before sending emails.")
            return
        sender_email = self.sender_var.get().strip()
        app_password = self.password_var.get().strip()
        if not sender_email or not app_password:
            messagebox.showerror("Email details missing", "Enter your Gmail address and Gmail App Password.")
            return

        students = list(self.selected_students)
        company = self.current_company
        self.send_button.set_enabled(False)
        self.status_var.set(f"Sending emails to {len(students)} student(s)...")

        def worker():
            sent_count, failed = 0, []
            for student in students:
                try:
                    send_email(student, company, sender_email, app_password)
                    sent_count += 1
                except (OSError, smtplib.SMTPException) as error:
                    failed.append(f"{student.name}: {error}")
            self.root.after(0, lambda: self.finish_sending(sent_count, failed))

        threading.Thread(target=worker, daemon=True).start()

    def finish_sending(self, sent_count, failed):
        self.send_button.set_enabled(True)
        if failed:
            self.status_var.set(f"Sent {sent_count}, failed {len(failed)}.")
            messagebox.showerror("Some emails were not sent", f"Sent: {sent_count}\n\n" + "\n".join(failed))
        else:
            self.status_var.set(f"Sent shortlist emails to {sent_count} student(s).")
            messagebox.showinfo("Emails sent", f"Sent shortlist emails to {sent_count} student(s).")

    def clear_results(self):
        for item in self.results.get_children():
            self.results.delete(item)
        self.selected_students = []
        self.current_company = None
        self.results_summary.set("No shortlist yet")
        self.results_label.configure(fg=MUTED)


if __name__ == "__main__":
    root = tk.Tk()
    PlacementApp(root)
    root.mainloop()
