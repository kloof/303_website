from rest_framework import serializers
from .models import Event, Seat, PromoCode

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'
        ref_name = 'EventSeat'

class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)
    venue_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'title', 'description', 'location', 'date_time', 'venue_image', 'created_at']
    
    def get_venue_image(self, obj):
        if obj.venue_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.venue_image.url)
            return obj.venue_image.url
        return None
    
    def create(self, validated_data):
        # Handle venue_image from request.FILES
        request = self.context.get('request')
        if request and 'venue_image' in request.FILES:
            validated_data['venue_image'] = request.FILES['venue_image']
        return super().create(validated_data)

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'
