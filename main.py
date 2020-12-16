#!/usr/bin/env python3

import sys # For command-line arguments
import os
import subprocess # For running shell commands
import shodan # For Shodan
import smtplib, ssl # For email
from crontab import CronTab # For creating crontabs

###############################################################
#                                                             #
#       Shodan API Automated Search Tool - Main Program       #
#       This program creates a cronjob that will allow        #
#       users to see changes/updates to their Shodan          #
#       searches at whatever time interval they desire.       #
#                                                             #
#                                                             #
#                   Author: Casey Lewis                       #
#                                                             #
###############################################################

# Define global variables for the program
SHODAN_API_KEY = "" # Give the program your API Key
cron = CronTab(os.getlogin()) # Create CronTab
path = os.getcwd()
api = shodan.Shodan(SHODAN_API_KEY) # Create Shodan API tool

# Set up Email Service
port = 465 # You may change to your desired SSL port
email = "" # Enter your email
password = "" # Enter your email password
context = ssl.create_default_context()

result_aspects = [
    "os",
    "ip_str",
    "hostnames",
    "hash",
    "org",
    "isp",
    "asn",
    "port",
    "location",
    "timestamp",
    "domains"
]

# The introductory message when the program starts
def intro():
    return_str = ""
    return_str += "Welcome to the SAAST (Shodan API Automated Search Tool)\n"
    return_str += "For help, enter '?' to be shown a help page\n"
    return return_str

# Print the SAAST help guide to stdout
def help():
    print("SAAST Help Guide")
    print("Welcome to the Shodan API Automated Search Tool (SAAST)! SAAST uses the Shodan databases and automatically creates a cron job to execute your search query at your desired interval.\n")
    print("Before you run SAAST, you are be required to enter 2 inputs: ")
    print("\t1. Your Shodan API Key. You can find your Shodan API Key by registering for a free account at https://www.shodan.io/?language=en. You must enter your API key in main.py on line 23, in the variable SHODAN_API_KEY")
    print("\t2. Your email address and password. Since this program should only be executed locally, there is no security concern with having the email and password in the source code (lines 30-31. NOTE: NEVER upload it to GitHub or any public location). These should be entered in the email and password fields in main.py.")
    print("\nOnce this information has been entered, you may run SAAST. Upon execution, you will be asked to enter 5 inputs:")
    print("\t1. Your Shodan Search Query. You should test your search query on https://shodan.io before using it in SAAST. ")
    print("\t2. Your Shodan Search Facets. Go to https://api.shodan.io/shodan/host/search/facets?key={YOUR_API_KEY} for a list of all available facets.")
    print("\t3. Which result aspects you'd like to save. To view a full list, type 'r' when prompted.")
    print("\t4. Your desired cron recurrence. How often you would like your search to execute. The syntax is as follows (<Field (Range of acceptable values)>:")
    print('\t   <Minute (0-59)> <Hour (0-23)> <Day of month (1-31)> <Month (1-12)> <Day of week (0-6; 0 being Sunday)>')
    print('\t   Example input: 0 15 * 1 2-6  <-- Translate to "repeat every Tuesday through Saturday in January at 3pm')
    print("\t5. Your alert type. You can receive either no alert, an alert once the results file reaches a specified number of lines, or an alert once a given string is found in the output file.")
    print("You may exit the program now by entering 'q' to find the above information. If you have already logged your API key, you may continue by entering your search query now:\n") 


# Print the list of result options to stdout
def result_list():
    print("\nPossible result aspects:")
    for e in result_aspects:
        print(e)

# Take the user's search criteria, call the API, and return the results
def execute_search(query, facets, result_list, alert_type, alert_param):
    print("Executing search criteria...")
    # Wrap the request in a try/except block to catch errors
    try:
        # Search Shodan
        results = api.search(query, facets=facets)
        i = 0

        # Show the results
        ip = 'ip_str'
        print(results['total'], " results found")
        f = open(path + "/saast_results.csv", "w")

        # Add the csv column headers
        result_list = result_list.split()
        if result_list[0] == 'a':
            for r in result_aspects:
                f.write(r + ",")
        else:
            for r in result_list:
                f.write(r + ",")
        f.write('\n')

        for result in results['matches']:
            # Save only the specified aspects of the result set
            if result_list[0] == 'a':
                result_list = result_aspects
            for r in result_list:
                f.write('{}'.format(result[r]).replace(",", "|")) # Replace all commas to avoid errors in CSV formatting
                f.write(',')
            f.write('\n')
        f.close()

        send_email_alert(alert_type, alert_param)

    except shodan.APIError as e:
        print('Error: {}'.format(e))
        exit(1)

def create_script(query, facets, result_list, alert_type, alert_param):
    script_string = "python " + path + "/main.py script '" + query + "' '" + facets + "' '" + result_list + "' '" + str(alert_type) + "' '" + alert_param + "'"
    f = open("" + path + "/saast_script.sh", "w")
    f.write('#!/bin/bash')
    f.write('\n')
    f.write(script_string)
    f.close()
    subprocess.run(["chmod", "+x", "" + path + "/saast_script.sh"])

def send_email_alert(alert_type, alert_param):
    # Send the email (if matching result found); do nothing otherwise
    if alert_type == 2 or alert_type == 3:
        email_message = ""
        if alert_type == 2:
            line_count = len(open("" + path + "/saast_results.csv").readlines(  ))
            if line_count >= int(alert_param):
                email_message = """\
Subject: SAAST Alert

File has reached or exceeded the specified number of lines: """ + alert_param
        if alert_type == 3:
            f = open("" + path + "/saast_results.csv", "r")
            if alert_param in f.read():
                email_message = """\
Subject: SAAST Alert

Your results file contains the string """ + alert_param
        if email_message != "":
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(email, password)
                server.sendmail(email, email, email_message) # Change the first argument if you'd like to send from a different email, or the second if you'd like to send to a different email

def main():
    # Print the welcome message
    print(intro())

    # Check if this is a script execution, otherwise, ignore any command line arguments given
    if len(sys.argv) > 1:
        if(sys.argv[1] == "script"):
            print("args: " + sys.argv[2] + " " + sys.argv[3] + " " + sys.argv[4] + " " + sys.argv[5] + " " + sys.argv[6])
            execute_search(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
            exit(0)

    # Capture the user's desired search query from stdin
    search_query = input("Enter your search criteria now:\n")

    # See if the user entered a search query or requested the help page
    validated = False
    while not validated:
        # If the user requested to see the help page
        if search_query == "?":
            help()
            search_query = input()
        # Else if the user wants to quit the program
        elif search_query == 'q':
            exit(0)
        # Any other string is technically a valid Shodan search
        else:
            validated = True

    # Capture the user's desired search facets (if any) from stdin
    search_facets = input("If you have any search facets you would like to add to your query, enter them now. Otherwise, press Enter to continue.\n")

    # Capture the result aspects the user would like to save
    result_aspects = input("Enter the result values you'd like to save, separated by a single space (or enter 'a' for all). Enter 'r' for a list of all possible values:\n")
    validated = False
    while not validated:
        if result_aspects == 'r':
            result_list()
            result_aspects = input("\nEnter the result values you'd like to save, separated by a single space (or enter 'a' for all). Enter 'r' for a list of all possible values:\n")
        else:
            validated = True         
    
    # Capture all 5 crontab parameters
    cron_parameters = input("Enter your crontab parameters (how often would you like this tool to run?):\n")

    alert_param = ""
    # Reset the validated variable for the next validation
    validated = False

    # Get alert type
    alert_type = int(input('''
Choose the alert type you would like to receive by entering the corresponding number:
1. Never send me an alert via email
2. Alert me once the file reaches a specific number of entries
3. Alert me once the file contains a specific string\n'''))

    while not validated:
        if alert_type == 1:
            alert_param = ""
            validated = True
        elif alert_type == 2:
            alert_param = input("Alert me once the file reaches this number of lines (Maximum 10000; enter your choice now):\n")
            if alert_param.isdigit():
                validated = True
            else:
                while not alert_param.isdigit():
                    alert_param = input("Error: Please enter a positive integer (Maximum 10000; enter your choice now):\n")
                validated = True
        elif alert_type == 3:
            alert_param = input("Alert me once the file contains this string (Enter string now):\n")
            validated = True
        else:
            alert_type = input("Error: Please enter a number 1, 2, or 3:\n")

    # Execute the initial search
    execute_search(search_query, search_facets, result_aspects, alert_type, alert_param)

    # Create Script
    create_script(search_query, search_facets, result_aspects, alert_type, alert_param)

    # Create the CronTab
    job = cron.new(command='' + path + '/saast_script.sh', comment='Shodan API Automated Search')
    job.setall(cron_parameters)
    cron.write()
    job.enable()

# Run main upon program execution
main()
