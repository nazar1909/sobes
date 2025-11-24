from django.urls import path
from .views import AdListCreateView, AdRetrieveUpdateDestroyView
from myapp.views import get_new_messages

urlpatterns = [
    path('ads/', AdListCreateView.as_view(), name='ad-list-create'),
    path('ads/<int:pk>/', AdRetrieveUpdateDestroyView.as_view(), name='ad-detail'),
    path('get_messages/<int:chat_id>/', get_new_messages, name='get_new_messages'),
]