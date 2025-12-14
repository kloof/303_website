from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum, Count
from .models import Event, Seat, PromoCode
from .serializers import EventSerializer, SeatSerializer, PromoCodeSerializer
from .permissions import IsOrganizerOrReadOnly

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Create event with optional seat tiers.
        Params: seat_rows, seat_cols, seat_price_vip, seat_price_standard, seat_price_economy
        Tier assignment: Rows A-B = VIP, C-E = Standard, F+ = Economy
        """
        # Extract seating config
        seat_rows = request.data.get('seat_rows')
        seat_cols = request.data.get('seat_cols')
        
        # Tier prices (fallback to single price if not provided)
        price_vip = request.data.get('seat_price_vip')
        price_standard = request.data.get('seat_price_standard')
        price_economy = request.data.get('seat_price_economy')
        single_price = request.data.get('seat_price')
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            event = serializer.save(organizer=request.user)
            
            if seat_rows and seat_cols:
                rows = int(seat_rows)
                cols = int(seat_cols)
                
                seats_to_create = []
                for r in range(rows):
                    row_label = chr(65 + r)  # A, B, C, ...
                    
                    # Determine tier and price based on row
                    if r < 2:  # Rows A-B = VIP
                        tier = 'VIP'
                        price = float(price_vip) if price_vip else float(single_price or 100)
                    elif r < 5:  # Rows C-E = Standard
                        tier = 'STANDARD'
                        price = float(price_standard) if price_standard else float(single_price or 75)
                    else:  # Rows F+ = Economy
                        tier = 'ECONOMY'
                        price = float(price_economy) if price_economy else float(single_price or 50)
                    
                    for c in range(cols):
                        seat_number = c + 1
                        x = 5 + (c * (90 / cols))
                        y = 5 + (r * (90 / rows))
                        
                        seats_to_create.append(Seat(
                            event=event,
                            row_label=row_label,
                            seat_number=str(seat_number),
                            x_coordinate=x,
                            y_coordinate=y,
                            price=price,
                            tier=tier,
                            status='AVAILABLE'
                        ))
                
                Seat.objects.bulk_create(seats_to_create)
        
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['seats_created'] = int(seat_rows) * int(seat_cols) if seat_rows and seat_cols else 0
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def seats(self, request, pk=None):
        event = self.get_object()
        seats = Seat.objects.filter(event=event)
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request):
        """
        Get sales analytics for the current organizer.
        Returns total revenue, tickets sold, and per-event breakdown.
        """
        from tickets.models import Ticket
        
        # Get events for this organizer
        events = Event.objects.filter(organizer=request.user)
        
        # Get all tickets for organizer's events
        tickets = Ticket.objects.filter(event__organizer=request.user, payment_status='COMPLETED')
        
        # Calculate totals
        total_tickets = tickets.count()
        total_revenue = tickets.aggregate(
            total=Sum('seat__price')
        )['total'] or 0
        
        # Per-event breakdown
        event_stats = []
        for event in events:
            event_tickets = tickets.filter(event=event)
            sold = event_tickets.count()
            revenue = event_tickets.aggregate(total=Sum('seat__price'))['total'] or 0
            total_seats = Seat.objects.filter(event=event).count()
            available = Seat.objects.filter(event=event, status='AVAILABLE').count()
            
            event_stats.append({
                'id': event.id,
                'title': event.title,
                'date': event.date_time,
                'total_seats': total_seats,
                'sold': sold,
                'available': available,
                'revenue': float(revenue)
            })
        
        return Response({
            'total_events': events.count(),
            'total_tickets_sold': total_tickets,
            'total_revenue': float(total_revenue),
            'events': event_stats
        })

class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsOrganizerOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

class PromoCodeViewSet(viewsets.ModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [IsOrganizerOrReadOnly]
