from rest_framework import serializers
from .models import Ticket
from events.serializers import EventSerializer, SeatSerializer

class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)
    event_title = serializers.SerializerMethodField()
    seat_label = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = ['id', 'customer', 'event', 'seat', 'payment_status', 'transaction_id', 'qr_code', 'purchase_date', 'event_title', 'seat_label']
    
    def get_event_title(self, obj):
        return obj.event.title if obj.event else None
    
    def get_seat_label(self, obj):
        if obj.seat:
            return f"{obj.seat.row_label}{obj.seat.seat_number}"
        return None

class TicketCreateSerializer(serializers.ModelSerializer):
    seat_id = serializers.IntegerField(write_only=True)
    event_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Ticket
        fields = ('event_id', 'seat_id')

    def validate(self, attrs):
        # Validation can happen here or in view
        return attrs
