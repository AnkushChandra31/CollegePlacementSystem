"""Core placement-system logic shared by the interface."""

from data_structures import LinkedList, PriorityQueue, Queue
from student import Student


class PlacementSystem:
    def __init__(self):
        self.students = LinkedList()

    def add_student(self, student_id, name, email, cgpa, backlogs, branch, skills):
        student = Student(student_id, name, email, cgpa, backlogs, branch, skills)
        self.students.insert(student)
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
