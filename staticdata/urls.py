from django.urls import path
from staticdata import views

urlpatterns = [
    path('events', views.BaseEventList.as_view()),
]
