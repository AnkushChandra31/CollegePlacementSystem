"""Placement workflow using stored student records from SQLite."""

from data_structures import PriorityQueue, Queue
from database import PlacementDatabase
from student import Student


class PlacementSystem:
    def __init__(self, database_path="placement_system.db"):
        self.database = PlacementDatabase(database_path)

    def add_student(self, student_id, name, email, cgpa, backlogs, branch, skills):
        if student_id <= 0:
            raise ValueError("Student ID must be a positive number.")
        if not name.strip() or not email.strip() or not branch.strip() or not skills:
            raise ValueError("Name, email, branch, and at least one skill are required.")
        if not 0 <= cgpa <= 10:
            raise ValueError("CGPA must be between 0 and 10.")
        if backlogs < 0:
            raise ValueError("Backlogs cannot be negative.")

        student = Student(student_id, name, email, cgpa, backlogs, branch, skills)
        self.database.add_student(student)
        return student

    def get_students(self):
        return self.database.get_students()

    def shortlist(self, company, save_criteria=True):
        """Shortlist students already saved in the database."""
        if save_criteria:
            self.database.add_company_criteria(company)
        applications = Queue()
        ranking = PriorityQueue()

        for student in self.get_students():
            applications.enqueue(student)

        while not applications.is_empty():
            student = applications.dequeue()
            if company.check_application(student):
                ranking.insert(student)

        selected_students = []
        while not ranking.is_empty():
            selected_students.append(ranking.remove())
        return selected_students

    def preview_shortlist(self, company):
        """Check matches without saving temporary criteria to the database."""
        return self.shortlist(company, save_criteria=False)
