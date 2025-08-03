from django.db import models
from django.contrib.auth.models import User
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import pandas as pd

class StationDetails(models.Model):
    stationName = models.CharField(max_length=255)
    stationId = models.IntegerField()
    email = models.EmailField()
    mobileNo = models.CharField(max_length=10)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    Area = models.CharField(max_length=255, default="_") 
    status = models.CharField(max_length=255)
    
    # Enhanced fields for ML recommendations
    dayTime = models.CharField(max_length=50, default="_")
    Pspaces = models.BigIntegerField(default=0)
    Paymodes = models.CharField(max_length=50, default="_")
    state = models.CharField(max_length=255, default="_") 
    Pincode = models.IntegerField(default=0)
    rapidcharger = models.IntegerField(default=0)
    fastCharger = models.IntegerField(default=0)
    slowcharger = models.IntegerField(default=0)
    loc1 = models.CharField(max_length=255, default="_")
    loc2 = models.CharField(max_length=255, default="_") 
    loc3 = models.CharField(max_length=255, default="_") 
    loc4 = models.CharField(max_length=255, default="_") 
    loc5 = models.CharField(max_length=255, default="_") 
    loc6 = models.CharField(max_length=255, default="_")
    
    # New fields for ML model
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    total_bookings = models.IntegerField(default=0)
    peak_hours = models.CharField(max_length=100, default="9-11,18-20")  # Peak usage hours
    amenities_score = models.IntegerField(default=0)  # Based on available amenities
    
    def get_current_occupancy_rate(self):
        """Calculate current occupancy rate"""
        from django.utils import timezone
        now = timezone.now()
        current_bookings = SlotBooking.objects.filter(
            stationId=self.stationId,
            arrivalTime__date=now.date(),
            status='Accept'
        ).count()
        total_capacity = self.rapidcharger + self.fastCharger + self.slowcharger
        return (current_bookings / max(total_capacity, 1)) * 100

class SlotBooking(models.Model):
    stationId = models.IntegerField()
    stationName = models.CharField(max_length=255, default="_")
    customerName = models.CharField(max_length=255)
    vehicleRegistration = models.CharField(max_length=20)
    chargerType = models.CharField(max_length=255)
    arrivalTime = models.DateTimeField()
    status = models.CharField(max_length=255, default="Request Pending")
    userRemark = models.TextField(default="-")
    stationRemark = models.TextField(default="_")
    unit = models.IntegerField()
    time = models.IntegerField()
    amount = models.IntegerField()
    
    # New fields for ML model
    booking_timestamp = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    user_rating = models.IntegerField(default=0, choices=[(i, i) for i in range(1, 6)])
    distance_from_user = models.FloatField(default=0.0)  # in km
    wait_time_actual = models.IntegerField(default=0)  # in minutes
    
    def __str__(self):
        return f"SlotBooking - ID: {self.id}, Customer: {self.customerName}"

class UserProfile(models.Model):
    """Enhanced user profile for better recommendations"""
    customerName = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    preferred_charger_type = models.CharField(max_length=50, default="fast")
    home_latitude = models.FloatField(default=0.0)
    home_longitude = models.FloatField(default=0.0)
    vehicle_type = models.CharField(max_length=100, default="sedan")
    battery_capacity = models.IntegerField(default=50)  # kWh
    charging_frequency = models.CharField(max_length=20, default="weekly")
    
    def get_booking_history(self):
        return SlotBooking.objects.filter(customerName=self.customerName).order_by('-booking_timestamp')

class StationRecommendationEngine:
    """ML-based recommendation engine for EV stations"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, station, user_location, current_time, user_preferences=None):
        """Prepare feature vector for ML model"""
        features = []
        
        # Station features
        features.extend([
            station.rapidcharger,
            station.fastCharger,
            station.slowcharger,
            station.Pspaces,
            station.average_rating,
            station.total_bookings,
            station.amenities_score,
            station.get_current_occupancy_rate()
        ])
        
        # Distance feature (simplified - in real app use proper geolocation)
        distance = abs(station.latitude - user_location[0]) + abs(station.longitude - user_location[1])
        features.append(distance)
        
        # Time-based features
        hour = current_time.hour
        day_of_week = current_time.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        is_peak_hour = 1 if hour in [9, 10, 11, 18, 19, 20] else 0
        
        features.extend([hour, day_of_week, is_weekend, is_peak_hour])
        
        # User preference features (if available)
        if user_preferences:
            charger_pref = 1 if user_preferences.get('charger_type') == 'rapid' else 0
            features.append(charger_pref)
        else:
            features.append(0)
        
        return np.array(features).reshape(1, -1)
    
    def train_model(self):
        """Train the recommendation model using historical data"""
        # Get training data from bookings
        bookings = SlotBooking.objects.filter(
            status__in=['Accept', 'Completed'],
            user_rating__gt=0
        ).select_related()
        
        if len(bookings) < 10:  # Not enough data
            return False
        
        X = []
        y = []
        
        for booking in bookings:
            try:
                station = StationDetails.objects.get(stationId=booking.stationId)
                user_location = [19.0760, 72.8777]  # Default Mumbai coordinates
                
                features = self.prepare_features(
                    station, 
                    user_location, 
                    booking.arrivalTime
                )
                
                # Target: combination of rating and inverse wait time
                target_score = booking.user_rating * 0.7 + (1.0 / max(booking.wait_time_actual, 1)) * 0.3
                
                X.append(features.flatten())
                y.append(target_score)
                
            except StationDetails.DoesNotExist:
                continue
        
        if len(X) < 5:
            return False
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Save model
        joblib.dump(self.model, 'station_recommendation_model.pkl')
        joblib.dump(self.scaler, 'feature_scaler.pkl')
        
        return True
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            self.model = joblib.load('station_recommendation_model.pkl')
            self.scaler = joblib.load('feature_scaler.pkl')
            self.is_trained = True
            return True
        except:
            return False
    
    def get_recommendations(self, user_location, user_preferences=None, limit=5):
        """Get station recommendations for a user"""
        if not self.is_trained and not self.load_model():
            # Fallback to rule-based recommendations
            return self.get_rule_based_recommendations(user_location, limit)
        
        stations = StationDetails.objects.filter(status='Active')
        current_time = datetime.now()
        
        station_scores = []
        
        for station in stations:
            try:
                features = self.prepare_features(
                    station, 
                    user_location, 
                    current_time, 
                    user_preferences
                )
                
                features_scaled = self.scaler.transform(features)
                predicted_score = self.model.predict(features_scaled)[0]
                
                station_scores.append({
                    'station': station,
                    'score': predicted_score,
                    'predicted_wait_time': max(1, int(station.get_current_occupancy_rate() / 10)),
                    'distance': abs(station.latitude - user_location[0]) + abs(station.longitude - user_location[1])
                })
                
            except Exception as e:
                continue
        
        # Sort by score and return top recommendations
        station_scores.sort(key=lambda x: x['score'], reverse=True)
        return station_scores[:limit]
    
    def get_rule_based_recommendations(self, user_location, limit=5):
        """Fallback rule-based recommendations"""
        stations = StationDetails.objects.filter(status='Active')
        
        station_scores = []
        
        for station in stations:
            # Simple scoring based on distance, availability, and rating
            distance = abs(station.latitude - user_location[0]) + abs(station.longitude - user_location[1])
            availability_score = 100 - station.get_current_occupancy_rate()
            rating_score = station.average_rating * 20
            
            total_score = (availability_score * 0.4) + (rating_score * 0.4) + (1/max(distance, 0.1) * 0.2)
            
            station_scores.append({
                'station': station,
                'score': total_score,
                'predicted_wait_time': max(1, int(station.get_current_occupancy_rate() / 10)),
                'distance': distance
            })
        
        station_scores.sort(key=lambda x: x['score'], reverse=True)
        return station_scores[:limit]




# from django.db import models



# class StationDetails(models.Model):
#     stationName = models.CharField(max_length=255)
#     stationId = models.IntegerField()
#     email = models.EmailField()
#     mobileNo = models.CharField(max_length=10)
#     username = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)
#     city = models.CharField(max_length=255)
#     Area =models.CharField(max_length=255,default="_") 
#     status = models.CharField(max_length=255)

#     dayTime =models.CharField(max_length=50,default="_")
#     Pspaces = models.BigIntegerField(default=0)
#     Paymodes = models.CharField( max_length=50,default="_")
#     state =models.CharField(max_length=255,default="_") 
#     Pincode = models.IntegerField(default=0)
#     # vehicleTypes = models.CharField(max_length=255,default="_")
#     rapidcharger = models.IntegerField(default=0)
#     fastCharger = models.IntegerField(default=0)
#     slowcharger = models.IntegerField(default=0)
#     loc1 = models.CharField(max_length=255,default="_")
#     loc2 =models.CharField(max_length=255,default="_") 
#     loc3 =models.CharField(max_length=255,default="_") 
#     loc4 =models.CharField(max_length=255,default="_") 
#     loc5 =models.CharField(max_length=255,default="_") 
#     loc6 =models.CharField(max_length=255,default="_") 
    
# # class SlotBooking(models.Model):
# #     customerName = models.CharField(max_length=255)
# #     vehicleRegistration = models.CharField(max_length=20)
# #     # arrivalDay = models.DateTimeField(_(""), auto_now=False, auto_now_add=False)
# #     arrivalTime = models.DateTimeField()
# #     userRemark = models.TextField()
# #     stationRemark = models.TextField()
# #     status = models.CharField(max_length=20)

# class SlotBooking(models.Model):
#     stationId = models.IntegerField()
#     stationName= models.CharField(max_length=255,default="_")
#     customerName = models.CharField(max_length=255)
#     vehicleRegistration = models.CharField(max_length=20)
#     chargerType = models.CharField(max_length=255)
#     # vehicleTypes = models.CharField(max_length=255)
#     # startDateTime = models.DateTimeField()
#     # endDateTime = models.DateTimeField()
#     # arrivalTime = models.TimeField()
#     arrivalTime=models.DateTimeField()
#     status = models.CharField(max_length=255, default="Request Pending")
#     userRemark = models.TextField(default="-")
#     stationRemark = models.TextField(default="_")
#     unit= models.IntegerField()
#     time = models.IntegerField()
#     amount = models.IntegerField()

#     def __str__(self):
#         return f"SlotBooking - ID: {self.id}, Customer: {self.customerName}"