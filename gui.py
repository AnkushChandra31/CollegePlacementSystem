"""Basic Tkinter user interface for the College Placement System."""

import os
import smtplib
import tkinter as tk
from tkinter import messagebox, ttk

from company import Company
from notification import send_email
from placement_system import PlacementSystem


class PlacementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Placement System")
        self.root.geometry("820x500")
        self.root.minsize(700, 420)
        self.root.resizable(True, True)
        self.system = PlacementSystem()

        self.student_fields = {}
        self.company_fields = {}
        self.selected_students = []
        self.current_company = None
        self.build_interface()

    def build_interface(self):
        ttk.Label(self.root, text="College Placement System", font=("Arial", 16, "bold")).pack(pady=(8, 2))
        ttk.Label(self.root, text="Add students, set criteria, then shortlist eligible candidates.").pack(pady=(0, 5))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        input_tab = ttk.Frame(self.notebook, padding=10)
        results_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(input_tab, text="Student and Company")
        self.notebook.add(results_tab, text="Shortlist and Email")

        form_area = ttk.Frame(input_tab)
        form_area.pack(fill="x")
        form_area.columnconfigure(0, weight=1)
        form_area.columnconfigure(1, weight=1)

        student_frame = ttk.LabelFrame(form_area, text="Add Student", padding=10)
        student_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        company_frame = ttk.LabelFrame(form_area, text="Company Criteria", padding=10)
        company_frame.grid(row=0, column=1, sticky="nsew")

        student_labels = [
            ("Student ID", ""), ("Name", ""), ("Email", ""), ("CGPA", ""),
            ("Backlogs", "0"), ("Branch", "BCA"), ("Skills (comma separated)", "Python"),
        ]
        for row, (label, default) in enumerate(student_labels):
            ttk.Label(student_frame, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(student_frame, width=25)
            entry.insert(0, default)
            entry.grid(row=row, column=1, pady=3)
            self.student_fields[label] = entry

        company_labels = [
            ("Company", "TCS"), ("Job Role", "Software Developer"), ("Minimum CGPA", "7.5"),
            ("Maximum Backlogs", "0"), ("Branch", "BCA"), ("Required Skills", "Python"),
        ]
        for row, (label, default) in enumerate(company_labels):
            ttk.Label(company_frame, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(company_frame, width=25)
            entry.insert(0, default)
            entry.grid(row=row, column=1, pady=3)
            self.company_fields[label] = entry

        button_area = ttk.Frame(input_tab, padding=(0, 12, 0, 0))
        button_area.pack()
        ttk.Button(button_area, text="Add Student", command=self.add_student).grid(row=0, column=0, padx=5)
        ttk.Button(button_area, text="Shortlist Students", command=self.shortlist_students).grid(row=0, column=1, padx=5)

        results_frame = ttk.LabelFrame(results_tab, text="Shortlisted Students", padding=10)
        results_frame.pack(fill="both", expand=True)
        self.results = ttk.Treeview(results_frame, columns=("id", "name", "cgpa", "email"), show="headings")
        for column, title, width in [
            ("id", "Student ID", 110), ("name", "Name", 180),
            ("cgpa", "CGPA", 80), ("email", "Email", 250),
        ]:
            self.results.heading(column, text=title)
            self.results.column(column, width=width, anchor="center")
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results.yview)
        self.results.configure(yscrollcommand=scrollbar.set)
        self.results.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        email_frame = ttk.LabelFrame(results_tab, text="Send Shortlist Emails", padding=8)
        email_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(email_frame, text="Your Gmail").grid(row=0, column=0, padx=(0, 5))
        self.sender_email = ttk.Entry(email_frame, width=32)
        self.sender_email.insert(0, os.getenv("PLACEMENT_SENDER_EMAIL", ""))
        self.sender_email.grid(row=0, column=1, padx=(0, 12))
        ttk.Label(email_frame, text="Gmail App Password").grid(row=0, column=2, padx=(0, 5))
        self.app_password = ttk.Entry(email_frame, width=22, show="*")
        self.app_password.insert(0, os.getenv("PLACEMENT_EMAIL_APP_PASSWORD", ""))
        self.app_password.grid(row=0, column=3, padx=(0, 12))
        ttk.Button(email_frame, text="Send Emails", command=self.send_shortlist_emails).grid(row=0, column=4)
        ttk.Button(email_frame, text="Clear Results", command=self.clear_results).grid(row=0, column=5, padx=(8, 0))

    def add_student(self):
        try:
            skills = [skill.strip() for skill in self.student_fields["Skills (comma separated)"].get().split(",") if skill.strip()]
            email = self.student_fields["Email"].get().strip()
            if "@" not in email or email.startswith("@") or email.endswith("@"):
                raise ValueError("Enter a valid email address.")
            self.system.add_student(
                int(self.student_fields["Student ID"].get()),
                self.student_fields["Name"].get().strip(),
                email,
                float(self.student_fields["CGPA"].get()),
                int(self.student_fields["Backlogs"].get()),
                self.student_fields["Branch"].get().strip(),
                skills,
            )
        except ValueError as error:
            messagebox.showerror("Invalid student details", str(error))
            return

        messagebox.showinfo("Student added", "Student added successfully.")
        for name in ("Student ID", "Name", "Email", "CGPA"):
            self.student_fields[name].delete(0, tk.END)

    def shortlist_students(self):
        try:
            required_skills = [skill.strip() for skill in self.company_fields["Required Skills"].get().split(",") if skill.strip()]
            company_name = self.company_fields["Company"].get().strip()
            job_role = self.company_fields["Job Role"].get().strip()
            branch = self.company_fields["Branch"].get().strip()
            min_cgpa = float(self.company_fields["Minimum CGPA"].get())
            max_backlogs = int(self.company_fields["Maximum Backlogs"].get())
            if not company_name or not job_role or not branch or not required_skills:
                raise ValueError("Complete all company criteria fields.")
            if not 0 <= min_cgpa <= 10:
                raise ValueError("Minimum CGPA must be between 0 and 10.")
            if max_backlogs < 0:
                raise ValueError("Maximum backlogs cannot be negative.")
            company = Company(
                company_name,
                job_role,
                min_cgpa,
                max_backlogs,
                branch,
                required_skills,
            )
        except ValueError as error:
            messagebox.showerror("Invalid company criteria", str(error))
            return

        self.clear_results()
        self.current_company = company
        self.selected_students = self.system.shortlist(company)
        for student in self.selected_students:
            self.results.insert("", tk.END, values=(student.student_id, student.name, student.cgpa, student.email))
        self.notebook.select(1)
        if not self.selected_students:
            messagebox.showinfo("Shortlist complete", "No students meet the selected criteria.")

    def send_shortlist_emails(self):
        if not self.selected_students or self.current_company is None:
            messagebox.showerror("No shortlist", "Shortlist students before sending emails.")
            return

        sender_email = self.sender_email.get().strip()
        app_password = self.app_password.get().strip()
        if not sender_email or not app_password:
            messagebox.showerror("Email details missing", "Enter your Gmail address and Gmail App Password.")
            return

        sent_count = 0
        failed_recipients = []
        for student in self.selected_students:
            try:
                send_email(student, self.current_company, sender_email, app_password)
                sent_count += 1
            except (OSError, smtplib.SMTPException) as error:
                failed_recipients.append(f"{student.name}: {error}")

        if failed_recipients:
            messagebox.showerror(
                "Some emails were not sent",
                f"Sent: {sent_count}\n\n" + "\n".join(failed_recipients),
            )
        else:
            messagebox.showinfo("Emails sent", f"Sent shortlist emails to {sent_count} student(s).")

    def clear_results(self):
        for item in self.results.get_children():
            self.results.delete(item)
        self.selected_students = []
        self.current_company = None


if __name__ == "__main__":
    root = tk.Tk()
    PlacementApp(root)
    root.mainloop()
