from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import verify_badge



urlpatterns = [
    path('officer_registrations/', views.officer_registrations, name='officer_registrations'),
    path('officer_login/', views.officer_login, name='officer_login'),
    path('selectPurpose/', views.selectPurpose, name='selectPurpose'),
    path('officer_profile/', views.officer_profile, name='officer_profile'),
    path('officer_logout/', views.officer_logout, name='officer_logout'),
    path('verify_badge/', verify_badge, name='verify_badge'),
    path('docketforms/', views.docketforms, name='docketforms'),
    path('searchdatabase/', views.searchdatabase, name='searchdatabase'),
    path('casesProgress/', views.casesProgress, name='casesProgress'),
    path('commandmessaging/', views.commandmessaging, name='commandmessaging'),
    path('CaseStep1View/', views.CaseStep1View, name='CaseStep1View'),
    path('CaseStep2View/', views.CaseStep2View, name='CaseStep2View'),
    path('CaseStep3View/', views.CaseStep3View, name='CaseStep3View'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
