from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from .models import ActionLog
from events.models import Event
from tickets.models import Ticket

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ActionLog.objects.create(
        user=user,
        action='LOGIN',
        details='User logged in successfully'
    )

@receiver(post_save, sender=Event)
def log_event_creation(sender, instance, created, **kwargs):
    if created:
        ActionLog.objects.create(
            user=instance.organizer,  # organizer is a User
            action='CREATE_EVENT',
            details=f"Created event: {instance.title} at {instance.location}"
        )

@receiver(post_save, sender=Ticket)
def log_ticket_booking(sender, instance, created, **kwargs):
    if created:
        ActionLog.objects.create(
            user=instance.customer,
            action='BOOK_TICKET',
            details=f"Booked ticket for event: {instance.seat.event.title} (Seat: {instance.seat.row_label}{instance.seat.seat_number})"
        )
