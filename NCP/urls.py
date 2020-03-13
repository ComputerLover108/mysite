from django.urls import path
from . import views

urlpatterns = [
    path('',views.overview,name='overview'),
    path('overall',views.overall,name='overall'),
]