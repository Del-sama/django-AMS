from django.forms import ModelForm
from ams_app import models
from django.contrib.auth.models import Group, User
from django import forms


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        help_texts = {
            'username': '',
        }


class ProfileForm(ModelForm):
    class Meta:
        model = models.Profile
        fields = ('role', 'matric_number')


class AssignmentForm(ModelForm):
    upload = forms.FileField(
        required=False,
        label='Select a file',
        help_text='max. 42 megabytes'
    )
    due_date = forms.DateField()

    class Meta:
        model = models.Assignment
        widgets = {
            'due_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }
        fields = ['title', 'upload', 'due_date', 'course_code', 'course_title']


class SubmissionForm(ModelForm):
    upload = forms.FileField(required=True)

    class Meta:
        model = models.Submission
        fields = ['upload']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        fields = ['username', 'password']
        help_texts = {
            'username': '',
        }


class PassForm(forms.Form):
    passcode = forms.CharField(max_length=8)

    class Meta:
        fields = "passcode"


class AssignmentSearchForm(forms.Form):
    assignment_query = forms.CharField()

    class Meta:
        fields = "assignment_query"


class SubmissionSearchForm(forms.Form):
    submission_query = forms.CharField()

    class Meta:
        fields = "submission_query"
