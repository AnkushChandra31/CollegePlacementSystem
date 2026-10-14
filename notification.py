#Email sending

import smtplib
from email.message import EmailMessage


def send_email(student, company):

    message = EmailMessage()

    message["Subject"] = "Placement Shortlisted"
    message["From"] = "your_email@gmail.com"
    message["To"] = student.email

    message.set_content(
        f"""Hello {student.name},

Congratulations!

You have been shortlisted for the position of {company.job_role} at {company.company_name}.

Your CGPA: {student.cgpa}

Regards,
College Placement System
"""
    )

    print("Email ready for:", student.email)