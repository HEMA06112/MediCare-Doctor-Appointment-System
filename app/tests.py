from django.contrib.auth.models import User
from django.test import TestCase

class AuthenticationTests(TestCase):
	def setUp(self):
		self.password = 'StrongPass!482'
		self.user = User.objects.create_user(
			username='patient1',
			email='patient@example.com',
			password=self.password,
		)

	def test_login_with_username(self):
		response = self.client.post('/login', {
			'username': self.user.username,
			'password': self.password,
		})

		self.assertRedirects(response, '/')

	def test_login_with_email(self):
		response = self.client.post('/login', {
			'username': 'PATIENT@example.com',
			'password': self.password,
		})

		self.assertRedirects(response, '/')

	def test_signup_with_matching_passwords(self):
		response = self.client.post('/signup', {
			'username': 'patient2',
			'email': 'patient2@example.com',
			'password': self.password,
			'confirm_password': self.password,
		})

		self.assertRedirects(response, '/')
		self.assertTrue(User.objects.filter(username='patient2').exists())

	def test_signup_rejects_mismatched_passwords(self):
		response = self.client.post('/signup', {
			'username': 'patient2',
			'email': 'patient2@example.com',
			'password': self.password,
			'confirm_password': 'DifferentPass!482',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Passwords do not match.')
		self.assertFalse(User.objects.filter(username='patient2').exists())

	def test_doctor_filters_render_as_in_flow_dropdowns(self):
		self.client.force_login(self.user)

		response = self.client.get('/doctor', {'specialization': 'Neurologist'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.count(b'<details class="filter-dropdown">'), 2)
		self.assertContains(response, 'Neurologist')
		self.assertContains(response, 'class="clear-search"')
		self.assertNotContains(response, '<select')
