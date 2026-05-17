from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', views.MeView.as_view()),

    path('levels/', views.LevelListView.as_view()),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view()),
    path('modules/<int:module_id>/toggle/', views.toggle_module),

    path('progress/', views.my_progress),
    path('stats/', views.public_stats),
]
