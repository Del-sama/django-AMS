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
    role_choice = (('Lecturer', 'Lecturer'), ('Student', 'Student'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=role_choice, default='Lecturer')
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
    passcode = models.CharField(max_length=100, default=unique_passcode)
    upload = models.FileField(upload_to='assignments/', null=True, default="No file uploaded")
    due_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)
    course_code = models.CharField(max_length=8)
    course_title = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignments'
    )


class Submission(models.Model):
    matric_number = models.CharField(max_length=100)
    upload = models.FileField(upload_to='submissions/')
    submitted_at = models.DateField(auto_now=True)
    last_updated = models.DateField(auto_now=True)
    assignment = models.ForeignKey(
        'Assignment',
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    grade = models.CharField(max_length=100, null=True, blank=True, default="No grade yet")
    feedback = models.CharField(max_length=255, null=True, blank=True, default="No feedback yet")
