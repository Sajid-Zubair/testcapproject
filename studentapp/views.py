from django.shortcuts import render
from .models import jnr_core, snr_core
from .models import Students
from twilio.rest import Client
from django.db.models import Func, F, Value
import os
from dotenv import load_dotenv

load_dotenv()


def students_table(request):
    students = Students.objects.all()
    return render(request, 'students_table.html', {'students': students})

def home(request):
    return render(request, 'landing.html')

def input_page(request):
    return render(request, 'input.html')


def input_page(request, batch):
    branch = request.GET.get("branch", "")
    section = request.GET.get("section", "")

    return render(request, 'input.html', {
        'batch': batch,
        'branch': branch,
        'section': section
    })

def students_table(request, batch):
    branch = request.GET.get("branch")
    section = request.GET.get("section")

    print("Branch:", branch)
    print("Section:", section)

    # Ensure that the values are stripped of leading/trailing spaces and case-sensitive
    branch = branch.strip().upper() if branch else ''
    section = section.strip().upper() if section else ''

    print(f"Formatted Branch: {branch}")
    print(f"Formatted Section: {section}")

    if batch == "jnr":
        # Filter students based on branch and section
        students = jnr_core.objects.annotate(
        clean_branch=Func(F('branch'), function='TRIM'),
        clean_section=Func(F('section'), function='TRIM')
        ).filter(
            clean_branch__iexact=branch,
            clean_section__iexact=section
        )
    elif batch == "snr":
        # Filter students based on branch and section
        students = snr_core.objects.annotate(
        clean_branch=Func(F('branch'), function='TRIM'),
        clean_section=Func(F('section'), function='TRIM')
        ).filter(
            clean_branch__iexact=branch,
            clean_section__iexact=section
        )
    else:
        students = []

    print(f"Students Found: {students.count() if students else 0}")
    
    # For debugging: Use raw SQL query with proper quotes
    from django.db import connection
    if students:
        # This will print a properly quoted SQL query 
        cursor = connection.cursor()
        sql = str(students.query)
        print("Generated SQL Query:", sql)
        
        # Alternative way to see the last executed query with proper parameter binding
        if connection.queries:
            print("Last executed SQL query:", connection.queries[-1]['sql'])

    return render(request, "students_table.html", {
        "students": students,
        "branch": branch,
        "section": section,
        "batch": batch
    })


def send_sms_to_all(request,batch):
    if batch == "jnr":
        students = jnr_core.objects.all()
    elif batch == "snr":
        students = snr_core.objects.all()

    if request.method == 'POST':
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')

        client = Client(account_sid, auth_token)
        selected_roll_numbers = request.POST.getlist('selected_students')
        
        if not selected_roll_numbers:
            return render(request, 'students_table.html', {
                'students': students,
                'message': 'No students selected for SMS'
            })
        
        selected_students = Students.objects.filter(rollno__in=selected_roll_numbers)

        status = {}

        for student in selected_students:
            # Correct E.164 format, e.g., +91XXXXXXXXXX
            phone_number = student.phonenumber.strip()
            
            if not phone_number.startswith("+"):
                phone_number = "+91" + phone_number  # Assuming India (+91)

            try:
                message = client.messages.create(
                    body="Hi, this is a random message from Twilio", 
                    from_=from_number,
                    to=phone_number
                )
                status[student.rollno] = "Sent"
            except Exception as e:
                status[student.rollno] = "Failed"
                print(f"Error sending message to {phone_number}: {str(e)}")

        # Render the table again after the message sending attempt
        return render(request, 'students_table.html', {
            'students': students,
            'status': status,
            'selected_roll_numbers': selected_roll_numbers,  # Retain selected roll numbers
            'message': 'Messages sent successfully' if status else 'Failed to send messages'  # Message feedback
        })
    
    return render(request, 'students_table.html',{
        'students': students,
        'status': {},
        'selected_roll_numbers': []  # Empty list when not submitting
    })



