#!/bin/env python

import mechanize
import getpass
import io

url_course = "https://moodle.ucl.ac.uk/course/view.php?id=10648"
output_filename = "grades.csv"
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"

def main():
    br = init_browser()
    moodle_login(br)
    select_grade_download_form(br)
    gradesheet = download_grades(br)
    write_file(gradesheet)

def init_browser():
    """Get browser object with settings so that Moodle won't block access."""
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.addheaders = [("User-agent",user_agent)]
    return br

def moodle_login(browser):
    """Fill in login form on Moodle site."""
    response = browser.open(url_course)
    browser.select_form(predicate=is_login_form)
    login_form = browser.form
    username = input("Enter username for Moodle login: ")
    password = getpass.getpass("Enter password for Moodle login: ")
    login_form['username'] = username
    login_form['password'] = password
    browser.submit()
    if not logged_in_to_moodle(browser):
        raise Exception("Not logged in")

def is_login_form(form):
    """Check if given form has expected username and password
    controls."""
    try:
        form.find_control(name='username',type='text')
        form.find_control(name='password',type='password')
        return True
    except mechanize.ControlNotFoundError:
        return False

def is_download_form(form):
    """Check if given form has expected download control."""
    try:
        submit = form.find_control(name='submitbutton',type='submit')
        label  = submit.get_labels()[0]
        return "Download" == label.text
    except mechanize.ControlNotFoundError:
        return False

def logged_in_to_moodle(browser):
    """Check if we are logged in to Moodle so can see 'My courses'."""
    try:
        browser.find_link(text="My courses")
        return True
    except mechanize.LinkNotFoundError:
        return False

def select_grade_download_form(browser):
    """Select form to download grades as plain text (CSV)."""
    browser.open(url_course)
    browser.follow_link(text="Gradebook setup")
    browser.follow_link(text="Export")
    browser.follow_link(text="Plain text file")
    browser.select_form(predicate=is_download_form)

def download_grades(browser):
    """Submit form and retrieve data."""
    download_response = browser.submit()
    data = download_response.get_data()
    string_data = data.decode()
    return string_data

def write_file(string_data):
    """Write multiline string to output file."""
    with open(output_filename,'w',encoding="utf-8") as f:
        f.write(string_data)

if __name__ == '__main__':
    main()
