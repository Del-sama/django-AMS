from django.forms import ModelForm
from ams_app import models
from django.contrib.auth.models import User
from django import forms
 

class UserForm(ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
            'label': 'username'
        }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        help_texts = {
            'username': '',
        }
        widgets = {
            'password' : forms.PasswordInput()
        }

CHOICES = (
   ('Lecturer', 'Lecturer'), 
   ('Student', 'Student'),
)


class ProfileForm(ModelForm):
    role = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.Select(attrs={'class':'form-control'}),
        label='I am a...',
    )
    
    class Meta:
        model = models.Profile
        fields = ['role', 'matric_number']

        
class AssignmentForm(ModelForm):
    upload = forms.FileField(
        required=False,
        label='Select a file',
        help_text='max. 42 megabytes'
    )
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'datepicker'})
    )

    class Meta:
        model = models.Assignment
        fields = ['title', 'upload', 'due_date', 'course_code', 'course_title']


class SubmissionForm(ModelForm):
    upload = forms.FileField(required=True)

    class Meta:
        model = models.Submission
        fields = ['upload']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        fields = ['username', 'password']
        help_texts = {
            'username': '',
        }


class PassForm(forms.Form):
    passcode = forms.CharField()

    class Meta:
        fields = "passcode"


class AssignmentSearchForm(forms.Form):
    q = forms.CharField()

    class Meta:
        fields = "q"
        errorlist = {
            'q': '',
        }


class SubmissionSearchForm(forms.Form):
    q = forms.CharField()

    class Meta:
        fields = "q"


class GradeForm(forms.Form):
    grade = forms.CharField()

    class Meta:
        fields = ['grade']


class FeedbackForm(forms.Form):
    feedback = forms.CharField()
    
    class Meta:
        fields = ['feedback']
