<<<<<<< HEAD
"""Email notifications for shortlisted students."""

import smtplib
from email.message import EmailMessage


def send_email(student, company, sender_email, app_password):
    """Send one shortlist notification through Gmail SMTP."""
    message = EmailMessage()
    message["Subject"] = "Placement Shortlisted"
    message["From"] = sender_email
    message["To"] = student.email
    message.set_content(
        f"""Hello {student.name},

Congratulations! You have been shortlisted for the position of
{company.job_role} at {company.company_name}.

Your CGPA: {student.cgpa}

Regards,
College Placement System
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(message)
=======
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
>>>>>>> aee2bce018ef6f7373df0dfc38b4cae6b5a6113e
