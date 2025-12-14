from django.test import TestCase
from django.contrib.auth import get_user_model
from events.models import Event, Seat
from tickets.models import Ticket

User = get_user_model()

class BookingFlowTests(TestCase):
    def setUp(self):
        # Create Organizer
        self.organizer = User.objects.create_user(username='org', password='password', role='ORGANIZER')
        
        # Create Customer
        self.customer = User.objects.create_user(username='cust', password='password', role='CUSTOMER')
        
        # Create Event
        self.event = Event.objects.create(
            organizer=self.organizer,
            title='Test Event',
            description='Test Description',
            location='Test Location',
            date_time='2025-12-31 20:00:00+00:00'
        )
        
        # Create Seat
        self.seat = Seat.objects.create(
            event=self.event,
            row_label='A',
            seat_number='1',
            price=10.00,
            x_coordinate=10.0,
            y_coordinate=10.0
        )

    def test_booking_flow_api(self):
        # Authenticate as Customer
        self.client.force_login(self.customer)
        
        # Book Ticket via API
        data = {
            'event_id': self.event.id,
            'seat_id': self.seat.id
        }
        response = self.client.post('/api/tickets/', data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payment_status'], 'COMPLETED')
        self.assertTrue(response.data['qr_code'])
        
        # Verify DB
        ticket = Ticket.objects.get(id=response.data['id'])
        self.assertEqual(ticket.customer, self.customer)
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, 'BOOKED')
