from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from app.models import Doctor, Patient

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

	def test_header_shows_register_when_logged_out_and_logout_when_logged_in(self):
		response = self.client.get('/')
		self.assertContains(response, 'id="register">Register</button>')
		self.assertNotContains(response, 'class="account-menu"')

		self.client.force_login(self.user)
		response = self.client.get('/')
		self.assertContains(response, 'class="account-menu"')
		self.assertContains(response, 'Log out')
		self.assertNotContains(response, 'id="register">Register</button>')

	def test_patient_menu_shows_patient_links_only(self):
		self.client.force_login(self.user)

		for page in ('/', '/about', '/doctor', '/department', '/contact'):
			with self.subTest(page=page):
				response = self.client.get(page)
				self.assertContains(response, '<details class="account-menu">')
				self.assertNotContains(response, '<details class="account-menu" open>')
				self.assertContains(response, 'My Appointments')
				self.assertContains(response, 'Appointment History')
				self.assertContains(response, 'class="logout-link"')
				self.assertNotContains(response, 'Patient Appointment List')

	def test_logout_redirects_to_login_page(self):
		self.client.force_login(self.user)

		response = self.client.get('/logout')

		self.assertRedirects(response, '/login')
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_doctor_menu_shows_doctor_links_only(self):
		doctor_user = User.objects.create_user(username='doctor1', password=self.password)
		doctor = Doctor.objects.create(
			user=doctor_user,
			name='Dr. Login Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)
		self.client.force_login(doctor_user)

		response = self.client.get('/')

		self.assertContains(response, 'Patient Appointment List')
		self.assertContains(response, 'Complete Appointment')
		self.assertContains(response, 'My Profile')
		self.assertNotContains(response, 'My Appointments')

	def test_login_with_email(self):
		response = self.client.post('/login', {
			'username': 'PATIENT@example.com',
			'password': self.password,
		})

		self.assertRedirects(response, '/')

	def test_doctor_login_with_doctor_id_and_linked_user(self):
		doctor_user = User.objects.create_user(username='doctor1', password=self.password)
		doctor = Doctor.objects.create(
			user=doctor_user,
			name='Dr. Login Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)

		response = self.client.post('/login', {
			'login_type': 'doctor',
			'doctor_id': doctor.id,
			'password': self.password,
		})

		self.assertRedirects(response, f'/profile/{doctor.id}')

	def test_login_page_has_separate_patient_and_doctor_forms(self):
		response = self.client.get('/login')

		self.assertContains(response, 'Patient Login')
		self.assertContains(response, 'Doctor Login')
		self.assertContains(response, 'name="doctor_id"')

	def test_doctor_login_rejects_invalid_password(self):
		doctor_user = User.objects.create_user(username='doctor1', password=self.password)
		doctor = Doctor.objects.create(
			user=doctor_user,
			name='Dr. Login Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)

		response = self.client.post('/login', {
			'login_type': 'doctor',
			'doctor_id': doctor.id,
			'password': 'wrong-password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid doctor ID or password')
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_patient_login_rejects_doctor_account(self):
		doctor_user = User.objects.create_user(username='doctor1', password=self.password)
		Doctor.objects.create(
			user=doctor_user,
			name='Dr. Login Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)

		response = self.client.post('/login', {
			'login_type': 'patient',
			'username': 'doctor1',
			'password': self.password,
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid username/email or password')

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


class AppointmentBookingTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='patient1', password='StrongPass!482')
		self.client.force_login(self.user)
		self.doctor = Doctor.objects.create(
			name='Dr. Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)

	def test_anonymous_booking_redirects_to_login_then_back_to_appointment(self):
		self.client.logout()
		appointment_url = f'/appointment/{self.doctor.id}'

		response = self.client.get(appointment_url)

		self.assertRedirects(response, f'/login?next={appointment_url}')
		response = self.client.get(response.url)
		self.assertContains(response, f'name="next" value="{appointment_url}"')

		response = self.client.post('/login', {
			'username': self.user.username,
			'password': 'StrongPass!482',
			'next': appointment_url,
		})

		self.assertRedirects(response, appointment_url)
		self.assertEqual(self.client.get(appointment_url).status_code, 200)

	def test_authenticated_user_can_open_appointment_without_logging_in_again(self):
		response = self.client.get(f'/appointment/{self.doctor.id}')

		self.assertEqual(response.status_code, 200)

	def test_patient_appointments_only_show_their_own_bookings(self):
		appointment_date = timezone.localdate() + timedelta(days=7)
		owned_appointment = Patient.objects.create(
			doctor=self.doctor,
			user=self.user,
			patient_name='Test Patient',
			email='patient@example.com',
			phone_number='1234567890',
			date=appointment_date,
			slot_time='10:00',
			reason='Consultation',
		)
		other_user = User.objects.create_user(username='patient2', password='StrongPass!482')
		Patient.objects.create(
			doctor=self.doctor,
			user=other_user,
			patient_name='Other Patient',
			email='other@example.com',
			phone_number='1234567891',
			date=appointment_date,
			slot_time='11:00',
			reason='Consultation',
		)

		response = self.client.get('/patient/appointments')

		self.assertContains(response, owned_appointment.patient_name)
		self.assertNotContains(response, 'Other Patient')

	def test_doctor_can_mark_their_appointment_completed(self):
		appointment_date = timezone.localdate() + timedelta(days=7)
		doctor_user = User.objects.create_user(username='doctor1', password='StrongPass!482')
		doctor = Doctor.objects.create(
			user=doctor_user,
			name='Dr. Test',
			specialization='Cardiologist',
			qualification='MD',
			experience=5,
			consultation_fee=100,
			profile_image='doctor/test.jpg',
			available_days='Monday-Friday',
			available_time='9:00 AM - 5:00 PM',
			bio='Test bio',
			about='Test about',
		)
		appointment = Patient.objects.create(
			doctor=doctor,
			patient_name='Test Patient',
			email='patient@example.com',
			phone_number='1234567890',
			date=appointment_date,
			slot_time='10:00',
			reason='Consultation',
		)
		self.client.force_login(doctor_user)

		response = self.client.post(f'/doctor/appointments/{appointment.id}/complete')

		self.assertRedirects(response, '/doctor/complete-appointments')
		appointment.refresh_from_db()
		self.assertTrue(appointment.completed)

	def test_successful_booking_shows_popup_message(self):
		response = self.client.post(f'/appointment/{self.doctor.id}', {
			'patient_name': 'Test Patient',
			'email': 'patient@example.com',
			'phone_number': '1234567890',
			'date': '2026-11-01',
			'slot_time': '10:00',
			'reason': 'Consultation',
		})

		self.assertRedirects(response, '/doctor', fetch_redirect_response=False)
		self.assertEqual(Patient.objects.count(), 1)
		self.assertEqual(Patient.objects.get().user, self.user)

		response = self.client.get('/doctor')
		self.assertContains(response, "alert('Appointment booked successfully!');")
