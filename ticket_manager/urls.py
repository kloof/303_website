from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/events/', include('events.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('organizer/', TemplateView.as_view(template_name='organizer_dashboard.html'), name='organizer'),
    path('event/<int:event_id>/', TemplateView.as_view(template_name='event_details.html'), name='event_details'),
    path('book-event/<int:event_id>/', TemplateView.as_view(template_name='booking.html'), name='book_event'),
    path('my-orders/', TemplateView.as_view(template_name='orders.html'), name='my_orders'),
    path('order-confirmation/', TemplateView.as_view(template_name='order_confirmation.html'), name='order_confirmation'),
    path('admin-logs/', include('admin_logs.urls')),
]

from django.urls import re_path
from django.views.static import serve

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

