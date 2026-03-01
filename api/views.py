from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserProfile, ScreenTime
from .serializers import UserProfileSerializer

@api_view(['POST'])
def sync_data(request):
    username = request.data.get('username')
    eye_color = request.data.get('eye_color')
    device_type = request.data.get('device_type')
    increment_seconds = request.data.get('increment_seconds', 0)

    if not username:
        return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Get or create UserProfile
    user, created = UserProfile.objects.get_or_create(username=username)

    # Update eye_color if provided
    if eye_color:
        user.eye_color = eye_color
        user.save()

    # Get or create ScreenTime for device
    if device_type:
        st, _ = ScreenTime.objects.get_or_create(user=user, device_type=device_type)
        if increment_seconds:
            st.seconds += int(increment_seconds)
            st.save()

    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_data(request, username):
    try:
        user = UserProfile.objects.get(username=username)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
