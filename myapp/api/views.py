from rest_framework import generics
from myapp.models import AD
from .serializers import AdSerializer

# ✅ Список і створення оголошень
class AdListCreateView(generics.ListCreateAPIView):
    queryset = AD.objects.all()
    serializer_class = AdSerializer

# ✅ Деталі / оновлення / видалення
class AdRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AD.objects.all()
    serializer_class = AdSerializer