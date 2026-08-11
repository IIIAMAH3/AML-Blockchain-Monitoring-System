from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("analyze/", views.analyze, name="analyze"),
    path("results/<int:pk>/", views.results, name="results"),
]
