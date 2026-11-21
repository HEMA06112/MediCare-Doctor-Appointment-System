from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from app.models import *

# Create your views here.
def index_page (request):
    return render(request,'index.html')


def about_page (request):
    return render (request,'about.html')


def doctor_page(request):
    item=Doctor.objects.all()

    name=request.GET.get('name','').strip()
    if name:
        item=item.filter(name__icontains=name)
    
    specialization=request.GET.get('specialization','')
    if specialization:
        item=item.filter(specialization__iexact=specialization)
    
    experience=request.GET.get('experience','')
    if experience == '0-2':
        item=item.filter(experience__gte=0,experience__lte=2)
    elif experience == '3-5':
        item=item.filter(experience__gte=3,experience__lte=5)
    elif experience == '6-9':
        item=item.filter(experience__gte=6,experience__lte=9)
    elif experience == '10+':
        item=item.filter(experience__gte=10)
    return render (request,'doctor.html',{'item':item})


def profile(request,id):
    a=Doctor.objects.get(id=id)
    return render (request,'profile.html',{'a':a})


def department_page(request):
    item=Department.objects.all()
    return render (request,'department.html',{'item':item})

@login_required(login_url='login')
def appointment(request, id):
   doctor = Doctor.objects.get(id=id)

   if request.method == "POST":
       Patient.objects.create(
           doctor=doctor,
           user=request.user,
           patient_name=request.POST['patient_name'],
           email=request.POST['email'],
           phone_number=request.POST['phone_number'],
           date=request.POST['date'],
           slot_time=request.POST['slot_time'],
           reason=request.POST['reason']
       )

       messages.success(request, 'Appointment booked successfully!')
       return redirect('doctor') 

   return render(request, 'appointment.html', {'a': doctor})


@login_required(login_url='login')
def patient_profile(request):
    if Doctor.objects.filter(user=request.user).exists():
        return redirect('doctor_profile')
    return render(request, 'patient_profile.html')


@login_required(login_url='login')
def patient_appointments(request):
    if Doctor.objects.filter(user=request.user).exists():
        return redirect('doctor_profile')
    appointments = Patient.objects.filter(
        user=request.user,
        date__gte=timezone.localdate(),
        completed=False,
    ).select_related('doctor').order_by('date', 'slot_time')
    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'page_title': 'My Appointments',
    })


@login_required(login_url='login')
def patient_appointment_history(request):
    if Doctor.objects.filter(user=request.user).exists():
        return redirect('doctor_profile')
    appointments = Patient.objects.filter(user=request.user).filter(
        Q(date__lt=timezone.localdate()) | Q(completed=True)
    ).select_related('doctor').order_by('-date', '-slot_time')
    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'page_title': 'Appointment History',
    })


@login_required(login_url='login')
def doctor_profile(request):
    doctor = Doctor.objects.filter(user=request.user).first()
    if doctor is None:
        return redirect('index')
    return redirect('profile', id=doctor.id)


@login_required(login_url='login')
def doctor_today_appointments(request):
    doctor = Doctor.objects.filter(user=request.user).first()
    if doctor is None:
        return redirect('index')
    appointments = Patient.objects.filter(
        doctor=doctor,
        date=timezone.localdate(),
    ).select_related('user').order_by('slot_time')
    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'page_title': "Today's Appointments",
        'doctor_view': True,
    })


@login_required(login_url='login')
def doctor_appointments(request):
    doctor = Doctor.objects.filter(user=request.user).first()
    if doctor is None:
        return redirect('index')
    appointments = Patient.objects.filter(
        doctor=doctor,
    ).select_related('user').order_by('-date', '-slot_time')
    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'page_title': 'Patient Appointment List',
        'doctor_view': True,
    })


@login_required(login_url='login')
def doctor_pending_appointments(request):
    doctor = Doctor.objects.filter(user=request.user).first()
    if doctor is None:
        return redirect('index')
    appointments = Patient.objects.filter(
        doctor=doctor,
        completed=False,
    ).select_related('user').order_by('date', 'slot_time')
    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'page_title': 'Complete Appointments',
        'doctor_view': True,
        'allow_completion': True,
    })


@login_required(login_url='login')
def complete_appointment(request, id):
    if request.method != 'POST':
        return redirect('doctor_pending_appointments')
    doctor = Doctor.objects.filter(user=request.user).first()
    if doctor is None:
        return redirect('index')
    appointment_record = get_object_or_404(
        Patient,
        id=id,
        doctor=doctor,
        completed=False,
    )
    appointment_record.completed = True
    appointment_record.save(update_fields=['completed'])
    messages.success(request, 'Appointment marked as complete.')
    return redirect('doctor_pending_appointments')


def contact_page (request):
    if request.method=='POST':
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        subject=request.POST.get("subject")
        message=request.POST.get("message")
        print(name,email,phone,subject,message)
    return render (request,"contact.html",{"success":"Message sent successfully!"})
    return render (request,"contact.html")

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            error = 'Please fill in all required fields.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif User.objects.filter(username__iexact=username).exists():
            error = 'That username is already taken.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'An account with that email already exists.'
        else:
            try:
                validate_password(password, user=User(username=username, email=email))
            except ValidationError as exc:
                error = ' '.join(exc.messages)
            else:
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('index')

        return render(request, 'signup.html', {'error': error})
    return render(request, 'signup.html')

def login_page(request):
    next_url = request.POST.get('next') or request.GET.get('next', '')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ''

    login_type = request.POST.get('login_type', 'patient')
    if request.user.is_authenticated:
        doctor = Doctor.objects.filter(user=request.user).first()
        if doctor:
            if next_url:
                return redirect(next_url)
            return redirect('profile', id=doctor.id)
        return redirect(next_url or 'index')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        doctor = None

        if login_type == 'doctor':
            doctor_id = str(request.POST.get('doctor_id', '')).strip()
            if doctor_id.isdigit():
                doctor = Doctor.objects.select_related('user').filter(pk=doctor_id).first()
            user = None
            if doctor and doctor.user:
                user = authenticate(
                    request,
                    username=doctor.user.username,
                    password=password,
                )
            if user is not None and user == doctor.user:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect('profile', id=doctor.id)
        else:
            username_or_email = request.POST.get('username', '').strip()
            account = User.objects.filter(email__iexact=username_or_email).first()
            username = account.username if account else username_or_email
            user = authenticate(request, username=username, password=password)

        if login_type != 'doctor' and user is not None and not Doctor.objects.filter(user=user).exists():
            login(request,user)
            return redirect(next_url or 'index')

        return render(request, 'login.html', {
            'error': 'Invalid doctor ID or password' if login_type == 'doctor'
            else 'Invalid username/email or password',
            'next': next_url,
            'login_type': login_type,
        })
    return render(request, 'login.html', {'next': next_url, 'login_type': login_type})
        

def logout_page(request):
    logout(request)
    return redirect('login')