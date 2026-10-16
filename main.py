"""Run the College Placement System in terminal mode."""

from company import Company
from placement_system import PlacementSystem


def read_student(system):
    """Read and save one student from the terminal."""
    try:
        student_id = int(input("Student ID: "))
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        cgpa = float(input("CGPA: "))
        backlogs = int(input("Backlogs: "))
        branch = input("Branch: ").strip()
        skills = [item.strip() for item in input("Skills (comma separated): ").split(",") if item.strip()]
        system.add_student(student_id, name, email, cgpa, backlogs, branch, skills)
        print("Student added successfully.\n")
    except ValueError as error:
        print(f"Could not add student: {error}\n")


def read_company():
    """Read company criteria from the terminal."""
    while True:
        try:
            company_name = input("Company name: ").strip()
            job_role = input("Job role: ").strip()
            min_cgpa = float(input("Minimum CGPA: "))
            max_backlogs = int(input("Maximum backlogs: "))
            branch = input("Eligible branch: ").strip()
            skills = [item.strip() for item in input("Required skills (comma separated): ").split(",") if item.strip()]

            if not company_name or not job_role or not branch or not skills:
                raise ValueError("Company name, job role, branch, and skills are required.")
            if not 0 <= min_cgpa <= 10 or max_backlogs < 0:
                raise ValueError("Enter a CGPA from 0 to 10 and non-negative backlogs.")
            return Company(company_name, job_role, min_cgpa, max_backlogs, branch, skills)
        except ValueError as error:
            print(f"Invalid company criteria: {error}\nPlease try again.\n")


def run_console():
    """Run the basic terminal version of the application."""
    system = PlacementSystem()
    print("College Placement System - Terminal Mode\n")

    while True:
        choice = input("Add a student? (y/n): ").strip().casefold()
        if choice == "n":
            break
        if choice == "y":
            read_student(system)
        else:
            print("Please enter y or n.\n")

    company = read_company()
    shortlisted = system.shortlist(company)

    print(f"\nShortlisted Students for {company.company_name} - {company.job_role}")
    if not shortlisted:
        print("No students meet the criteria.")
        return

    for number, student in enumerate(shortlisted, start=1):
        print(f"{number}. {student.name} | CGPA: {student.cgpa} | Email: {student.email}")


if __name__ == "__main__":
    run_console()
