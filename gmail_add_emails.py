#!/usr/bin/env python
#
# gmail_add_emails.py - Add a file of emails into a gmail contact list.
#
# Author: chrisken@ck37.com (hat tip to libgmail example code)
#
# License: GPL 2.0
#

import os
import sys
import logging
import libgmail

# Number of consecutive fails to allow before aborting.
max_consecutive_fails = 20

# How many rows to skip before printing a status update line.
status_update_frequency = 50

if __name__ == "__main__":
    import time
    from getpass import getpass

    hide_output = open("/dev/null","w")
    show_output = sys.stdout

    try:
        account = sys.argv[1]
        email_file = sys.argv[2]
    except IndexError:
        print "Usage: %s <account> <email_file>" % sys.argv[0]
        raise SystemExit
        
    password = getpass("Password: ")

    ga = libgmail.GmailAccount(account, password)

    print "\nPlease wait, logging in..."

    try:
        ga.login()
    except libgmail.GmailLoginFailure:
        print "\nLogin failed. (Wrong username/password?)"
        raise SystemExit
    else:
        print "Log in successful.\n"

    input = open(email_file, 'r')
    status = open('.' + email_file + '-status', 'r+')

    good = 0
    bad = 0
    line_count = 0

    starting_line = status.readline()
    if starting_line:
      starting_line = int(starting_line.strip())
    else:
      starting_line = 0
    
    # Skip to the starting line.
    while line_count < starting_line:
      input.readline()
      line_count += 1
      
    print "Starting at line %s." % line_count

    def report_status():
      print "Line: %s. Added: %s. Failed: %s." % (line_count, good, bad)

    def save_line_count(line_count):
      # Go back to the beginning of the file.
      status.seek(0)
      # Save the line number.
      status.write(str(line_count))

    consecutive_fails = 0

    for email in input:
      # Split off anything after the first comma, in case it's a csv.
      email = email.strip().split(",")[0]
      # Make sure there aren't any quotes as gmail won't strip them.
      email = email.strip('"')

      contact = libgmail.GmailContact("", email)
      contact.setMoreInfo({'Personal': (('o', 'auto_import'))})

      try:
        # Redirect stdout in case of error.
        sys.stdout = hide_output
        ga.addContact(contact)
      except Exception:
        sys.stdout = show_output
        print "Could not add %s." %email
        bad += 1
        consecutive_fails += 1
      else:
        sys.stdout = show_output
        good += 1
        consecutive_fails = 0
     
      line_count += 1

      save_line_count(line_count)

      # Could potentially delay a bit so we don't overload, but not needed.
      # time.sleep(0.1)

      if line_count % status_update_frequency == 0:
        report_status()

      # Abort if we have failed too many times in a row.
      if consecutive_fails >= max_consecutive_fails:
        print "Error: aborting due to too many consecutive failures."
        # Revert line count so we can re-run the recent failures.
        save_line_count(line_count - max_consecutive_fails)
        break

    # Ended for loop of emails in file.  

    report_status()
    input.close()
    status.close()

