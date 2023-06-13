# webapplicationproject
A simple on-call ticket web database application was created based on the requirements of Amazon’s Alexa Shopping team.

## Table of Contents
- [App site](#app-site)
  - [Unregistered Users](#unregistered-users)
  - [Registered Users](#registered-users)
- [Admin Site](#admin-site)
  - [App](#app)
  - [Logs](#logs)
- [Database Tables](#database-tables)

## App site
### Unregistered Users
- Home page
- Login page - form for user to login 
- Register Page - form for user to register (inserts into application_engineeruser table)

### Registered Users
- Home page
- Create ticket - form for user to create a ticket (inserts into application_ticket table)
- Edit ticket - form for user to edit a ticket (updates application_ticket table)
- Delete ticket - Requires admin user permissions (deletes from application_ticket table)
- My tickets - views tickets created by user in a table (reads application_ticket table)
- All tickets - views tickets created by all users in a table (reads application_ticket table)
- Set on call - form for user to change current on call (updates application_engineeruser table)
- View on call - views current on call (reads application_engineeruser table)
- Logout user - logs user out of the application

## Admin Site
### App
#### Tickets
- View tickets (reads application_ticket table)
- Add tickets (inserts into application_ticket table)
- Change tickets (updates application_ticket table)
- Delete tickets (deletes from application_ticket table)

#### Users
- View users (reads application_engineeruser table)
- Add users (inserts into application_engineeruser table)
- Change users (updates application_engineeruser table)
- Delete users (deletes from application_engineeruser table)

### Logs
#### Admin Logs
- View log entries of admin user actions on the admin site (reads django_admin_log table)

#### User Logs
- View log entries of user actions on the application site (reads logger_customstatuslog table)

## Database Tables

| Table name               | Model                                                          | Notes                          |
|--------------------------|----------------------------------------------------------------|--------------------------------|
| application_engineeruser | EngineerUser (Based on django.contrib.auth.models.User)        | Stores engineer user details   |
| application_ticket       | Ticket                                                         | Stores ticket details          | 
| logger_customstatuslog   | CustomStatusLog (Based on django_db_logger.models.StatusLog)   | Stores user log entry details  | 
| django_admin_log         | CustomLogEntry (Based on django.contrib.admin.models.LogEntry) | Stores admin log entry details |
