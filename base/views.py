from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Topic, Message
from .forms import CourseForm
# Create your views here.

# courses = [
#     {'id': 1, 'name': 'Lets learn python together'},
#     {'id': 2, 'name': 'Design together with me'},
#     {'id': 3, 'name': 'Frontend developers'},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User not found in our system.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
             messages.error(request, 'Username OR password not found in our system.')
         
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')     

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''

    courses = Course.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__contains=q)
        )
        

    topics = Topic.objects.all()
    course_count = courses.count()
    course_messages = Message.objects.filter(Q(course__topic__name__icontains=q))

    context =  {'courses': courses, 'topics': topics, 
                'course_count': course_count, 'course_messages': course_messages}
    return render(request, 'base/home.html', context)
    
def course(request, pk):
    course = Course.objects.get(id=pk)
    course_messages = course.message_set.all()
    participants = course.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            course=course,
            body=request.POST.get('body')
        )
        course.participants.add(request.user)
        return redirect('course', pk=course.id)
    context = {'course': course, 'course_messages': course_messages, 
               'participants':  participants}       
    return render(request, 'base/course.html', context) 

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    courses = user.course_set.all()
    course_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'courses': courses, 
               'course_messages': course_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)
 

@login_required(login_url='login')
def createCourse(request):
    form = CourseForm()
 
    if request.method == 'POST':
       form = CourseForm(request.POST)
       if form.is_valid():
        course = form.save(commit=False)
        course.host = request.user
        course.save()
        return redirect('home')
    context = {'form': form} 
    return render(request, 'base/course_form.html', context)

@login_required(login_url='login')
def updateCourse(request, pk):
    course = Course.objects.get(id=pk)
    form = CourseForm(instance=course)

    if request.user != course.host:
        return HttpResponse('Access Denied !!')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('home')
        
    context = {'form': form}
    return render(request, 'base/course_form.html', context)

@login_required(login_url='login')
def deleteCourse(request, pk):
    course = Course.objects.get(id=pk)

    if request.user != course.host:
        return HttpResponse('Access Denied !!')

    if request.method == 'POST':
        course.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':course})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Access Denied !!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})
