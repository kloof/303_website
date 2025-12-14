from django.db import models
from django.conf import settings
from events.models import Event, Seat

class Ticket(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='ticket')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.customer.username} - {self.event.title}"
