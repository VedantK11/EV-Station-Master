from django.contrib import admin
from django.urls import path
from django.urls import include
from EVStationMaster import views


urlpatterns = [
    path("", views.index,name='index'),
    path('stationLogin', views.stationLogin, name='stationLogin'),
    path('stationRegistration', views.stationRegistration, name='stationRegistration'),
    path('stationDefault', views.stationDefault, name='stationDefault'),
    path('stationDetails', views.stationDetails, name='stationDetails'),
    path('stationBooking', views.stationBooking, name='stationBooking'),
    path('searchStation', views.searchStation, name='searchStation'),
    path('viewStation', views.viewStation, name='viewStation'),
    path('slotBooking', views.slotBooking, name='slotBooking'),
    path('userStatus', views.userStatus, name='userStatus'),
    path('updateBookingStatus', views.updateBookingStatus, name='updateBookingStatus'),
    path('bookingHistory', views.bookingHistory, name='bookingHistory'),
    path('userStatusUpdate', views.userStatusUpdate, name='userStatusUpdate'),
    path('adminLogin', views.adminLogin, name='adminLogin'),
    path('adminDefault', views.adminDefault, name='adminDefault'),
    path('adminMaster', views.adminMaster, name='adminMaster'),
    path('stationList', views.stationList, name='stationList'),
    path('change_status/<int:station_id>/', views.change_status, name='change_status'),


]
