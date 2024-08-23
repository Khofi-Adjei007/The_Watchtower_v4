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
    path('docketforms/', views.docketforms, name='docketforms'),
    path('docketforms/CaseStep1Form/', views.CaseStep1Form, name='CaseStep1Form'),
    path('docketforms/CaseStep2Form/', views.CaseStep2Form, name='CaseStep2Form'),
    path('docketforms/CaseStep3Form/', views.CaseStep3Form, name='CaseStep3Form'),
    path('searchdatabase/', views.searchdatabase, name='searchdatabase'),
    path('casesProgress/', views.casesProgress, name='casesProgress'),
    path('selectPurpose/', views.selectPurpose, name='selectPurpose'),
    path('docketforms/', views.docketforms, name='docketforms'),
    path('searchdatabase/', views.searchdatabase, name='searchdatabase'),
    path('casesProgress/', views.casesProgress, name='casesProgress'),
    path('commandmessaging/', views.commandmessaging, name='commandmessaging'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)