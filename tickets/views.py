from rest_framework import viewsets, permissions, status, exceptions
from rest_framework.response import Response
from django.db import transaction
from .models import Ticket
from .serializers import TicketSerializer, TicketCreateSerializer
from .utils import generate_ticket_qr
from events.models import Seat, Event
import uuid

class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer

    def create(self, request, *args, **kwargs):
        """
        Book tickets for one or multiple seats.
        Accepts: { event_id: int, seat_ids: [int, int, ...] }
        Or legacy: { event_id: int, seat_id: int }
        """
        event_id = request.data.get('event_id')
        
        # Support both single seat_id and array of seat_ids
        seat_ids = request.data.get('seat_ids', [])
        if not seat_ids:
            single_id = request.data.get('seat_id')
            if single_id:
                seat_ids = [single_id]
        
        if not event_id or not seat_ids:
            raise exceptions.ValidationError("event_id and seat_ids are required.")
        
        created_tickets = []
        
        with transaction.atomic():
            # Process all seats in one transaction
            for seat_id in seat_ids:
                try:
                    seat = Seat.objects.select_for_update().get(id=seat_id, event_id=event_id)
                except Seat.DoesNotExist:
                    raise exceptions.ValidationError(f"Seat {seat_id} not found.")

                if seat.status != 'AVAILABLE':
                    raise exceptions.ValidationError(f"Seat {seat.row_label}{seat.seat_number} is not available.")

                # Generate transaction ID
                transaction_id = str(uuid.uuid4())
                
                # Create Ticket
                ticket = Ticket.objects.create(
                    customer=request.user,
                    event_id=event_id,
                    seat=seat,
                    payment_status='COMPLETED',
                    transaction_id=transaction_id
                )
                
                # Update Seat status
                seat.status = 'BOOKED'
                seat.save()

                # Generate QR Code
                qr_data = f"TICKET:{ticket.id}-USER:{request.user.id}-{transaction_id}"
                qr_file = generate_ticket_qr(qr_data)
                ticket.qr_code.save(f'qr_{ticket.id}.png', qr_file, save=True)
                
                created_tickets.append(ticket)

        # Return all created tickets
        serializer = TicketSerializer(created_tickets, many=True)
        return Response({
            'count': len(created_tickets),
            'tickets': serializer.data
        }, status=status.HTTP_201_CREATED)
