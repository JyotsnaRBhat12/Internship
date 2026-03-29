from django.urls import path
from . import views

urlpatterns = [
    path('create-note/', views.create_note),
    path('share-note/', views.share_note),
    path('public/<str:token>/', views.public_note),

    path('login/', views.login_user),
    path('verify-otp/', views.verify_otp),

    path('admin-only/', views.admin_only),
]