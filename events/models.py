from django.db import models
from django.conf import settings

class Event(models.Model):
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    venue_image = models.ImageField(upload_to='venue_maps/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Seat(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('BOOKED', 'Booked'),
        ('RESERVED', 'Reserved'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    row_label = models.CharField(max_length=10)
    seat_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tier = models.CharField(max_length=50, blank=True, null=True) # e.g. VIP
    x_coordinate = models.FloatField(help_text="X coordinate on the venue map (percentage or pixels)")
    y_coordinate = models.FloatField(help_text="Y coordinate on the venue map (percentage or pixels)")

    class Meta:
        unique_together = ('event', 'row_label', 'seat_number')

    def __str__(self):
        return f"{self.event.title} - {self.row_label}{self.seat_number}"

class PromoCode(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='promo_codes')
    code = models.CharField(max_length=50)
    discount_percentage = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"
