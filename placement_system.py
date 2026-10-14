"""Core placement-system logic shared by the interface."""

from data_structures import LinkedList, PriorityQueue, Queue
from student import Student


class PlacementSystem:
    def __init__(self):
        self.students = LinkedList()
        self.student_ids = set()

    def add_student(self, student_id, name, email, cgpa, backlogs, branch, skills):
        if student_id <= 0:
            raise ValueError("Student ID must be a positive number.")
        if student_id in self.student_ids:
            raise ValueError("A student with this ID already exists.")
        if not name.strip() or not email.strip() or not branch.strip() or not skills:
            raise ValueError("Name, email, branch, and at least one skill are required.")
        if not 0 <= cgpa <= 10:
            raise ValueError("CGPA must be between 0 and 10.")
        if backlogs < 0:
            raise ValueError("Backlogs cannot be negative.")

        student = Student(student_id, name, email, cgpa, backlogs, branch, skills)
        self.students.insert(student)
        self.student_ids.add(student_id)
        return student

    def shortlist(self, company):
        applications = Queue()
        ranking = PriorityQueue()
        current = self.students.head

        while current is not None:
            applications.enqueue(current.data)
            current = current.next

        while not applications.is_empty():
            student = applications.dequeue()
            if company.check_application(student):
                ranking.insert(student)

        selected_students = []
        while not ranking.is_empty():
            selected_students.append(ranking.remove())
        return selected_students
