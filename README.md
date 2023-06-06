# webapplicationproject
A simple on-call ticket web database application was created based on the requirements of Amazon’s Alexa Shopping team.

**Current functions:**
* Register User (Creates in database)
* Login User
* Logout User
* Create Tickets (Creates in database)
* View Tickets (Reads database)
* View User Tickets (Reads database)
* View On Call (Reads database)
* Set On Call (Updates database)
* Update Ticket (Updates database)
* Remove Ticket (Deletes in database - ADMIN)
* Remove User (Deletes in database - ADMIN)

**Database Tables:**
* Ticket
* EngineerUser (Based on django.contrib.auth.models.User)
