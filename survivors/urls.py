from django.urls import path
from .views import report_infection, register_survivor, update_location, profile

urlpatterns = [
    path('register/', register_survivor, name='register-survivor'),
    path('<int:survivor_id>/location/', update_location, name='update-location'),
    path('report/', report_infection, name='report-infection'),
    path('<int:survivor_id>/profile/', profile, name='profile'),
]
