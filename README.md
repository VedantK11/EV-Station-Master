# EV-Station-Master
# Project Overview
The global shift towards electric vehicles (EVs) is rapidly increasing, creating a growing demand for electric vehicle charging infrastructure. However, one significant challenge EV users face is the potential for long wait times at charging stations, leading to inconvenience and frustration. To address this issue, we propose the development of an Electric Vehicle Charging Reservation and Recommendation System.

### Charging Station Database
- Comprehensive database of available charging stations.
- Real-time updates on station availability.
# Database : Postgres

## Profiles
### User
1. Registration and profile creation.
2. Browsing available charging stations.
3. Selecting preferred station, date, and time.
4. Requesting booking reservation.
5. Receiving booking confirmation and reminders.

### Station Manager
1. Registration and profile creation for the particular station.
2. Accepting and Rejecting booking requests.
3. Profile upgrade.

### Admin
1. Validating station requests.
2. Suspend or deactivate stations as needed.

## Project Implementation
1. Clone the project
2. In Project/Project/settings.py: Setup Database parameters
3. Now execute python3 manage.py runserver