from selenium import webdriver
from bs4 import BeautifulSoup
import re
from google_calendar import Calendar
from config import config

class webreg:

    def __init__(self):
        self.username = config["username"]
        self.password = config["password"]
        self.chrome_driver_path = config["chrome_driver_path"]

        # setting driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(self.chrome_driver_path, options=chrome_options)
        self.driver.implicitly_wait(2)
        self.driver.get("https://www.reg.uci.edu/cgi-bin/webreg-redirect.sh")


    def login(self):
        # adds username to textfield
        self.driver.find_element_by_id("ucinetid").send_keys(self.username)
        # adds password to textfield
        self.driver.find_element_by_id("password").send_keys(self.password)
        # clicks login button
        self.driver.find_element_by_name("login_button").click()

        # check if incorrect username or password / if student is currently in use
        login_error = self.driver.find_elements_by_class_name("webauth-alert")
        login_error += self.driver.find_elements_by_class_name("WebRegErrorMsg")
        if login_error or not self.driver.find_element_by_xpath("//form[5]//input[4]"):
            self.driver.close()
            raise Exception(login_error[0].text)

    def logout(self):
        # click logout button
        self.driver.find_element_by_class_name("WebRegLogoutButton").click()
        self.driver.close()

    def get_html(self)->str:
        study_list = self.driver.find_element_by_class_name("studyList")
        outerhtml = study_list.get_attribute('outerHTML')
        return outerhtml

    def reformat(self, l:list)->list:
        courses = [{} for i in range(len(l))]
        day_tracker = {"M":"MO ", "T":"TU ", "W":"WE ", "F":"FR ", " ":""}
        for course in range(len(courses)):
            c = list(filter(None, l[course].split(" ")))
            # add course number
            courses[course]['Number'] = c[0]
            if not c[2].isdigit():
                c[1] += c[2]
                del c[2]
            c[1] += " " + c[2]
            del c[2]
            del c[3]
            # add course name
            courses[course]['Name'] = c[2] + " " + c[1]
            for day in range(6, len(c)):
                if len(c[day]) == 1:
                    c[5] += " " + c[day]
                else:
                    for d in range(day - 6):
                        del c[6]
                    break
            # add list of class days
            day = l[course][41:46]
            class_day = ''
            for d in range(len(day)):
                if day[d] == "T" and d == 3:
                    class_day += "TH "
                else:
                    class_day += day_tracker[day[d]]
            courses[course]["Days"] = class_day.strip().split()
            # add course time
            if c[6] == "ON":
                courses[course]["Time"] = c[6] + c[7]
                del c[7]
            else:
                courses[course]["Time"] = c[6]
            c[7] += " " + c[8]
            del c[8]
            # add course location
            courses[course]["Location"] = c[7]
        return courses

    def parse_html(self, html:str)-> list:
        parsed = BeautifulSoup(html, "html.parser")
        text = parsed.get_text()
        # gets rid of blank lines
        text = [line.strip() for line in text.split("\n") if not line.strip() == ""]
        # using regular expressions to find lines containing 5 digit course ID
        courses = [line for line in text if not re.match(r'\d{5}', line.strip()) is None]
        return self.reformat(courses)


    def get_study_list(self)->list:
        # go to study list
        self.driver.find_element_by_xpath("//form[5]//input[4]").click()
        # get html
        return self.parse_html(self.get_html())

    def add_classes_to_calendar(self):
        calendar = Calendar()
        for course in self.get_study_list():
            if course["Time"] != "ON LINE":
                calendar.add_event(course)



