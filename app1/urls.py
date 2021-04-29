from django.urls import path
from . import views

urlpatterns = [
    path('add-event/', views.AddEvent.as_view(), name='add-event'),

]