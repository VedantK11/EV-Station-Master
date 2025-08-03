
from django.shortcuts import render,redirect,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from EVStationMaster.models import StationDetails, SlotBooking
from django.contrib import messages
from django.db import connection
from datetime import datetime
from django.db.models import Q, Avg
from django.urls import reverse
from django.http import JsonResponse
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import pickle
import os

# Add this class to your existing code
class StationRecommendationEngine:
    """ML-based recommendation engine for EV stations"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = 'station_recommendation_model.pkl'
        self.scaler_path = 'feature_scaler.pkl'
    
    def prepare_features(self, station, user_location, current_time, user_preferences=None):
        """Prepare feature vector for ML model"""
        try:
            features = []
            
            # Station features
            features.extend([
                float(station.rapidcharger or 0),
                float(station.fastCharger or 0),
                float(station.slowcharger or 0),
                float(station.Pspaces or 0),
                float(getattr(station, 'average_rating', 0)),
                float(getattr(station, 'total_bookings', 0)),
                float(getattr(station, 'amenities_score', 0)),
                self.get_current_occupancy_rate(station)
            ])
            
            # Distance feature (simplified calculation)
            station_lat = getattr(station, 'latitude', 19.0760)  # Default Mumbai lat
            station_lng = getattr(station, 'longitude', 72.8777)  # Default Mumbai lng
            distance = abs(station_lat - user_location[0]) + abs(station_lng - user_location[1])
            features.append(distance)
            
            # Time-based features
            hour = current_time.hour
            day_of_week = current_time.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            is_peak_hour = 1 if hour in [9, 10, 11, 18, 19, 20] else 0
            
            features.extend([hour, day_of_week, is_weekend, is_peak_hour])
            
            # User preference features
            if user_preferences:
                charger_pref = 1 if user_preferences.get('charger_type') == 'rapid' else 0
                features.append(charger_pref)
            else:
                features.append(0)
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            print(f"Error in prepare_features: {e}")
            # Return default feature vector
            return np.zeros((1, 14))
    
    def get_current_occupancy_rate(self, station):
        """Calculate current occupancy rate"""
        try:
            from django.utils import timezone
            now = timezone.now()
            current_bookings = SlotBooking.objects.filter(
                stationId=station.stationId,
                arrivalTime__date=now.date(),
                status='Accept'
            ).count()
            total_capacity = (station.rapidcharger or 0) + (station.fastCharger or 0) + (station.slowcharger or 0)
            if total_capacity == 0:
                return 0
            return (current_bookings / total_capacity) * 100
        except:
            return 0
    
    def train_model(self):
        """Train the recommendation model using historical data"""
        try:
            # Get training data from bookings with ratings
            bookings = SlotBooking.objects.filter(
                status__in=['Accept'],
                userRemark__isnull=False
            ).exclude(userRemark='-')
            
            if len(bookings) < 5:  # Not enough data
                return False
            
            X = []
            y = []
            
            for booking in bookings:
                try:
                    station = StationDetails.objects.get(stationId=booking.stationId)
                    user_location = [19.0760, 72.8777]  # Default location
                    
                    features = self.prepare_features(
                        station, 
                        user_location, 
                        booking.arrivalTime
                    )
                    
                    # Create target score based on booking success and user remarks
                    target_score = 3.0  # Base score
                    if 'good' in booking.userRemark.lower() or 'excellent' in booking.userRemark.lower():
                        target_score = 4.5
                    elif 'bad' in booking.userRemark.lower() or 'poor' in booking.userRemark.lower():
                        target_score = 2.0
                    
                    X.append(features.flatten())
                    y.append(target_score)
                    
                except StationDetails.DoesNotExist:
                    continue
                except Exception as e:
                    print(f"Error processing booking {booking.id}: {e}")
                    continue
            
            if len(X) < 3:
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Save model
            try:
                joblib.dump(self.model, self.model_path)
                joblib.dump(self.scaler, self.scaler_path)
            except:
                # Fallback to pickle if joblib fails
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
            
            return True
            
        except Exception as e:
            print(f"Error in train_model: {e}")
            return False
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                try:
                    self.model = joblib.load(self.model_path)
                    self.scaler = joblib.load(self.scaler_path)
                except:
                    # Fallback to pickle
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    with open(self.scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                
                self.is_trained = True
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False
    
    def get_recommendations(self, user_location, user_preferences=None, limit=5):
        """Get station recommendations for a user"""
        if not self.is_trained and not self.load_model():
            # Fallback to rule-based recommendations
            return self.get_rule_based_recommendations(user_location, limit)
        
        try:
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
                        'score': max(0, predicted_score),  # Ensure non-negative score
                        'predicted_wait_time': max(1, int(self.get_current_occupancy_rate(station) / 10)),
                        'distance': abs(getattr(station, 'latitude', 19.0760) - user_location[0]) + 
                                   abs(getattr(station, 'longitude', 72.8777) - user_location[1])
                    })
                    
                except Exception as e:
                    print(f"Error processing station {station.stationId}: {e}")
                    continue
            
            # Sort by score and return top recommendations
            station_scores.sort(key=lambda x: x['score'], reverse=True)
            return station_scores[:limit]
            
        except Exception as e:
            print(f"Error in get_recommendations: {e}")
            return self.get_rule_based_recommendations(user_location, limit)
    
    def get_rule_based_recommendations(self, user_location, limit=5):
        """Fallback rule-based recommendations"""
        try:
            stations = StationDetails.objects.filter(status='Active')
            
            station_scores = []
            
            for station in stations:
                # Simple scoring based on distance, availability, and features
                distance = abs(getattr(station, 'latitude', 19.0760) - user_location[0]) + \
                          abs(getattr(station, 'longitude', 72.8777) - user_location[1])
                availability_score = 100 - self.get_current_occupancy_rate(station)
                capacity_score = (station.rapidcharger or 0) + (station.fastCharger or 0) + (station.slowcharger or 0)
                
                total_score = (availability_score * 0.4) + (capacity_score * 0.3) + (1/max(distance, 0.1) * 0.3)
                
                station_scores.append({
                    'station': station,
                    'score': total_score,
                    'predicted_wait_time': max(1, int(self.get_current_occupancy_rate(station) / 10)),
                    'distance': distance
                })
            
            station_scores.sort(key=lambda x: x['score'], reverse=True)
            return station_scores[:limit]
            
        except Exception as e:
            print(f"Error in rule_based_recommendations: {e}")
            return []

# Initialize recommendation engine
try:
    recommendation_engine = StationRecommendationEngine()
except:
    recommendation_engine = None

# Update your existing searchStation function
def searchStation(request):
    recommendations = []
    show_recommendations = False
    
    if request.method == 'POST':
        if 'btn_recommend' in request.POST and recommendation_engine:
            # Get ML recommendations
            try:
                user_lat = float(request.POST.get('user_lat', 19.0760))
                user_lng = float(request.POST.get('user_lng', 72.8777))
                charger_preference = request.POST.get('charger_preference', 'fast')
                
                user_location = [user_lat, user_lng]
                user_preferences = {'charger_type': charger_preference}
                
                recommendations = recommendation_engine.get_recommendations(
                    user_location, 
                    user_preferences, 
                    limit=6
                )
                show_recommendations = True
                
            except Exception as e:
                print(f"Error getting recommendations: {e}")
                message = "Error getting recommendations. Please try again."
                return render(request, 'searchStation.html', {
                    'message': message,
                    'show_recommendations': False,
                    'recommendations': []
                })
        
        elif 'Button1' in request.POST:
            # Original search functionality
            ddl_area = request.POST.get('ddlArea')
            txt_username = request.POST.get('txtusername')
            
            if ddl_area is not None and txt_username is not None:
                if ddl_area == "Station Name":
                    id = "1"
                elif ddl_area == "Area":
                    id = "2"
                url = reverse('viewStation') + f'?id={id}&value={txt_username}'
                return redirect(url)
        
        elif 'Button2' in request.POST:
            return redirect('userStatus')
    
    return render(request, 'searchStation.html', {
        'recommendations': recommendations,
        'show_recommendations': show_recommendations
    })

# Add this new function for training the model (admin use)
def train_recommendation_model(request):
    """Admin function to train the ML model"""
    if request.method == 'POST':
        if recommendation_engine:
            success = recommendation_engine.train_model()
            if success:
                message = "Recommendation model trained successfully!"
            else:
                message = "Not enough data to train the model. Need at least 5 bookings with user feedback."
        else:
            message = "Recommendation engine not available."
        
        return render(request, 'admin_ml_management.html', {'message': message})
    
    # Show current model status
    context = {
        'model_trained': recommendation_engine.is_trained if recommendation_engine else False,
        'total_bookings': SlotBooking.objects.count(),
        'rated_bookings': SlotBooking.objects.exclude(userRemark='-').count()
    }
    
    return render(request, 'admin_ml_management.html', context)


def updateBookingStatus(request):
    if 'username' not in request.session:
        return redirect('stationLogin')
    
    if request.method == 'GET':
        slot_id = int(request.GET.get("id"))

        booking = SlotBooking.objects.get(pk=slot_id)

        context = {
            'id':slot_id,
            'customerName': booking.customerName,
            'vehicleRegistration': booking.vehicleRegistration,
            'arrivalTime': booking.arrivalTime.time(),
            'arrivalDate':booking.arrivalTime.date(),
            'userRemark': booking.userRemark,
            'stationRemark': booking.stationRemark,
            'status': booking.status ,
            'unit':booking.unit,
            'time':booking.time,
            'amount':booking.amount,
            'chargerType':booking.chargerType
        }
        return render(request, 'updateBookingStatus.html', context)

    if request.method == 'POST':
        id=int(request.POST.get("slotid"))
        
        booking = SlotBooking.objects.get(pk=id)
        booking.stationRemark=request.POST.get('txtremark')
        booking.status=request.POST.get('ddlstatus')
        booking.save()
        return render(request, 'stationDefault.html')

# Create your views here.
def master(request):
    return render(request, 'master.html')

def stationLogin(request):
    if request.method == 'POST':
        username = request.POST.get('txtusername')
        password = request.POST.get('txtpassword')
        
        try:
            user = StationDetails.objects.get(username=username, password=password, status='Active')
            request.session['username'] = user.username
            request.session['stationID'] = user.stationId
            return redirect('stationDefault')  
        except StationDetails.DoesNotExist:
            message = 'Invalid Username or Password or Station Deactive'
            return render(request, 'stationLogin.html', {'message': message})

    return render(request, 'stationLogin.html')  

def is_table_empty():
    return StationDetails.objects.count() == 0

def stationRegistration(request):
    if request.method == 'POST':
        station_name = request.POST.get('txtstation')
        email = request.POST.get('txtEmail')
        mobile_no = request.POST.get('txtnumber')
        username = request.POST.get('txtUsername')
        password = request.POST.get('txtPassword')
        city = request.POST.get('txtcity')

        if is_table_empty():
            new_registration=1
        else:
            last_registration = StationDetails.objects.latest('stationId')
            new_registration=last_registration.stationId+1

        StationDetails.objects.create(
            stationName=station_name,
            email=email,
            mobileNo=mobile_no,
            username=username,
            password=password,
            city=city,
            Area='-',
            status='Active',
            stationId=new_registration
        )

        # last_registration = StationDetails.objects.latest('stationId')
        message = f"Registration successful. Station ID is: {new_registration}"
        return render(request, 'stationLogin.html', {'message': message})

    return render(request, 'stationRegistration.html')

def stationMaster(request):
    user_authenticated = 'username' in request.session
    username = request.session.get('username', '')

    return render(request, 'stationMaster.html', {'user_authenticated': user_authenticated, 'username': username})
    # return render(request, 'stationMaster.html', { 'username': username})


def stationDefault(request):
    if 'username' not in request.session:
        return redirect('stationLogin')  
    
    return render(request, 'stationDefault.html')


def stationDetails(request):
    # if 'username' not in request.session:
    #     return redirect('login')  # Redirect to your login page

    station_id = request.session.get('stationID')
    # print(station_id)
    stationDetails = StationDetails.objects.get(stationId=station_id)

    if request.method == 'POST':
        # try:
            # Update station details based on the form data
            # Adjust the field names based on your model
            stationDetails.dayTime = request.POST.get('txtoperationDHr')
            stationDetails.Pspaces = request.POST.get('txtspace')
            stationDetails.Paymodes = request.POST.get('ddlpaymentMode')
            stationDetails.state = request.POST.get('txtstate')
            # if 'txtcity' in request.POST:
                #  stationDetails.city = request.POST.get('txtcity')
            stationDetails.Pincode = request.POST.get('txtpincode')
            stationDetails.rapidcharger = request.POST.get('txtrapid')
            stationDetails.fastCharger = request.POST.get('txtfast')
            stationDetails.slowcharger = request.POST.get('txtslow')
            stationDetails.loc1 = request.POST.get('txtloc1')
            stationDetails.loc2 = request.POST.get('txtloc2')
            stationDetails.loc3 = request.POST.get('txtloc3')
            stationDetails.loc4 = request.POST.get('txtloc4')
            stationDetails.loc5 = request.POST.get('txtloc5')
            stationDetails.loc6 = request.POST.get('txtloc6')
            stationDetails.Area = request.POST.get('txtArea')

            stationDetails.save()

        # except:
            # messages.warning(request, 'Kindly fill the details properly')
            # message = 'Kindly fill the details properly'
            # return render(request, 'stationDetails.html', {'message': message})


    context = {
        'stationDetails': stationDetails,
    }

    return render(request, 'stationDetails.html', context)

def stationBooking(request):
    if 'username' not in request.session:
        return redirect('stationLogin')

    station_id = request.session.get('stationID', 0)
    bookings = SlotBooking.objects.filter(status__in=['Pending', 'Request Pending'], stationId=station_id)

    context = {'bookings': bookings}
    return render(request, 'stationBooking.html', context)





def bookingHistory(request):
    if 'username' not in request.session:
        return redirect('stationLogin')

    data = SlotBooking.objects.filter(status__in=['Accept', 'Reject']).order_by('id')

    return render(request, 'bookingHistory.html', {'data': data})


# def searchStation(request):
#     if request.method == 'POST' and 'Button1' in request.POST:
#     # if request.method == 'GET' and 'Button1' in request.GET:
#         # Handle the form submission for Button1
#         ddl_area = request.POST.get('ddlArea')
#         txt_username = request.POST.get('txtusername')
        
#         if ddl_area is not None and txt_username is not None:
#             # url = f'viewStation/?id={ddl_area}&value={txt_username}'
#             if ddl_area=="Station Name":
#                 id="1"
#             elif ddl_area=="Area":
#                 id="2"
#             url=reverse('viewStation') + f'?id={id}&value={txt_username}'
#             return redirect(url)

#     # Handle the form submission for Button2
#     elif request.method == 'POST' and 'Button2' in request.POST:
#         return redirect('userStatus')

#     # Render the initial page
#     return render(request, 'searchStation.html')

def viewStation(request):
    id = request.GET.get("id")
    value = request.GET.get("value")

    if id == "1":
        stations = StationDetails.objects.filter(status='Active', stationName__icontains=value)
    elif id == "2":
        stations = StationDetails.objects.filter(status='Active').filter(
            Q(city__icontains=value) | Q(Area__icontains=value) | Q(loc1__icontains=value) |
            Q(loc2__icontains=value) | Q(loc3__icontains=value) | Q(loc4__icontains=value) |
            Q(loc5__icontains=value) | Q(loc6__icontains=value)
        ).order_by('stationName')

    context = {'stations': stations}
    return render(request, 'viewStation.html', context)

def slotBooking(request):
# def slotBooking(request, station_id, station_name):

    if request.method == 'GET':
        station_id = request.GET.get("id")
        station_name = request.GET.get("name")
        # print('in if going to render slotBooking')
        # print(f'Station ID: {station_id}, Station Name: {station_name}')
        return render(request, 'slotBooking.html', {'station_id': station_id, 'station_name': station_name})
        
    
    if request.method == 'POST':
        station_id = int(request.POST.get('txtsID'))
        station_name = request.POST.get('txtstation')
        customer_name = request.POST.get('txtCostomerN')
        vehicle_registration = request.POST.get('txtregistration')
        charger_type = request.POST.get('ddlcharingT')
        # vehicle_types = request.POST.get('rblvehicle')
        start_date_time = datetime.strptime(request.POST.get('txtSdate') + ' ' + request.POST.get('txtarrivalT'), '%Y-%m-%d %H:%M')
        status = 'Request Pending'
        user_remark = '-'
        unit = int(request.POST.get('hfunit'))
        time = int(request.POST.get('hftime'))
        amount = int(request.POST.get('hfamount'))

        SlotBooking.objects.create(
            stationId=station_id,
            stationName=station_name,
            customerName=customer_name,
            vehicleRegistration=vehicle_registration,
            chargerType=charger_type,
            # vehicleTypes=vehicle_types,
            # startDateTime=start_date_time,
            # endDateTime=None,
            arrivalTime=start_date_time,
            status=status,
            userRemark=user_remark,
            stationRemark='-',
            unit=unit,
            time=time,
            amount=amount
        )

        message = "Slot Request successful..!"
        return render(request, 'searchStation.html', {'message': message })
    

def userStatus(request):
    if request.method == 'POST':
        txtusername = request.POST.get('txtusername')
        txtvhicaln = request.POST.get('txtvhicaln')

        # with connection.cursor() as cursor:
            # cursor.execute("SELECT * FROM SlotBooking WHERE customerName LIKE %s AND vehicleRegistration = %s", ['%' + txtusername + '%', txtvhicaln])
        user_details = SlotBooking.objects.filter(customerName=txtusername, vehicleRegistration=txtvhicaln)

        # user_details = cursor.fetchall()
        print(user_details)
        return render(request, 'userStatus.html', {'user_details': user_details})

    return render(request, 'userStatus.html')


def userStatusUpdate(request):

    if request.method == 'POST':
        slot_id=request.POST.get('slotId')
        slot_booking = SlotBooking.objects.get(pk=slot_id)
        slot_booking.userRemark = request.POST.get('txtremark')
        slot_booking.save()
        message = "Slot Request successful..!"
        # return redirect('searchStation')
        return render(request, 'searchStation.html', {'message': message })
    
    try:
        slot_id=request.GET.get('id')
        booking = SlotBooking.objects.get(pk=slot_id)
        if booking.status == 'Request Pending':
            message = "Your Request is Pending ..."
        elif booking.status == 'Accept':
            message = "Your Request is Already Accepted"
        elif booking.status == 'Reject':
            message = "Your Request was Rejected"
        else:
            context = {
            'id':slot_id,
            'customerName': booking.customerName,
            'stationName': booking.stationName,
            'vehicleRegistration': booking.vehicleRegistration,
            'arrivalTime': booking.arrivalTime.time(),
            'arrivalDate':booking.arrivalTime.date(),
            'userRemark': booking.userRemark,
            'stationRemark': booking.stationRemark,
            'status': booking.status ,
            'unit':booking.unit,
            'time':booking.time,
            'amount':booking.amount,
            'chargerType':booking.chargerType
            }
            return render(request, 'userStatusUpdate.html', context)

        return render(request, 'searchStation.html', {'message': message })
    
    except ObjectDoesNotExist:
        return HttpResponse("Slot ID does not exist.")

    
def adminLogin(request):
    if request.method == 'POST':
        username = request.POST.get('txtusername')
        password = request.POST.get('txtpwd')

        if username == "admin" and password == "super":
            return redirect('adminDefault')  
        else:
            messages.error(request, 'Invalid Username and Password!')

    return render(request, 'adminLogin.html')

def adminDefault(request):
    return render(request, 'adminDefault.html')

def adminMaster(request):
    return render(request, 'adminMaster.html')

def stationList(request):
    stations = StationDetails.objects.all()
    return render(request, 'stationList.html', {'stations': stations})

def change_status(request, station_id):
    station = StationDetails.objects.get(stationId=int(station_id))

    station.status = 'Inactive' if station.status == 'Active' else 'Active'
    station.save()

    return redirect('stationList')  