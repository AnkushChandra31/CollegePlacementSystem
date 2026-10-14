<<<<<<< HEAD
"""Launch the College Placement System GUI."""

import tkinter as tk

from gui import PlacementApp


if __name__ == "__main__":
    root = tk.Tk()
    PlacementApp(root)
    root.mainloop()
=======
#Runs the project and connects everything

from student import Student
from company import Company
from data_structures import LinkedList, Queue, PriorityQueue
from notification import send_email


students = LinkedList()
applications = Queue()
ranking = PriorityQueue()


def add_student():
    student_id = int(input("Enter Student ID: "))
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    cgpa = float(input("Enter CGPA: "))
    backlogs = int(input("Enter Backlogs: "))
    branch = input("Enter Branch: ")
    skills = input("Enter Skills separated by comma: ").split(",")

    for i in range(len(skills)):
        skills[i] = skills[i].strip()

    student = Student(
        student_id,
        name,
        email,
        cgpa,
        backlogs,
        branch,
        skills
    )

    students.insert(student)

    print("Student added successfully")





add_student()
add_student()

temp = students.head

while temp != None:
    applications.enqueue(temp.data)
    temp = temp.next


company = Company(
    "TCS",
    "Software Developer",
    7.5,
    0,
    "BCA",
    ["Python"]
)


applications.enqueue(student1)
applications.enqueue(student2)


while not applications.is_empty():

    student = applications.dequeue()

    if company.check_application(student):
        ranking.insert(student)


print("Selected Students:")

while not ranking.is_empty():

    student = ranking.remove()

    print(student.name, student.cgpa)

    send_email(student, company)
>>>>>>> aee2bce018ef6f7373df0dfc38b4cae6b5a6113e
