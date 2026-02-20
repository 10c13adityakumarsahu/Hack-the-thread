from rest_framework import serializers
from .models import SavedItem

class SavedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedItem
        fields = '__all__'
