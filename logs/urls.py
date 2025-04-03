from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventLogViewSet

router = DefaultRouter()
router.register(r'', EventLogViewSet, basename='eventlog')

urlpatterns = [
    path('', include(router.urls)),
]
