from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from ams_app.models import Assignment, Submission, Profile

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@test.com", password="password")

        self.assignment = Assignment.objects.create(
            title="Test",
            due_date="2017-12-12",
            course_code="Test 123",
            course_title="Test",
            user_id=self.user.id
        )

        self.first_file = SimpleUploadedFile("file.txt", b"file_content")

        self.submission = Submission.objects.create(
            upload=self.first_file,
            user_id=self.user.id,
            assignment_id=self.assignment.id,
            matric_number='15907984'
        )

    def test_user_is_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.email, "test@test.com")

    def test_profile_is_created_alongside_user(self):
        self.assertTrue(hasattr(self.user, 'profile'), True)
        self.user.profile.role = 'Lecturer'
        self.assertEqual(self.user.profile.role, 'Lecturer')

    def test_assignment_is_created(self):
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertEqual(self.assignment.title, "Test")

    def test_submission_is_created(self):
        self.assertEqual(Submission.objects.count(), 1)

    def test_assignment_has_passcode(self):
        self.assertTrue(hasattr(self.assignment, 'passcode'), True)
        self.assertEqual(len(self.assignment.passcode), 8)
