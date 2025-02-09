from django.urls import path
from . import views

urlpatterns = [
    path("", views.home),
    path("dashboard/", views.dashboard,  name="dashboard"),
    path("user_detail/<int:id>/", views.user_detail, name="user_detail"),
]