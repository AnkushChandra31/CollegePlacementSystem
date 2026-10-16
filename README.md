# College Placement System

A basic Python desktop application for maintaining student information, checking company eligibility criteria, ranking shortlisted students by CGPA, and sending shortlist emails.

## Features

- Add student details: ID, name, email, CGPA, backlogs, branch, and skills.
- Set company eligibility criteria: company, job role, minimum CGPA, maximum backlogs, branch, and required skills.
- Shortlist eligible students and rank them by CGPA.
- Send shortlist email notifications to selected students using Gmail SMTP.
- Prevent duplicate student IDs and invalid CGPA/backlog values.

## Requirements

- Python 3
- Tkinter (included with most standard Python installations on Windows)
- A Gmail account with 2-Step Verification enabled, if email notifications are required.

## Run the Application

Open a terminal in the project folder and run:

```powershell
python gui.py
```

This opens the desktop interface. To use the basic terminal version, run:

```powershell
python main.py
```

## How to Use

1. Open the **Student and Company** tab.
2. Enter the student details and click **Add Student**. Add as many students as needed.
3. Set the company criteria.
4. Click **Shortlist Students**.
5. Open the **Shortlist and Email** tab to view eligible students.
6. To email the shortlisted students, enter the sender Gmail address and Gmail App Password, then click **Send Emails**.

## Email Setup

Gmail does not allow an application to send email anonymously. The application needs a sender email address and a Gmail App Password to sign in securely.

Create a Gmail App Password:

1. Enable 2-Step Verification in the Gmail account.
2. Open the Google Account **App Passwords** page.
3. Create an app password and use that password in the application instead of the normal Gmail password.

### Avoid Typing Credentials Every Time

You can save the email values in Windows environment variables. Do not put passwords inside Python files or upload them to GitHub.

```powershell
setx PLACEMENT_SENDER_EMAIL "your-email@gmail.com"
setx PLACEMENT_EMAIL_APP_PASSWORD "your-16-character-app-password"
```

Close and reopen the terminal/application after running these commands. The email fields will then be filled automatically.

## Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Starts the desktop application. |
| `gui.py` | Tkinter interface, validation, shortlisting display, and email controls. |
| `placement_system.py` | Student storage and shortlisting workflow. |
| `student.py` | Student data model. |
| `company.py` | Company eligibility rules. |
| `data_structures.py` | Linked list, queue, and priority queue implementations. |
| `notification.py` | Gmail SMTP shortlist email sender. |

## Security Note

Never commit an App Password, `.env` file, or personal email credentials to GitHub. The included `.gitignore` excludes common secret and local-development files.
