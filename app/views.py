from django.contrib.auth.decorators import login_required 
from django.shortcuts import render
from app.models import *

# Create your views here.
def index_page (request):
    return render(request,'index.html')

@login_required
def about_page (request):
    return render (request,'about.html')

@login_required
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

@login_required
def profile(request,id):
    a=Doctor.objects.get(id=id)
    return render (request,'profile.html',{'a':a})

@login_required
def department_page(request):
    item=Department.objects.all()
    return render (request,'department.html',{'item':item})


from django.shortcuts import render, redirect
from .models import Doctor, Patient

def appointment(request, id):
   doctor = Doctor.objects.get(id=id)

   if request.method == "POST":
       Patient.objects.create(
           doctor=doctor,
           patient_name=request.POST['patient_name'],
           email=request.POST['email'],
           phone_number=request.POST['phone_number'],
           date=request.POST['date'],
           slot_time=request.POST['slot_time'],
           reason=request.POST['reason']
       )

       return redirect('doctor') 

   return render(request, 'appointment.html', {'a': doctor})

@login_required
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
from django.shortcuts import redirect

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

from django.contrib.auth import authenticate,login,logout

def login_page(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = User.objects.filter(email__iexact=username_or_email).first()

        if user:
            username = user.username
        else:
            username = username_or_email
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request,user)
            return redirect ('index')

        return render(request, 'login.html', {
            'error': 'Invalid username/email or password'
        })
    return render(request, 'login.html')
        

def logout_page(request):
    logout(request)
    return redirect('login')