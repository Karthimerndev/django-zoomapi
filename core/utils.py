import requests
from django.conf import settings
from .models import ZoomToken
from django.utils.timezone import now, timedelta
import base64

def get_zoom_token():
    token_obj = ZoomToken.objects.first()

    if token_obj and not token_obj.is_expired():
        return token_obj.access_token

    # Refresh or create token
    auth_header = base64.b64encode(
        f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}".encode()
    ).decode()

    res = requests.post(
        f'https://zoom.us/oauth/token?grant_type=account_credentials&account_id={settings.ZOOM_ACCOUNT}',
        headers={
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
    )

    data = res.json()
    new_token = data.get('access_token')
    expires_in = data.get('expires_in')

    if new_token:
        if not token_obj:
            token_obj = ZoomToken()

        token_obj.access_token = new_token
        token_obj.expires_at = now() + timedelta(seconds=expires_in)
        token_obj.save()

        return new_token
    else:
        raise Exception(f"Failed to refresh Zoom token: {data}")