from rest_framework import serializers
from .models import UserProfile, ScreenTime

class ScreenTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenTime
        fields = ['device_type', 'seconds']

class UserProfileSerializer(serializers.ModelSerializer):
    screentime_records = ScreenTimeSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'eye_color', 'screentime_records']
