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

def send_sms_to_all(request, batch):
    # Initialize branch, section, and students variable
    branch = ''
    section = ''
    students = []

    # Handle POST request (when the message is being sent)
    if request.method == 'POST':
        branch = request.POST.get('branch')
        section = request.POST.get('section')

        # Fetch the students based on the branch and section for the given batch
        if batch == "jnr":
            students = jnr_core.objects.filter(branch=branch, section=section)
        elif batch == "snr":
            students = snr_core.objects.filter(branch=branch, section=section)
        
        # Get the selected roll numbers from the form
        selected_roll_numbers = request.POST.getlist('selected_students')
        
        if not selected_roll_numbers:
            return render(request, 'students_table.html', {
                'students': students,
                'message': 'Please select students first',
                'status': {},
                'batch': batch,
                'branch': branch,
                'section': section,
                'selected_roll_numbers': []
            })
        
        # Fetch the selected students using the roll numbers
        if batch == "jnr":
            selected_students = jnr_core.objects.filter(rno__in=selected_roll_numbers)
        elif batch == "snr":
            selected_students = snr_core.objects.filter(rno__in=selected_roll_numbers)

        # Twilio setup
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')

        client = Client(account_sid, auth_token)
        status = {}

        # Send SMS to selected students
        for student in selected_students:
            phone_number = student.phone.strip()

            if not phone_number.startswith("+"):
                phone_number = "+91" + phone_number  # Assuming India (+91)

            try:
                message = client.messages.create(
                    body="Hi, this is a random message from Twilio regarding your results", 
                    from_=from_number,
                    to=phone_number
                )
                status[str(student.rno)] = "Sent"
            except Exception as e:
                status[str(student.rno)] = "Failed"
                print(f"Error sending message to {phone_number}: {str(e)}")
                
        for student in students:
            student.sms_status = status.get(str(student.rno), None)

        # Render the table again after message sending attempt
        return render(request, 'students_table.html', {
            'students': students,
            'status': status,  # Show the status of the messages
            'batch': batch,
            'branch': branch,
            'section': section,
            'selected_roll_numbers': selected_roll_numbers,  # Retain selected roll numbers
            'message': 'Messages sent successfully' if "Sent" in status.values() else 'Failed to send messages'
        })
    
    # Handle GET request (when the page is first loaded or refreshed)
    else:
        branch = request.GET.get('branch')
        section = request.GET.get('section')

        if batch == "jnr":
            students = jnr_core.objects.filter(branch=branch, section=section)
        elif batch == "snr":
            students = snr_core.objects.filter(branch=branch, section=section)

    # Render the table initially or after form submission
    return render(request, 'students_table.html', {
        'students': students,  # List of students based on selected branch and section
        'status': {},  # No status at initial load
        'batch': batch,
        'branch': branch,
        'section': section,
        'selected_roll_numbers': []  # Empty list for the selected students on the first load
    })



