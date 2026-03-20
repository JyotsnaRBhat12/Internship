from django.urls import path
from . import views

urlpatterns = [

    path('create-note/', views.create_note),

    path('share-note/<int:note_id>/', views.generate_share_link),

    path('share/<uuid:token>/', views.access_shared_note),

]