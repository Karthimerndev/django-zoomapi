from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view()),
    path('api/token/', TokenObtainPairView.as_view()),  # Login
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('api/', include('core.urls')),
]