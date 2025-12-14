from django.db import models
from django.conf import settings

class ActionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50)  # e.g., 'LOGIN', 'CREATE_EVENT', 'BOOK_TICKET'
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
