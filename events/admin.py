from django.contrib import admin
from .models import Event, Seat, PromoCode

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'date_time', 'location', 'created_at')
    list_filter = ('date_time', 'organizer')
    search_fields = ('title', 'location', 'description')
    ordering = ('-date_time',)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('event', 'row_label', 'seat_number', 'tier', 'status', 'price')
    list_filter = ('event', 'status', 'tier')
    search_fields = ('event__title', 'row_label')
    list_editable = ('status', 'price')

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'event', 'discount_percentage', 'active')
    list_filter = ('active', 'event')
    search_fields = ('code',)
