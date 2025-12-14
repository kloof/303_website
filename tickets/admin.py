from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'event', 'seat', 'payment_status', 'purchase_date')
    list_filter = ('payment_status', 'purchase_date', 'event')
    search_fields = ('customer__username', 'transaction_id', 'event__title')
    readonly_fields = ('transaction_id', 'purchase_date', 'qr_code')
