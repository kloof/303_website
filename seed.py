import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticket_manager.settings")
django.setup()

from users.models import User
from events.models import Event, Seat

def seed_data():
    print("Seeding data...")
    
    # Create Organizer
    org, created = User.objects.get_or_create(username='organizer', email='org@example.com', role='ORGANIZER')
    if created:
        org.set_password('password123')
        org.save()
        print("Created organizer: organizer/password123")

    # Create Customer
    cust, created = User.objects.get_or_create(username='customer', email='cust@example.com', role='CUSTOMER')
    if created:
        cust.set_password('password123')
        cust.save()
        print("Created customer: customer/password123")

    # Create Event
    event, created = Event.objects.get_or_create(
        title='Tech Conference 2025',
        defaults={
            'organizer': org,
            'description': 'The biggest tech conference of the year featuring AI, Web Dev, and more.',
            'location': 'Silicon Valley Convention Center',
            'date_time': timezone.now() + timedelta(days=30)
        }
    )
    if created:
        print(f"Created event: {event.title}")

    # Create Seats
    if not event.seats.exists():
        seats = []
        rows = ['A', 'B', 'C']
        for i, row in enumerate(rows):
            for num in range(1, 6): # 5 seats per row
                seats.append(Seat(
                    event=event,
                    row_label=row,
                    seat_number=str(num),
                    price=50.00 + (10 * (len(rows)-i)), # Front rows more expensive
                    tier='VIP' if row == 'A' else 'Regular',
                    x_coordinate=15.0 * num,
                    y_coordinate=20.0 * (i + 1)
                ))
        Seat.objects.bulk_create(seats)
        print(f"Created {len(seats)} seats for {event.title}")

    print("Seeding complete.")

if __name__ == '__main__':
    seed_data()
