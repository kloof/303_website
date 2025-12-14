from django.core.management.base import BaseCommand
from mcp.server.fastmcp import FastMCP
from events.models import Event, Seat
from logs.models import ActionLog
import json

class Command(BaseCommand):
    help = 'Runs the MCP server for AI integration'

    def handle(self, *args, **options):
        # Initialize MCP Server
        mcp = FastMCP("TicketManager")

        # --- Resources ---
        
        @mcp.resource("prompts://events")
        def list_events() -> str:
            """List all upcoming events with their IDs and locations."""
            events = Event.objects.all().order_by('date_time')
            if not events:
                return "No upcoming events found."
            
            result = ["# Upcoming Events"]
            for e in events:
                result.append(f"- [{e.id}] {e.title} at {e.location} on {e.date_time}")
            return "\n".join(result)

        @mcp.resource("prompts://logs")
        def list_logs() -> str:
            """List the last 50 system logs."""
            logs = ActionLog.objects.all()[:50]
            if not logs:
                return "No logs found."
            
            result = ["# Recent System Logs"]
            for l in logs:
                result.append(f"- {l.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {l.user} | {l.action} | {l.details}")
            return "\n".join(result)

        # --- Tools ---

        @mcp.tool()
        def check_availability(event_id: int) -> str:
            """Check seat availability for a specific event."""
            try:
                event = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                return f"Error: Event with ID {event_id} not found."

            total_seats = Seat.objects.filter(event=event).count()
            available_seats = Seat.objects.filter(event=event, status='AVAILABLE').count()
            
            # Breakdown by tier
            vip_total = Seat.objects.filter(event=event, tier='VIP').count()
            vip_avail = Seat.objects.filter(event=event, tier='VIP', status='AVAILABLE').count()
            
            std_total = Seat.objects.filter(event=event, tier='STANDARD').count()
            std_avail = Seat.objects.filter(event=event, tier='STANDARD', status='AVAILABLE').count()
            
            eco_total = Seat.objects.filter(event=event, tier='ECONOMY').count()
            eco_avail = Seat.objects.filter(event=event, tier='ECONOMY', status='AVAILABLE').count()

            return f"""
Availability for '{event.title}':
- Total Seats: {total_seats}
- Available: {available_seats}

Breakdown:
- 🥇 VIP: {vip_avail}/{vip_total} (Price: ${Seat.objects.filter(event=event, tier='VIP').first().price if vip_total else 'N/A'})
- 🥈 Standard: {std_avail}/{std_total}
- 🥉 Economy: {eco_avail}/{eco_total}
            """

        self.stdout.write(self.style.SUCCESS('Starting TicketManager MCP Server...'))
        mcp.run()
