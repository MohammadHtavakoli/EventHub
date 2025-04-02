from django.urls import path
from .views import UserEventsView

urlpatterns = [
    path('me/events/', UserEventsView.as_view(), name='user-events'),
]