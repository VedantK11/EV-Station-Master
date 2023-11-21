from django.shortcuts import render,redirect
from EVStationMaster.models import  StationDetails,SlotBooking
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

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

    # views.py
from django.shortcuts import render, redirect
from .models import StationDetails

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
    bookings = SlotBooking.objects.filter(status__in=['Pending', 'Request Pending'], station_id=station_id)

    context = {'bookings': bookings}
    return render(request, 'stationBooking.html', context)

def updateBookingStatus(request, slot_id):
    if 'username' not in request.session:
        return redirect('stationLogin')

    booking = SlotBooking.objects.get(pk=slot_id)

    context = {
        'customerName': booking.customerName,
        # Add other context variables as needed
        'vehicleRegistration': booking.vehicleRegistration,
        'arrivalTime': booking.arrivalTime,
        'userRemark': booking.userRemark,
        'stationRemark': booking.stationRemark,
        'status': booking.status 
    }
    return render(request, 'updateBookingStatus.html', context)