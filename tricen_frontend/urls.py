from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard),
    path("user_detail/<int:id>/", views.user_detail, name="user_detail"),
]