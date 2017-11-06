# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py
# TODO: create requirements.txt and install

import getpass
import requests

def setup(session, token):
   session.headers = {'User-Agent': 'Python'}
   def token_auth(req):
      req.headers['Authorization'] = 'token ' + token
      return req

   session.auth = token_auth
   
   return session
   
def printextra(level, text, label, err): 
   if level == 0:
      return
   if level == 1:
      if err == 1:
         print('ERROR: ' + label + '; ' + text)
         return
   if level == 2:
      if err == 0:
         print('[' + label + '][SUC] ' + text)
      if err == 1:
         print('[' + label + '][ERR] ' + text)               
      if err == 2:
         print('[' + label + '][DRY] ' + text)
   if level > 4:
      if level == 6:
         print('[SUMMARY] ' + text) 
      if level == 5:
         print('SUMMARY: ' + text)         

