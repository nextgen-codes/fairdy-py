from django.contrib.auth.models import User
from django.core import mail
from django.test import Client
from django.test import TestCase

from accounts.models import FairdyUser


class RegistrationTest(TestCase):
    def setUp(self):
        c = Client()
        response = c.post('/accounts/register/', {'email': 'test@fairdy.no', 'username': 'testuser',
                                                       'password1': 'kjH457*fhs6&&', 'password2': 'kjH457*fhs6&&'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username='testuser')
        fairdy_user = FairdyUser.objects.get(user_id=user.id)

        # Test that the new user is now in the temp database used for testing
        self.assertIsNotNone(fairdy_user)

        # Test that the test email mailbox now has 1 message in it
        self.assertEqual(len(mail.outbox), 1)

        # Test that the email contains the token for the fairdy_user
        token = fairdy_user.token
        self.assertIn(token, mail.outbox[0].body)

        # Test validation
        response = c.get('/accounts/validate/{}/'.format(token))
        self.assertEqual(response.status_code, 302)

        # Test validation only works once
        response = c.get('/accounts/validate/{}/'.format(fairdy_user.token))
        self.assertEqual(response.status_code, 404)

        # Test log out
        response = c.get('/accounts/logout/')
        self.assertURLEqual(response.url, '/accounts/login/')
        self.assertURLEqual(c.get('/accounts/profile/').url, '/accounts/login/?next=/accounts/profile/')

    def test_change_email(self):
        user = User.objects.get(username='testuser')
        fairdy_user = FairdyUser.objects.get(user_id=user.id)
        token_old = fairdy_user.token
        print(token_old)
        c = Client()

        # Test log in
        response = c.post('/accounts/login', {'username': 'testuser', 'password': 'kjH457*fhs6&&'})
        print(response)

        # Test change email
        response = c.post('/accounts/change_email/', {'email': 'test2@fairdy.no'})
        print(response)
        self.assertEqual(response.status_code, 302)

        # Check Token was changed
        fairdy_user.refresh_from_db()
        token_2 = fairdy_user.token
        print(token_old)
        print(token_2)
        self.assertNotEqual(token_old, token_2)

        # Check the test mailbox now has 2 emails in it
        self.assertEqual(len(mail.outbox), 2)

        # Check new token in new email
        self.assertIn(token_2, mail.outbox[1].body)

        # Check resend email validation
        response = c.get('/accounts/resend_validation/')
        self.assertEqual(response.status_code, 302)

        # Check Token was changed
        fairdy_user.refresh_from_db()
        token_3 = fairdy_user.token
        self.assertNotEqual(token_2, token_3)

        # Test validation
        response = c.get('/accounts/validate/{}/'.format(token_3))
        self.assertEqual(response.status_code, 302)

        # Check resend email validation disabled now
        response = c.get('/accounts/resend_validation/')
        self.assertEqual(response.status_code, 404)

    def test_forgot_password(self):
        self.c.logout()
        response = self.c.post('/accounts/forgot_password', {'username': 'kasjdfkjasdfksjdf'})
        self.assertEqual(response.status_code, 302)
        self.assertContains(response, "User not found.")
