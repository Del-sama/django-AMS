import os

import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery

from ams_app import forms
from ams_app.models import Assignment, Submission, Profile


# Create your views here.
def sign_up(request):
    if request.method == "POST":
        user_form = forms.UserForm(request.POST)
        profile_form = forms.ProfileForm(request.POST)
        # check whether it's valid:
        if user_form.is_valid() and profile_form.is_valid():
            user = User.objects.create_user(
                username=user_form.cleaned_data["username"],
                email=user_form.cleaned_data["email"],
                password=user_form.cleaned_data["password"])
            user.profile.role = profile_form.cleaned_data["role"]
            user.profile.matric_number= profile_form.cleaned_data["matric_number"]
            user.save()
            messages.success(request, 'User was successfully created.')
            # redirect to a new URL:
            return HttpResponseRedirect('/')
        for error in user_form.errors.values() or  error in profile_form.errors.values():
            messages.error(request, error)
    user_form = forms.UserForm()
    profile_form = forms.ProfileForm
    login_form = forms.LoginForm()
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "login": login_form
    }
    return render(request, "ams_app/auth.html", context=context)


def login_user(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'User was successfully logged in.')
                return HttpResponseRedirect('/dashboard')
            else:
                messages.error(request, 'Username or password is incorrect')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return HttpResponseRedirect('/')

    login_form = forms.LoginForm()
    context = {
        "login": login_form
    }
    return render(request, "ams_app/auth.html", context=context)


@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'User was successfully logged out.')
    return HttpResponseRedirect('/')


@login_required
def dashboard(request):
    assignment_form = forms.AssignmentForm()
    search_form = forms.AssignmentSearchForm()
    id = request.user.id
    user = Profile.objects.get(user_id=id)
    assignments= Assignment.objects.filter(user_id=id)
    assignment_list = assignments
    if user.role == 'Lecturer':
        paginator = Paginator(assignment_list, 10)
        page = request.GET.get('page')
        try:
            assignments = paginator.page(page)
        except PageNotAnInteger:
            assignments = paginator.page(1)
        except EmptyPage:
            assignments = paginator.page(paginator.num_pages)

        if request.method == 'POST':
            form = forms.AssignmentSearchForm(request.POST)

            if form.is_valid():
                assignment_query = request.POST['assignment_query']
                assignments = assignment_list.annotate(
                    search=SearchVector('title', 'course_code', 'course_title'),
                    ).filter(search=SearchQuery(assignment_query))

                paginator = Paginator(assignments, 10)
                page = request.GET.get('page')
                try:
                    assignments = paginator.page(page)
                except PageNotAnInteger:
                    assignments = paginator.page(1)
                except EmptyPage:
                    assignments = paginator.page(paginator.num_pages)

                context = {
                    "assignments": assignments,
                    "search_form": search_form,
                    "assignment_id": id,
                    "assignment": assignment_form
                }
                return render(request, 'ams_app/dashboard.html', context=context)
        context = {
            "assignment_id": id,
            "assignments": assignments,
            "assignment": assignment_form,
            "search_form": search_form
        }
        return render(request, 'ams_app/dashboard.html', context=context)
    else:
        submission_list = Submission.objects.filter(user_id=id)
        submissions = submission_list
        submission_search_form = forms.SubmissionSearchForm()
        paginator = Paginator(submission_list, 10)
        page = request.GET.get('page')
        try:
            submissions = paginator.page(page)
        except PageNotAnInteger:
            submissions = paginator.page(1)
        except EmptyPage:
            submissions = paginator.page(paginator.num_pages)

        if request.method == 'POST':
            form = forms.SubmissionSearchForm(request.POST)

            if form.is_valid():
                submission_query = request.POST['submission_query']
                submissions = submission_list.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(submission_query))

                paginator = Paginator(submissions, 10)
                page = request.GET.get('page')
                try:
                    submissions = paginator.page(page)
                except PageNotAnInteger:
                    submissions = paginator.page(1)
                except EmptyPage:
                    submissions = paginator.page(paginator.num_pages)

                context = {
                    "search_form": submission_search_form,
                    "submissions": submissions
                    }
                return render(request, 'ams_app/students_dashboard.html', context=context)
        context = {
            "search_form": submission_search_form,
            "submissions": submissions
        }
        return render(request, 'ams_app/students_dashboard.html', context=context)
    

             
@login_required
def create_assignment(request):
    assignment_form = forms.AssignmentForm()
    id = request.user.id
    user = Profile.objects.get(user_id=id)
    if user.role == 'Lecturer':
        if request.method == "POST":
            form = forms.AssignmentForm(request.POST, request.FILES)
            if form.is_valid():
                assignment = form.save(commit=False)
                assignment.user_id = request.user.id
                assignment.save()
                new_data = Assignment.objects.last()
                messages.success(request, 'Assignment was successfully created.')
                return redirect('/dashboard')

        context = {
            "assignment": assignment_form
        }
        return render(request, "ams_app/dashboard.html", context=context)
    else:
        messages.error(request, 'Only Lecturer accounts can create assignments')
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
    user_id = request.user.id
    user = Profile.objects.get(user_id=user_id)
    assignment_id = id
    # submission = Submission.objects.filter(assignment_id=assignment_id)
    if user.role == 'Lecturer':
        search_form = forms.SubmissionSearchForm()
        grade_form = forms.GradeForm()
        assignment = Assignment.objects.get(id=id)
        submission_list = Submission.objects.filter(assignment_id=id).order_by('matric_number')
        paginator = Paginator(submission_list, 10)
        page = request.GET.get('page')
        try:
            submissions = paginator.page(page)
        except PageNotAnInteger:
            submissions = paginator.page(1)
        except EmptyPage:
            submissions = paginator.page(paginator.num_pages)

        if request.method == 'POST':
            form = forms.GradeForm(request.POST)
            if form.is_valid():
                grade = request.POST['grade']
                submission_id = request.POST['submit-grade']
                submission = Submission.objects.get(id=submission_id)
                submission.grade = grade
                submission.save()

        if request.method == "GET":
            form = forms.SubmissionSearchForm(request.GET)

            if form.is_valid():
                submission_query = request.GET['submission_query']
                submissions = submission_list.annotate(
                    search=SearchVector('matric_number'),
                    ).filter(search=SearchQuery(submission_query))

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
                "assignment_id": assignment_id
            }
        return render(request, 'ams_app/assignment-submissions.html', context=context)



@login_required
def delete_assignment(request, id):
    assignment = Assignment.objects.get(id=id)
    user_id = assignment.user_id
    if user_id == request.user.id:
        assignment.delete()
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
    assignment_form = forms.AssignmentForm(initial=initial)
    if request.method == "POST":
        form = forms.AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            current_user = request.user.id
            if current_user == user_id:
                form.save()
                messages.success(request, 'Assignment was successfully edited.')
                new_data = Assignment.objects.last()
                return redirect('assignment_detail', id=new_data.id)
            else:
                messages.error(request, "You are not authorized to carry out this operation")
    context = {
        "assignment": assignment_form,
        "assignment_id": id
    }
    return render(request, "ams_app/assignment-edit.html", context=context)



@login_required
def pre_submission(request, id):
    if request.method == "POST":
        form = forms.PassForm(request.POST)
        assignment = Assignment.objects.get(id=id)
        assignment_passcode = assignment.passcode
        if form.is_valid():
            passcode = request.POST["passcode"]
            if passcode == assignment_passcode:
                request.session['passcode'] = passcode
                return redirect('assignment_submission', id=id)
            else:
                messages.error(request, "passcode does not match")
        else:
            for error in form.errors.values():
                messages.error(request, error)

    pass_form = forms.PassForm()
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
    if 'passcode' not in request.session.keys() or request.session['passcode'] != assignment.passcode:
        return redirect('pre_submission', id=id)
    else:
        if assignment.due_date > datetime.date.today():
            if request.method == "POST":
                form = forms.SubmissionForm(request.POST, request.FILES)
                if form.is_valid():
                    user_id = request.user.id
                    user = Profile.objects.get(user_id=user_id)
                    submission = form.save(commit=False)
                    submission.user_id = user_id
                    submission.assignment_id = id
                    submission.matric_number = user.matric_number
                    submission.save()
                    messages.success(request, 'Assignment was successfully submitted.')
                    return redirect('submission_detail', id=submission.id)
                else:
                    for error in form.errors.values():
                            messages.error(request, error)

            submission_form = forms.SubmissionForm()
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
    user_id = submission.user_id
    if user_id == request.user.id:
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
    submission_form = forms.SubmissionForm(initial=initial)
    if request.method == "POST":
        if assignment.due_date > datetime.date.today():
            form = forms.SubmissionForm(request.POST, request.FILES, instance=submission)
            if form.is_valid():
                current_user = request.user.id
                if current_user == user_id:
                    form.save()
                    messages.success(request, 'Submission was successfully edited.')
                    new_data = Submission.objects.last()
                    return redirect('submission_detail', id=new_data.id)
                else:
                    messages.error(request, "You are not authorized to carry out this operation")
        context = {
            "submission": submission_form,
            "submission_id": id,
            "single_submission": submission
        }
        return render(request, "ams_app/submission-detail.html", context=context)
    else:
        context = {
            "submission": submission_form,
            "submission_id": id,
            "single_submission": submission
        }
        return render(request, "ams_app/past_due.html", context=context)
