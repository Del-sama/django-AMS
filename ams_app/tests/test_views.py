import datetime
from django.test import TestCase,  Client
import os

from django.urls import reverse

from django.contrib.auth.models import User
from ams_app.models import Assignment, Submission, Profile
from django.core.files.uploadedfile import SimpleUploadedFile

class amsappViewTest(TestCase):

    def setUp(self):
        self.sample_file = SimpleUploadedFile("file.txt", b"file_content")
        self.client = Client()
        self.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            password="password"
        )
        self.user.profile.role = "Lecturer"
        
        self.user.save()

        self.student = User.objects.create_user(
            username="student",
            email="testtest@test.com",
            password="password"
        )
        self.student.profile.role = "Student"
        self.student.profile.matric_number = '15907984'
        self.student.save()

        self.login = self.client.login(
            username="test",
            password="password"
        )
        
        self.assignment = Assignment.objects.create(
                title="Test",
                due_date="2017-12-12",
                course_code="Test 123",
                course_title="Test",
                user_id=self.user.id)
        self.assignment.save()

        self.submission = Submission.objects.create(
            upload=self.sample_file,
            user_id=self.student.id,
            assignment_id=self.assignment.id,
            matric_number='15907984'
        )
        self.submission.save()

    def tearDown(self):
        User.objects.all().delete()

    def test_successful_signup(self):
        response = self.client.post('/', {
            'name': 'Delores',
            'email': 'd@d.com',
            'username': 'Delinsky',
            'password': 'password',
            'role': 'Student',
            'matric_number': '01057846'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 3)

    def test_email_already_exists(self):
        response = self.client.post('/', {
            'name': 'Delores',
            'email': 'test@test.com',
            'username': 'delinsky',
            'password': 'password',
            'role': 'Student',
            'matric_number': '01057846'
        }, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertTrue("A user with that email address already exists." in message.message)
        self.assertEqual(response.status_code, 200)

    def test_username_already_exists(self):
        response = self.client.post('/', {
            'name': 'Delores',
            'email': 'd@d.com',
            'username': 'test',
            'password': 'password',
            'role': 'Student',
            'matric_number': '01057846'
        }, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertTrue("A user with that username already exists." in message.message)
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        response = self.client.post(
            reverse('login'), {
                'username': 'test',
                'password': 'password'
            })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard')

    def test_invalid_login_form(self):
        response = self.client.post(
            reverse('login'), {
                'username': 'test'
            }, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertTrue("This field is required." in message.message)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'ams_app/auth.html')

    def test_nonexistent_user(self):
        response = self.client.post(
            reverse('login'), {
                'username': 'testy',
                'password': 'password'
            }, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "error")
        self.assertTrue("Username or password is incorrect" in message.message)
        self.assertEqual(response.status_code, 200)

    def test_succesful_logout(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_lecturer_can_reach_dashboard(self):
        self.assertEqual(self.login, True)
        response = self.client.get(
            reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_student_can_reach_dashboard(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.get(
            reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_can_search_assignments(self):
        self.assertEqual(self.login, True)
        response = self.client.get(
            reverse('dashboard'), {
                'q': 'test'
            })
        expected_html = '<td><a href="/assignments/{}">Test</a></td>'.format(self.assignment.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_html)

    def test_can_search_submissions(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.get(
            reverse('dashboard'), {
                'q': '15907984'
            })
        expected_html = '<td><a href="/submissions/{}/edit">15907984</a></td>'.format(self.submission.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_html)

    def test_can_create_assignment(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('add_assignment'),
            {
                "title": "Test",
                "due_date": "2017-10-11",
                "course_code": "Test 123",
                "course_title": "Test",
                "user_id": self.user.id
            })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Assignment.objects.count(), 2)
    
    def test_invalid_assignment_form(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('add_assignment'),
            {
                "title": "Test",
                "course_code": "Test 123",
                "course_title": "Test",
                "user_id": self.user.id
            }, follow=True)
        message = list(response.context.get('messages'))[0]  
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertTrue("This field is required." in message.message)

    def test_student_create_assignment(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.post(
            reverse('add_assignment'),
            {
                "title": "Test",
                "due_date": "2017-10-11",
                "course_code": "Test 123",
                "course_title": "Test",
                "user_id": self.user.id
            }, follow=True)
        message = list(response.context.get('messages'))[0]  
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertTrue("Only Lecturer accounts can create assignments" in message.message)

    def test_error_creating_assignment(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('add_assignment'))
        self.assertEqual(Assignment.objects.count(), 1)

    def test_can_reach_assignment_detail(self):
        self.assertEqual(self.login, True)
        response = self.client.get(
            reverse('assignment_detail', kwargs={'id': self.assignment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'ams_app/assignment-detail.html')

    def test_can_view_assignment_submissions(self):
        self.assertEqual(self.login, True)
        response = self.client.get(
            reverse('submissions', kwargs={'id': self.assignment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'ams_app/assignment-submissions.html')

    def test_delete_assignment(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('delete_assignment', kwargs ={'id': self.assignment.id}))            
        self.assertEqual(Assignment.objects.count(), 0) 

    def test_unauthorized_delete_assignment(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.post(
            reverse('delete_assignment', kwargs ={'id': self.assignment.id}),
            follow=True)
        message = list(response.context.get('messages'))[0]              
        self.assertEqual(Assignment.objects.count(), 1)
        self.assertTrue("You are not authorized to carry out this operation" in message.message)

    def test_edit_assignment(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('edit_assignment', kwargs ={'id': self.assignment.id}),
            {
                'title': 'Edit test',
                "due_date": "2017-10-11",
                "course_code": "Test 123",
                "course_title": "Test",
                "user_id": self.user.id
                }, follow=True)

        assignment = Assignment.objects.get(id=self.assignment.id)
        message = list(response.context.get('messages'))[0]            
        self.assertEqual(assignment.title, 'Edit test')
        self.assertTrue("Assignment was successfully edited." in message.message)

    def test_unauthorized_edit_assignment(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.post(
            reverse('edit_assignment', kwargs ={'id': self.assignment.id}),{
                'title': 'Edit test',
                "due_date": "2017-10-11",
                "course_code": "Test 123",
                "course_title": "Test",
                "user_id": self.user.id
                }, follow=True)
        assignment = Assignment.objects.get(id=self.assignment.id)
        message = list(response.context.get('messages'))[0]              
        self.assertEqual(assignment.title, 'Test')
        self.assertTrue("You are not authorized to carry out this operation" in message.message)

    def test_pre_submission(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.post(
            reverse('pre_submission', kwargs ={'id': self.assignment.id}),
            { 'passcode': self.assignment.passcode})
        self.assertRedirects(response, reverse('assignment_submission', kwargs={'id':self.assignment.id}), status_code=302)

    def test_invalid_passcode(self):
        self.login = self.client.login(
            username="student",
            password="password"
        ) 
        response = self.client.post(
            reverse('pre_submission', kwargs ={'id': self.assignment.id}),
            { 'passcode': 'duir663'}, follow=True)
        message = list(response.context.get('messages'))[0]              
        self.assertTrue("Passcode does not match" in message.message)
    
    def test_submit_assignment(self):
        test_file = SimpleUploadedFile("file.txt", b"file_content")
        
        self.login = self.client.login(
            username="student",
            password="password"
        )
        session = self.client.session
        session['passcode'] = self.assignment.passcode
        session.save()

        url = reverse('assignment_submission', kwargs ={'id': self.assignment.id})
        data = {'upload': test_file}

        response = self.client.post(url, data, follow=True)
        submission = Submission.objects.filter(assignment_id=self.assignment.id)
        self.assertEqual(submission.count(), 2)

    def test_delete_submission(self):
        self.login = self.client.login(
            username="student",
            password="password"
        )
        response = self.client.post(
            reverse('delete_submission', kwargs ={'id': self.submission.id}))            
        self.assertEqual(Submission.objects.count(), 0) 

    def test_unauthorized_delete_submission(self):
        self.assertEqual(self.login, True)
        response = self.client.post(
            reverse('delete_submission', kwargs ={'id': self.submission.id}),
            follow=True)
        message = list(response.context.get('messages'))[0]              
        self.assertEqual(Submission.objects.count(), 1)
        self.assertTrue("You are not authorized to carry out this operation" in message.message)

    def test_can_reach_submission_detail(self):
        self.login = self.client.login(
            username="student",
            password="password"
        )
        response = self.client.get(
            reverse('submission_detail', kwargs={'id': self.submission.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'ams_app/submission-detail.html')

    def test_edit_submission(self):
        test_file = SimpleUploadedFile("file.txt", b"file_content")
        self.login = self.client.login(
            username="student",
            password="password"
        )
        
        response = self.client.post(
            reverse('submission_detail', kwargs ={'id': self.submission.id}),
            {
                'upload': test_file
                }, follow=True)

        edited_submission = Submission.objects.get(id=self.submission.id)
        message = list(response.context.get('messages'))[0]            
        self.assertNotEqual(self.submission.upload, edited_submission.upload)
        self.assertTrue("Submission was successfully edited" in message.message)

    def test_unauthorized_edit_submission(self):
        test_file = SimpleUploadedFile("file.txt", b"file_content")
        self.assertEqual(self.login, True) 
        response = self.client.post(
            reverse('submission_detail', kwargs ={'id': self.submission.id}),{
                'upload': test_file
                }, follow=True)
        edited_submission = Submission.objects.get(id=self.submission.id)
        message = list(response.context.get('messages'))[0]              
        self.assertEqual(self.submission.upload, edited_submission.upload)
        self.assertTrue("You are not authorized to carry out this operation" in message.message)
