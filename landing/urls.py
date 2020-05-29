from django.urls import path
from . import views


app_name = 'landing'
urlpatterns = [
    path('', views.main_page, name='home'),
    path('logout/', views.LogoutView.as_view(), name='logouut_page'),
]
