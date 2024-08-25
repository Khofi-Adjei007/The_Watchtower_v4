from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from officers.models import NewOfficerRegistration

class VerifyBadgeTestCase(TestCase):
    def setUp(self):
        # Create a user and associate a NewOfficerRegistration with it
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.officer_registration = NewOfficerRegistration.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            officer_staff_ID='ABC123',  # Badge number
            officer_current_rank='Sergeant',
            username=self.user.username,  # Ensure username is passed
            # Add any other required fields here
        )
        self.client = Client()

    def test_verify_badge_success(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        
        # Test with correct badge number
        response = self.client.post(reverse('verify_badge'), {'officer_staff_ID': 'ABC123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})

    def test_verify_badge_invalid(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        
        # Test with incorrect badge number
        response = self.client.post(reverse('verify_badge'), {'officer_staff_ID': 'WRONG123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'error', 'message': 'Invalid badge number'})

    def test_verify_badge_unauthenticated(self):
        # Test without logging in
        response = self.client.post(reverse('verify_badge'), {'officer_staff_ID': 'ABC123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'error', 'message': 'User not authenticated'})
