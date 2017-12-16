import os

import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchQuery

from ams_app import forms
from ams_app.models import Assignment, Submission, Profile


def sign_up(request):
    user_form = forms.UserForm(request.POST or None)
    profile_form = forms.ProfileForm(request.POST or None)
    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            username=user_form.cleaned_data["username"]
            email=user_form.cleaned_data["email"]
            password=user_form.cleaned_data["password"]
            if User.objects.filter(username=username).exists():
                messages.error(request, "A user with that username already exists.")
                return redirect('/')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "A user with that email address already exists.")
                return redirect('/')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password)
                user.profile.role = profile_form.cleaned_data["role"]
                user.profile.matric_number= profile_form.cleaned_data["matric_number"]
                user.save()
                login(request, user)
                messages.success(request, 'User was successfully created.')
                return redirect('/dashboard')
        for error in user_form.errors.values() or  error in profile_form.errors.values():
            messages.error(request, error)
    login_form = forms.LoginForm()
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "login": login_form
    }
    return render(request, "ams_app/auth.html", context=context)


def login_user(request):
    login_form = forms.LoginForm(request.POST or None)
    if request.method == "POST":
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'User was successfully logged in.')
                return redirect('/dashboard')
            else:
                messages.error(request, 'Username or password is incorrect')
                return redirect('/')
        else:
            for error in login_form.errors.values():
                messages.error(request, error)
            return redirect('/')
    context = {
        "login": login_form
    }
    return render(request, "ams_app/auth.html", context=context)


@login_required
def logout_user(request):
    logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    assignment_form = forms.AssignmentForm(request.POST or None)
    search_form = forms.AssignmentSearchForm(request.GET or None)
    user_id = request.user.id
    user = request.user.profile
    assignments = request.user.assignments.all()
    assignments_list = assignments
    if user.role == 'Lecturer':
        paginator = Paginator(assignments_list, 10)
        page = request.GET.get('page')
        try:
            assignments_list = paginator.page(page)
        except PageNotAnInteger:
            assignments_list = paginator.page(1)
        except EmptyPage:
            assignments_list = paginator.page(paginator.num_pages)

        if request.method == 'GET':
            if search_form.is_valid():
                q = request.GET['q']
                assignments = assignments.annotate(
                    search=SearchVector('title', 'course_code', 'course_title'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(assignments, 10)
                page = request.GET.get('page')
                try:
                    assignments = paginator.page(page)
                except PageNotAnInteger:
                    assignments = paginator.page(1)
                except EmptyPage:
                    assignments = paginator.page(paginator.num_pages)
            else:
                for error in search_form.errors.values():
                    messages(request, error)
                    
                context = {
                    "assignments": assignments,
                    "search_form": search_form,
                    "assignment": assignment_form
                }
                return render(request, 'ams_app/dashboard.html', context=context)
        context = {
            "assignments": assignments,
            "assignment": assignment_form,
            "search_form": search_form
        }
        return render(request, 'ams_app/dashboard.html', context=context)
    else:
        submissions = request.user.submissions.all()
        submissions_list = submissions
        search_form = forms.SubmissionSearchForm(request.GET or None)
        paginator = Paginator(submissions_list, 10)
        page = request.GET.get('page')
        try:
            submissions_list = paginator.page(page)
        except PageNotAnInteger:
            submissions_list = paginator.page(1)
        except EmptyPage:
            submissions_list = paginator.page(paginator.num_pages)

        if request.method == 'GET':
            if search_form.is_valid():
                q = request.GET['q']
                submissions = submissions.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(submissions, 10)
                page = request.GET.get('page')
                try:
                    submissions = paginator.page(page)
                except PageNotAnInteger:
                    submissions = paginator.page(1)
                except EmptyPage:
                    submissions = paginator.page(paginator.num_pages)

                context = {
                    "search_form": search_form,
                    "submissions": submissions
                    }
                return render(request, 'ams_app/students_dashboard.html', context=context)
        context = {
            "search_form": search_form,
            "submissions": submissions,
        }
        return render(request, 'ams_app/students_dashboard.html', context=context)

             
@login_required
def create_assignment(request):
    assignment_form = forms.AssignmentForm(request.POST or None)
    if request.user.profile.role == 'Lecturer':
        if request.method == "POST":
            if assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.user_id = request.user.id
                assignment.save()
                new_data = Assignment.objects.last()
                messages.success(request, 'Assignment was successfully created.')
                return redirect('/dashboard')
            else:
                for error in assignment_form.errors.values():
                    messages.error(request, error)
        context = {
            "assignment": assignment_form
        }
        return render(request, "ams_app/dashboard.html", context=context)
    else:
        messages.error(request, 'Only Lecturer accounts can create assignments')
        context = {
            "assignment": assignment_form
        }
        return render(request, "ams_app/dashboard.html", context=context)


@login_required
def assignment_detail(request, id):
    assignment = Assignment.objects.get(id=id)
    initial = {
        "title": assignment.title,
        "upload": assignment.upload,
        "due_date": assignment.due_date,
        "course_code": assignment.course_code,
        "course_title": assignment.course_title
        }
    assignment_form = forms.AssignmentForm(initial=initial)
    context = {
        "single_assignment": assignment,
        "assignment_id": id,
        "assignment": assignment_form
    }
    return render(request, 'ams_app/assignment-detail.html', context=context)


@login_required
def assignment_submissions(request, id):
    assignment_id = id
    if request.user.profile.role == 'Lecturer':
        search_form = forms.SubmissionSearchForm(request.GET or None)
        feedback_form = forms.FeedbackForm(request.POST or None)
        grade_form = forms.GradeForm(request.POST or None)
        assignment = Assignment.objects.get(id=id)
        submissions = assignment.submissions.all().order_by('matric_number')
        submissions_list = submissions
        paginator = Paginator(submissions_list, 10)
        page = request.GET.get('page')
        try:
            submissions_list = paginator.page(page)
        except PageNotAnInteger:
            submissions_list = paginator.page(1)
        except EmptyPage:
            submissions_list = paginator.page(paginator.num_pages)

        if request.method == 'POST':
            if feedback_form.is_valid():
                feedback = request.POST['feedback']
                submission_id = request.POST['submit-feedback']
                submission = Submission.objects.get(id=submission_id)
                submission.feedback = feedback
                submission.save()
            elif grade_form.is_valid():
                grade = request.POST['grade']
                submission_id = request.POST['submit-grade']
                submission = Submission.objects.get(id=submission_id)
                submission.grade = grade
                submission.save()

        if request.method == "GET":
            if search_form.is_valid():
                q = request.GET['q']
                submissions = submissions.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(q))

                paginator = Paginator(submissions, 10)
                page = request.GET.get('page')
                try:
                    submissions = paginator.page(page)
                except PageNotAnInteger:
                    submissions = paginator.page(1)
                except EmptyPage:
                    submissions = paginator.page(paginator.num_pages)

                context = {
                    "search_form": search_form,
                    "submissions": submissions
                }
                return render(request, 'ams_app/assignment-submissions.html', context=context)

        context = {
                "search_form": search_form,
                "submissions": submissions,
                "grade_form": grade_form,
                "feedback_form": feedback_form,
                "assignment_id": assignment_id
            }
        return render(request, 'ams_app/assignment-submissions.html', context=context)


@login_required
def delete_assignment(request, id):
    assignment = Assignment.objects.get(id=id)
    user_id = assignment.user_id
    if user_id == request.user.id:
        assignment.delete()
        messages.success(request, "Assignment was successfully deleted")
        return redirect('/dashboard')
    else:
        context = {
            "single_assignment": assignment,
            "assignment_id": id
        }
        messages.error(request, "You are not authorized to carry out this operation")
        return render(request, 'ams_app/assignment-detail.html', context=context)


@login_required
def edit_assignment(request, id):
    assignment = Assignment.objects.get(id=id)
    user_id = assignment.user_id
    initial = {
        "title": assignment.title,
        "upload": assignment.upload,
        "due_date": assignment.due_date,
        "course_code": assignment.course_code,
        "course_title": assignment.course_title
        }
    assignment_form = forms.AssignmentForm(request.POST, request.FILES, instance=assignment, initial=initial)
    if request.method == "POST":

        if assignment_form.is_valid():
            current_user = request.user.id
            if current_user == user_id:
                assignment_form.save()
                assignment.last_updated = datetime.date.today()
                assignment.save()
                messages.success(request, 'Assignment was successfully edited.')
                new_data = Assignment.objects.last()
                return redirect('assignment_detail', id=new_data.id)
            else:
                messages.error(request, "You are not authorized to carry out this operation")
        else:
            for error in assignment_form.errors.values():
                messages.error(request, error)
            
    context = {
        "assignment": assignment_form,
        "assignment_id": id
    }
    return render(request, "ams_app/assignment-detail.html", context=context)


def pre_submission(request, id):
    if not request.user.is_authenticated():
      return redirect('/')  
    pass_form = forms.PassForm(request.POST or None)
    if request.method == "POST":
        assignment = Assignment.objects.get(id=id)
        if pass_form.is_valid():
            passcode = request.POST["passcode"]
            if passcode == assignment.passcode:
                request.session['passcode'] = passcode
                return redirect('assignment_submission', id=id)
            else:
                messages.error(request, "Passcode does not match")
        else:
            for error in pass_form.errors.values():
                messages.error(request, error)

    submission_form = forms.SubmissionForm()
    context = {
        "pass": pass_form,
        "assignment_id": id,
        "submission": submission_form
    }
    return render(request, "ams_app/pass.html", context)


@login_required
def submit_assignment(request, id):
    assignment = Assignment.objects.get(id=id)
    submission_form = forms.SubmissionForm(request.POST, request.FILES)
    if 'passcode' not in request.session.keys() or request.session['passcode'] != assignment.passcode:
        return redirect('pre_submission', id=id)
    else:
        if assignment.due_date > datetime.date.today():
            if request.method == "POST":
                if submission_form.is_valid():
                    user = request.user.profile
                    submission = submission_form.save(commit=False)
                    submission.user_id = request.user.id
                    submission.assignment_id = id
                    submission.matric_number = user.matric_number
                    submission.save()
                    messages.success(request, 'Assignment was successfully submitted.')
                    return redirect('submission_detail', id=submission.id)
                else:
                    for error in submission_form.errors.values():
                            messages.error(request, error)
            context = {
                "submission": submission_form,
                "assignment_id": id,
                "assignment": assignment
            }
            return render(request, "ams_app/submission.html", context=context)
        else:
            context = {
                "assignment_id": id,
            }
            return render(request, "ams_app/past_due.html", context=context)


@login_required
def submission_detail(request, id):
    submission = Submission.objects.get(id=id)
    context = {
        "single_submission": submission,
        "submission_id": id
    }
    return render(request, 'ams_app/submission-detail.html', context=context)

@login_required
def delete_submission(request, id):
    submission = Submission.objects.get(id=id)
    if submission.user_id == request.user.id:
        submission.delete()
        return redirect('/dashboard')
    else:
        context = {
            "single_submission": submission,
            "submission_id": id
        }
        messages.error(request, "You are not authorized to carry out this operation")
        return render(request, 'ams_app/submission-detail.html', context=context)


@login_required
def edit_submission(request, id):
    submission = Submission.objects.get(id=id)
    assignment_id = submission.assignment_id
    assignment = Assignment.objects.get(id=assignment_id)
    user_id = submission.user_id
    initial = {
        "upload": submission.upload
        }
    submission_form = forms.SubmissionForm(request.POST, request.FILES, instance=submission, initial=initial)
    if request.method == "POST":
        if assignment.due_date > datetime.date.today():
            if submission_form.is_valid():
                current_user = request.user.id
                if current_user == user_id:
                    submission_form.save()
                    submission.last_updated = datetime.date.today()
                    submission.save()
                    messages.success(request, 'Submission was successfully edited.')
                    new_data = Submission.objects.last()
                    return redirect('submission_detail', id=new_data.id)
                else:
                    messages.error(request, "You are not authorized to carry out this operation")
            else:
                for error in submission_form.values():
                    messages.error(request, error)
                
        else:
            messages.error(request, "The due date for this assignment has passed")
    context = {
        "submission": submission_form,
        "submission_id": id,
        "single_submission": submission
    }
    return render(request, "ams_app/submission-detail.html", context=context)
