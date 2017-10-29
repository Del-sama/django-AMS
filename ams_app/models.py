import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

def unique_passcode():
    d = uuid.uuid4()
    passcode = d.hex
    return passcode[0:8]


class Profile(models.Model):
    lecturer_or_student = (('Lecturer', 'Lecturer'), ('Student', 'Student'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    matric_number = models.CharField(max_length=12, unique=True, blank=True, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    passcode = models.CharField(max_length=8, default=unique_passcode)
    upload = models.FileField(upload_to='assignments/', null=True)
    due_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    course_code = models.CharField(max_length=8)
    course_title = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


class Submission(models.Model):
    matric_number = models.CharField(max_length=12)
    upload = models.FileField(upload_to='submissions/')
    submitted_at = models.DateField(auto_now=True)
    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    grade = models.CharField(max_length=100, blank=True, null=True)
