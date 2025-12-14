from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, SeatViewSet, PromoCodeViewSet

router = DefaultRouter()
# Register seats FIRST before the catch-all events pattern
router.register(r'seats', SeatViewSet, basename='seats')
router.register(r'promos', PromoCodeViewSet, basename='promos')
# Events at root of /api/events/ needs to be last
router.register(r'', EventViewSet, basename='events')

urlpatterns = [
    path('', include(router.urls)),
]
