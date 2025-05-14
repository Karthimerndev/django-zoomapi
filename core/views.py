from rest_framework import generics, viewsets, permissions
from .models import User, Meeting
from .serializers import RegisterSerializer, MeetingSerializer
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from .utils import get_zoom_token
import requests

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        meeting = serializer.save(user=self.request.user)
        if meeting.participants.exists():
            token = get_zoom_token()

            # Zoom Meeting creation
            zoom_payload = {
                "topic": meeting.title,
                "type": 2,
                "start_time": meeting.date_time.isoformat(),
                "duration": 30,
                "agenda": meeting.description,
                "settings": {"join_before_host": True}
            }

            res = requests.post(
                'https://api.zoom.us/v2/users/me/meetings',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json=zoom_payload
            )
            data = res.json()
            print(data)

            meeting.zoom_meeting_id = data.get("id")
            meeting.join_url = data.get("join_url")
            meeting.save()

            # Send email invitations
            subject = f"Meeting Invite: {meeting.title}"
            message = f"Join the meeting: {meeting.join_url}"
            recipients = [user.email for user in meeting.participants.all()]
            send_mail(subject, message, 'noreply@meetingapp.com', recipients)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        user = request.user
        meetings = Meeting.objects.filter(user=user, date_time__gte=now())
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)