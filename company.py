class Company:
    def __init__(self, company_name, job_role, min_cgpa, max_backlogs, branch, required_skills):
        self.company_name = company_name
        self.job_role = job_role
        self.min_cgpa = min_cgpa
        self.max_backlogs = max_backlogs
        self.branch = branch
        self.required_skills = required_skills

    def is_eligible(self, student):
        if student.cgpa < self.min_cgpa:
            return False

        if student.backlogs > self.max_backlogs:
            return False

        if student.branch.strip().casefold() != self.branch.strip().casefold():
            return False

        student_skills = {skill.strip().casefold() for skill in student.skills}
        for skill in self.required_skills:
            if skill.strip().casefold() not in student_skills:
                return False

        return True

    def check_application(self, student):
        if self.is_eligible(student):
            return True

        return False
