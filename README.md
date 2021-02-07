# LightCal
An SMS interface for your Google Calendar using the Python APIs for Twilio and Google Calendar.

This is primarily for those who are looking to practice digital minimalism, and so decide to downgrade from a smartphone to a dumbphone.
In its current state, you'll have to obtain your own Twilio number, set up your own Google Calendar app and also find a server to run this Flask based app on.

The two main parts of the project are:
  1.) 'scheduled_tasks.py', which is used automatically to send the user reminders of their calendar events, and
  2.) 'web_app.py,' which handles the interactivity between user and server (adding and deleting events, for instance.)
