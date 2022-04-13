from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from . models import Todo
from django.utils import timezone


def home(request):
    return render(request, 'todowoo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todowoo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect(currenttodos)
            except IntegrityError:
                return render(request, 'todowoo/signupuser.html',
                                  {'form': UserCreationForm(), 'error': 'That username has alredy been taken. Please choose a new username.'})
        else:
            return render(request, 'todowoo/signupuser.html', {'form': UserCreationForm(), 'error':'Passwords didn\'t mutch, try again.' })


def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'todowoo/currenttodos.html', {'todos': todos})


def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todowoo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect(currenttodos)
        except ValueError:
            return render(request, 'todowoo/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad date passed in'})

def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect(currenttodos)

def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect(home)

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todowoo/login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todowoo/login.html', {'form': AuthenticationForm(), 'error': 'Username and password didn\'t match'})
        else:
            login(request, user)
            return redirect(currenttodos)

def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todowoo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect(currenttodos)
        except ValueError:
            return render(request, 'todowoo/createtodo.html', {'form': TodoForm(), 'error': 'Bad date passed in'})
