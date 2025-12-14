from django.shortcuts import render
from rest_framework import generics, permissions
from logs.models import ActionLog
from logs.serializers import ActionLogSerializer

# Page View - Renders the template (Frontend handles auth check via token)
def admin_logs_page(request):
    return render(request, 'admin_logs.html')

# API View - Returns JSON data (Protected by JWT)
class AdminLogListAPI(generics.ListAPIView):
    queryset = ActionLog.objects.all()
    serializer_class = ActionLogSerializer
    permission_classes = [permissions.IsAdminUser] # Only superusers/staff
