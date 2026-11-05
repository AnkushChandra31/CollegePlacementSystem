"""SQLite database functions for the College Placement System."""

import sqlite3

from student import Student


class PlacementDatabase:
    def __init__(self, database_path="placement_system.db"):
        self.database_path = database_path
        self.create_tables()
        self.seed_default_students()

    def connect(self):
        return sqlite3.connect(self.database_path)

    def create_tables(self):
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    cgpa REAL NOT NULL,
                    backlogs INTEGER NOT NULL,
                    branch TEXT NOT NULL,
                    skills TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS company_criteria (
                    criteria_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    job_role TEXT NOT NULL,
                    min_cgpa REAL NOT NULL,
                    max_backlogs INTEGER NOT NULL,
                    branch TEXT NOT NULL,
                    required_skills TEXT NOT NULL
                )
                """
            )

    def add_student(self, student):
        try:
            with self.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO students
                    (student_id, name, email, cgpa, backlogs, branch, skills)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        student.student_id,
                        student.name,
                        student.email,
                        student.cgpa,
                        student.backlogs,
                        student.branch,
                        ", ".join(student.skills),
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError("A student with this ID already exists in the database.") from error

    def seed_default_students(self):
        """Add missing starter records without changing existing student data."""
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT OR IGNORE INTO students
                (student_id, name, email, cgpa, backlogs, branch, skills)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (101, "Aarav Sharma", "aarav.sharma@example.com", 8.6, 0, "BCA", "Python, SQL, Java"),
                    (102, "Priya Singh", "priya.singh@example.com", 8.1, 0, "BCA", "Python, HTML, CSS"),
                    (103, "Rohan Patel", "rohan.patel@example.com", 7.2, 1, "BCA", "Java, SQL"),
                    (104, "Neha Verma", "neha.verma@example.com", 8.9, 0, "BCA", "Python, SQL, Django"),
                    (105, "Karan Mehta", "karan.mehta@example.com", 7.7, 0, "BCA", "C++, Java"),
                ],
            )

    def get_students(self):
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT student_id, name, email, cgpa, backlogs, branch, skills
                FROM students
                ORDER BY student_id
                """
            ).fetchall()
        return [
            Student(row[0], row[1], row[2], row[3], row[4], row[5], row[6].split(", "))
            for row in rows
        ]

    def add_company_criteria(self, company):
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO company_criteria
                (company_name, job_role, min_cgpa, max_backlogs, branch, required_skills)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    company.company_name,
                    company.job_role,
                    company.min_cgpa,
                    company.max_backlogs,
                    company.branch,
                    ", ".join(company.required_skills),
                ),
            )
