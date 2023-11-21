from django.db import models


class StationDetails(models.Model):
    stationName = models.CharField(max_length=255)
    stationId = models.IntegerField()
    email = models.EmailField()
    mobileNo = models.CharField(max_length=10)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    Area =models.CharField(max_length=255,default="_") 
    status = models.CharField(max_length=255)

    dayTime =models.CharField(max_length=50,default="_")
    Pspaces = models.BigIntegerField(default=0)
    Paymodes = models.CharField( max_length=50,default="_")
    state =models.CharField(max_length=255,default="_") 
    Pincode = models.IntegerField(default=0)
    # vehicleTypes = models.CharField(max_length=255,default="_")
    rapidcharger = models.IntegerField(default=0)
    fastCharger = models.IntegerField(default=0)
    slowcharger = models.IntegerField(default=0)
    loc1 = models.CharField(max_length=255,default="_")
    loc2 =models.CharField(max_length=255,default="_") 
    loc3 =models.CharField(max_length=255,default="_") 
    loc4 =models.CharField(max_length=255,default="_") 
    loc5 =models.CharField(max_length=255,default="_") 
    loc6 =models.CharField(max_length=255,default="_") 
    
class SlotBooking(models.Model):
    customerName = models.CharField(max_length=255)
    vehicleRegistration = models.CharField(max_length=20)
    # arrivalDay = models.DateTimeField(_(""), auto_now=False, auto_now_add=False)
    arrivalTime = models.DateTimeField()
    userRemark = models.TextField()
    stationRemark = models.TextField()
    status = models.CharField(max_length=20)
