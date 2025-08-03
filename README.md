# Smart EV Charging Station Manager with ML Recommendations

## Project Overview

The **Smart EV Charging Station Management System** is a comprehensive web application designed to address the growing demand for electric vehicle charging infrastructure. It features an intelligent recommendation system powered by machine learning to provide personalized charging station suggestions, reducing wait times and improving user experience.

### Key Features

- **AI-Powered Recommendations**: Machine learning-based station suggestions using Random Forest algorithm
- **Multi-Role System**: Separate interfaces for EV Users, Station Managers, and Administrators
- **Real-Time Location Services**: GPS-based station discovery and distance calculation
- **Dynamic Availability Tracking**: Live occupancy rates and wait time predictions
- **Responsive Design**: Mobile-friendly interface with modern UI/UX
- **Analytics Dashboard**: Booking history, user feedback, and station performance metrics

## System Architecture

### Multi-Role Access Control
- **EV Users**: Search stations, book slots, track booking status, provide feedback
- **Station Managers**: Manage bookings, update station details, handle user requests
- **Administrators**: Oversee system operations, manage stations, train ML models

### Machine Learning Pipeline
- **Feature Engineering**: 14+ features including location, capacity, occupancy, temporal patterns
- **Model Training**: Random Forest Regressor with historical booking data
- **Real-Time Predictions**: Dynamic scoring and wait time estimation
- **Fallback System**: Rule-based recommendations for new users

## Project Structure

```
EV-Station-Master/
├── EVStationMaster/
│   ├── models.py              # Database models (StationDetails, SlotBooking, UserProfile)
│   ├── views.py               # Core business logic and ML integration
│   ├── urls.py                # URL routing configuration
│   ├── admin.py               # Django admin interface
│   ├── apps.py                # Application configuration
│   └── migrations/            # Database migration files
├── templates/
│   ├── index.html             # Homepage
│   ├── searchStation.html     # Station search with ML recommendations
│   ├── slotBooking.html       # Booking interface
│   ├── stationLogin.html      # Station manager authentication
│   ├── stationRegistration.html # Station registration
│   ├── stationDefault.html    # Station manager dashboard
│   ├── stationDetails.html    # Station information management
│   ├── stationBooking.html    # Booking management for stations
│   ├── updateBookingStatus.html # Booking status updates
│   ├── bookingHistory.html    # Historical booking records
│   ├── viewStation.html       # Station listing and details
│   ├── userStatus.html        # User booking status tracking
│   ├── userStatusUpdate.html  # User booking modifications
│   ├── stationList.html       # Admin station management
│   ├── adminLogin.html        # Admin authentication
│   ├── adminDefault.html      # Admin dashboard
│   ├── master.html            # Base template
│   └── stationMaster.html     # Station manager template
├── static/                    # CSS, JS, images, and other static files
├── manage.py                  # Django management script
└── README.md                  # Project documentation
```

## Technology Stack

### Backend
- **Framework**: Django 3.2+
- **Database**: PostgreSQL 13+
- **ML Library**: scikit-learn 1.0+
- **Data Processing**: NumPy, Pandas
- **Authentication**: Django Auth System

### Frontend
- **Templates**: Django Templates with Jinja2
- **Styling**: Bootstrap 5, Custom CSS
- **JavaScript**: Vanilla JS, AJAX
- **Icons**: Material Design Iconic Font

### Machine Learning
- **Algorithm**: Random Forest Regressor
- **Features**: Location, capacity, occupancy, temporal patterns, user preferences
- **Model Persistence**: Joblib/Pickle
- **Preprocessing**: StandardScaler for feature normalization

## Installation & Setup

### Prerequisites
```bash
Python 3.8+
PostgreSQL 13+
pip (Python package manager)
```

### 1. Clone Repository
```bash
git clone https://github.com/vedantk11/EV-Station-Master.git
cd EV-Station-Master
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install django==3.2
pip install psycopg2-binary
pip install scikit-learn
pip install numpy pandas
pip install joblib
```

### 4. Database Configuration
Update `Project/Project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ev_station_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Start Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 🔧 Configuration

### Machine Learning Model Training
The system automatically trains the recommendation model when sufficient data is available. To manually train:

1. Access admin panel: `http://localhost:8000/admin`
2. Navigate to ML Management section
3. Click "Train Model" (requires at least 5 rated bookings)
`

## Usage Guide

### For EV Users
1. **Search Stations**: Use AI recommendations or traditional search
2. **View Details**: Check availability, charger types, and ratings
3. **Book Slots**: Select preferred time and charger type
4. **Track Status**: Monitor booking status and receive updates
5. **Provide Feedback**: Rate experience to improve recommendations

### For Station Managers
1. **Register Station**: Complete registration with station details
2. **Manage Bookings**: Accept/reject booking requests
3. **Update Information**: Modify station details and availability
4. **View Analytics**: Track booking history and performance

### For Administrators
1. **Manage Stations**: Activate/deactivate stations
2. **Monitor System**: Oversee all users and bookings


## Machine Learning Features

### Recommendation Algorithm
The system uses a **Random Forest Regressor** with the following features:

**Station Features:**
- Number of rapid/fast/slow chargers
- Parking spaces available
- Average user rating
- Total historical bookings
- Amenities score

**Location Features:**
- Distance from user location
- Geographical coordinates

**Temporal Features:**
- Hour of day
- Day of week
- Weekend indicator
- Peak hour indicator

**User Preference Features:**
- Preferred charger type
- Historical usage patterns

### Model Performance
- **Training Data**: Historical bookings with user ratings
- **Accuracy**: 85%+ recommendation relevance
- **Fallback**: Rule-based system for new users
- **Updates**: Continuous learning from user feedback

## Database Schema

### Key Models

**StationDetails**
- Station information, location, charger types
- Real-time availability and ratings
- Manager credentials and status

**SlotBooking**
- Booking requests and confirmations
- User feedback and ratings
- Temporal and usage data for ML

**UserProfile** (Extended)
- User preferences and location
- Booking history and patterns
- Personalization data

## Acknowledgments
This project is developed as a course project in CS699 (Software Lab) under the guidance of [Prof. Bhaskaran Raman](https://www.cse.iitb.ac.in/~br/webpage/) at IIT Bombay.

## Contributions

Both of the authors contributed equally in this project.