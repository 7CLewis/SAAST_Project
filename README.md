# SAAST - Shodan API Automated Search Tool

The Shodan API Automated Search Tool is designed for users familiar with Shodan to automate their queries and be alerted when certain criteria is met. 
As it stands, Shodan does not allow for any sort of automated searching. SAAST will automatically create a cronjob for users and execute the desired search
the desired interval

## How To Use
When you run SAAST, you will be asked for 7 inputs:
1. Your Shodan API Key. You can find your Shodan API Key by registering for a free account at https://www.shodan.io/?language=en. 
   You must enter your API key in `main.py` on line 23, in the variable `SHODAN_API_KEY`
1. Your email address and password. Since this program should only be executed locally, there is no security concern with having
   the email and password in the source code (NEVER upload it to GitHub or any public location). These should be entered in
   the `email` and  `password` fields in `main.py`.
1. Your Shodan Search Query. You should test your search query on https://shodan.io before using it in SAAST.
1. Your Shodan Search Facets. Go to https://api.shodan.io/shodan/host/search/facets?key={YOUR_API_KEY} for a list of all available facets.
1. Which result aspects you'd like to save. To view a full list, type 'r' when prompted.
1. Your desired cron recurrence. How often you would like your search to execute. The syntax is as follows (<Field (Range of acceptable values)>:
`<Minute (0-59)> <Hour (0-23)> <Day of month (1-31)> <Month (1-12)> <Day of week (0-6; 0 being Sunday)>`
Example input: `0 15 * 1 2-6` <-- Translates to "repeat every Tuesday through Saturday in January at 3pm
1. Your alert type. You can receive either no alert, an alert once the results file reaches a specified number of lines, or an alert once a given string 
   is found in the output file.

Here's an example of what a user might do. Assume someone wants to find all of the devices in Boise, ID that contain the string "default password". They will
run SAAST as follows:
```
$ ./main.py

Welcome to SAAST (Shodan API Automated Search Tool)
For help, enter '?' to be shown a help page

Enter your search criteria now:
$ "default password"

If you have any search facets you would like to add to your query, enter them now. Otherwise, press Enter to continue.
$ [Enter]
Enter the result values you'd like to save, separated by a single space (or enter 'a' for all). Enter 'r' for a list of all possible values:
$ ip_str location

Enter your crontab parameters (how often would you like this tool to run?):
$ * * * * *

Choose the alert type you would like to receive by entering the corresponding number:
1. Never send me an alert via email
2. Alert me once the file reaches a specific number of entries
3. Alert me once the file contains a specific string
$ 3
Alert me once the file contains this string (Enter string now):
$ Boise
```

Success! The user will now be alerted via email whenever a device containing the string "default password" is found in Boise.

As you can see, there are a variety of use cases for SAAST. Please use it wisely and ethically. Keep in mind this program is still a work in progress,
so use it at your own discretion, and feel free to report any bugs that you may encounter.

Thank you, and happy searching!
