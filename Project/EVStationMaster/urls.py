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

]
