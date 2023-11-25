from django.shortcuts import render,redirect,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from EVStationMaster.models import  StationDetails,SlotBooking
from django.contrib import messages
from django.db import connection
from datetime import datetime
from django.db.models import Q
from django.urls import reverse

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
    bookings = SlotBooking.objects.filter(status__in=['Pending', 'Request Pending'], stationId=station_id)

    context = {'bookings': bookings}
    return render(request, 'stationBooking.html', context)

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



def bookingHistory(request):
    if 'username' not in request.session:
        return redirect('stationLogin')

    data = SlotBooking.objects.filter(status__in=['Accept', 'Reject']).order_by('id')

    return render(request, 'bookingHistory.html', {'data': data})


def searchStation(request):
    if request.method == 'POST' and 'Button1' in request.POST:
    # if request.method == 'GET' and 'Button1' in request.GET:
        # Handle the form submission for Button1
        ddl_area = request.POST.get('ddlArea')
        txt_username = request.POST.get('txtusername')
        
        if ddl_area is not None and txt_username is not None:
            # url = f'viewStation/?id={ddl_area}&value={txt_username}'
            if ddl_area=="Station Name":
                id="1"
            elif ddl_area=="Area":
                id="2"
            url=reverse('viewStation') + f'?id={id}&value={txt_username}'
            return redirect(url)

    # Handle the form submission for Button2
    elif request.method == 'POST' and 'Button2' in request.POST:
        return redirect('userStatus')

    # Render the initial page
    return render(request, 'searchStation.html')

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