from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import verify_badge




urlpatterns = [
    path('officer_registrations/', views.officer_registrations, name='officer_registrations'),
    path('officer_login/', views.officer_login, name='officer_login'),
    path('selectPurpose/', views.selectPurpose, name='selectPurpose'),
    path('officer_logout/', views.officer_logout, name='officer_logout'),
    path('verify_badge/', verify_badge, name='verify_badge'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)