from django.urls import path
from .views import AdListCreateView, AdRetrieveUpdateDestroyView

urlpatterns = [
    path('ads/', AdListCreateView.as_view(), name='ad-list-create'),
    path('ads/<int:pk>/', AdRetrieveUpdateDestroyView.as_view(), name='ad-detail'),
]