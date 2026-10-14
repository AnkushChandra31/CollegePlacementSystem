#Student class and student-related data

class Student:
    def __init__(self, student_id, name, email, cgpa, backlogs, branch, skills):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.cgpa = cgpa
        self.backlogs = backlogs
        self.branch = branch
        self.skills = skills
