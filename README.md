# Adding UCI Webreg Courses to Google Calendar

 Created using Selenium technology to log into UCI Webreg and view the user's list of courses for the quarter. User can directly add these courses to their calendar using Google's Calendar API.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python 3+
* Chrome
* A Google Account

### Installing

* install Selenium

```
pip install selenium
```

* install Chrome Driver (save the path of file)

https://chromedriver.chromium.org/

* install Google API Client

```
pip install google-api-python-client
```

* create google credentials to access calendar (save the path of the file)

    *The youtube video linked below gives clear instructions on how to create and save the credentials.
https://www.youtube.com/watch?v=j1mh0or2CX8&t=1456s

* download github repository

    * can use github link: https://github.com/Vakhshoori101/UCI_Webreg_to_Google_Calendar.git
    
    * can download as zip file

## Features

* login and logout of Webreg account
* view study list
* add courses from study list to Google Calendar

## Deployment

1. Fill out information in "config.py"

```
config = {
    "username" : "",                   # Webreg Username
    "password" : "",                   # Webreg Password
    "client_secret_path" : "",         # Path to find json file containing User's Google Credentials
    "chrome_driver_path" : ""          # Path for Chrome Driver
}
```

2.  Create new file to use features 

```
from webreg import webreg

w = webreg()

# Logging into UCI Webreg
w.login()

# Returns a list of UCI Courses and their information
print(w.get_study_list())

# Adds study list to Google Calendar
# While running, will require authorization code to connect to the calendar
w.add_classes_to_calendar()

# Log out of UCI Webreg
w.logout()

```

## Enjoy!

