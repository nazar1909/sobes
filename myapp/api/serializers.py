from rest_framework import serializers
from myapp.models import AD

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AD
        fields = '__all__'