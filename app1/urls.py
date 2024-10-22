from django.urls import path, include
from . import views
from app1.views import index


urlpatterns = [
    path('', views.index, name='index'),
    path('api/room-categories/', views.room_categories_view, name='room_categories'),  # API route for room categories
    path('api/available-rooms/', views.available_rooms_view, name='available_rooms'),  # API route for checking available rooms
    path('api/make-reservation/', views.make_reservation_view, name='make_reservation'),
]