# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py
# TODO: create requirements.txt and install

import flask
import getpass
import requests
import click
import configparser
import json
import sys
import os
import hmac
import hashlib

    
from labelord.setupfile import setup, printextra
from labelord.web import convert_time, LabelordWeb, get, post

# Structure your implementation as you want (OOP, FP, ...)
# Try to make it DRY also for your own good


@click.group('labelord')                
@click.help_option('-h', '--help')
@click.version_option(version='labelord, version 0.1')
@click.option('-c', '--config', type=click.Path(exists=True), help='Config file')    
@click.option('-t', '--token', help='Token')
@click.pass_context
def cli(ctx, config, token): 
   """
   Open config file, set session and context.
   
   Main function.
   
   :param: ``ctx`` Context, for Click
   :param: ``config`` Config file
   :param: ``token`` Token
   :return: ``None``
   """
   
   conffile = configparser.ConfigParser()
             
   if config is not None:
      conffile.read(config) 
   else:
      if os.path.isfile('./config.cfg') == True:
         conffile.read('./config.cfg')
         config = './config.cfg'
           
   
    # TODO: Add and process required app-wide options
    # You can/should use context 'ctx' for passing
    # data and objects to commands

    # Use this session for communication with GitHub
   session = ctx.obj.get('session', requests.Session())
   ctx.obj['session'] = session
   ctx.obj['config'] = config


@cli.command()  
@click.option('-t', '--token', help='Token')
@click.option('--tenv', envvar='GITHUB_TOKEN')
@click.pass_context
def list_repos(ctx, token, tenv):
   """
   List repos.
   
   Check if token provided. I do get repositories and print them.
   
   :param: ``ctx`` Context, for Click     
   :param: ``token`` Token
   :param: ``tenv`` Token if set by environment variable
   :return: ``None``
   """
   session = ctx.obj['session']
   config = ctx.obj['config']
   conffile = configparser.ConfigParser()
   conffile.optionxform = str   
   if config is not None and os.path.isfile(config) == True:
      conffile.read(config)
   
   if not token:
      if not tenv:
         if os.path.isfile('./config.cfg') == False and 'github' not in conffile:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         if 'github' in conffile and 'token' not in conffile['github']:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         else: t = conffile['github']['token']
      else: t = tenv
   else: t = token
   
   session = setup(session, t)

   repos = session.get('https://api.github.com/user/repos?per_page=100&page=1')
   a = 0
   if 'message' in repos.json() and repos.json()['message'] == 'Bad credentials':
      print("GitHub: ERROR " + str(repos.status_code) + ' - ' + repos.json()['message'], file=sys.stderr)
      sys.exit(4)

   if repos.status_code != 200:
      print("GitHub: ERROR " + str(repos.status_code) + ' - ' + repos.json()['message'], file=sys.stderr)
      sys.exit(10)

   for repo in repos.json():
      print(repo['full_name'])
      a = a+1
   
   b = 1   
   if a == 100:
      while a == 100:  
        a = 0
        b = b+1
        repos = session.get('https://api.github.com/user/repos?per_page=100&page=' + str(b)) 
        for repo in repos.json():
           print(repo['full_name']) 
           a = a+1 


@cli.command()
@click.argument('repository', required=1)
@click.option('-t', '--token', help='Token')
@click.option('--tenv', envvar='GITHUB_TOKEN')
@click.pass_context
def list_labels(ctx, repository, token, tenv):
   """
   List labels.
   
   Check if token provided. If do get all labels from repository and print them.
      
   :param: ``ctx`` Context, for Click
   :param: ``repository`` Repository from which labels will be listed
   :param: ``token`` Token
   :param: ``tenv`` Token if set by environment variable
   :return: ``None``
   """
   session = ctx.obj['session']
   config = ctx.obj['config']
   conffile = configparser.ConfigParser()
   conffile.optionxform = str
   if config is not None and os.path.isfile(config) == True:
      conffile.read(config) 
   
   if not token:
      if not tenv:
         if os.path.isfile('./config.cfg') == False and 'github' not in conffile:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         if 'github' in conffile and 'token' not in conffile['github']:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         else: t = conffile['github']['token']
      else: t = tenv
   else: t = token
   
   session = setup(session, t)
   
   a = 0
   list = session.get('https://api.github.com/repos/' + repository + '/labels?per_page=100&page=1')
   if list.status_code == 404:
      print("GitHub: ERROR " + str(list.status_code) + ' - ' + list.json()['message'], file=sys.stderr)
      sys.exit(5)
  
   if 'message' in list.json() and list.json()['message'] == 'Bad credentials':
      print("GitHub: ERROR " + str(list.status_code) + ' - ' + list.json()['message'], file=sys.stderr)
      sys.exit(4)
        
   if list.status_code != 200:
      print("GitHub: ERROR " + str(list.status_code) + ' - ' + list.json()['message'], file=sys.stderr)
      sys.exit(10)
      
   for label in list.json():
      print(u'\u0023' + label['color'] + ' ' + label['name'])
      a = a+1 
        
   b = 1 
     
   if a == 100:
      while a == 100: 
        a = 0
        b = b+1
        list = session.get('https://api.github.com/repos/' + repository + '/labels?per_page=100&page=' + str(b))
     
        for label in list.json():
           print(u'\u0023' + label['color'] + ' ' + label['name'])
           a = a+1
          

@cli.command()                      
@click.argument('mode', type=click.Choice(['update', 'replace']))
@click.option('-r', '--template-repo', help="Add a template repo.")
@click.option('-a', '--all-repos', is_flag=True, help='All available repos.')
@click.option('-d', '--dry-run', is_flag=True, help='Dry run')
@click.option('-v', '--verbose', is_flag=True, help='Verbose mode')
@click.option('-q', '--quiet', is_flag=True, help='Quiet mode')
@click.option('-t', '--token', help='Token')
@click.option('--tenv', envvar='GITHUB_TOKEN')
@click.pass_context
def run(ctx, mode, template_repo, all_repos, dry_run, verbose, quiet, token, tenv):
   """
   Run a labels update/replace.
   
   Check if token provided. If do get labels (as template ones and changable ones) and do the magic - change them the way that all repositories has same (template) labels (dont forget update/replace mode).
      
   :param: ``ctx`` Context, for Click
   :param: ``mode`` Mode of run [update, replace]
   :param: ``template_repo`` Template repositary from which labels will be using
   :param: ``all_repos`` Flag, if changes will be taken in all repositaries from ``list_repos`` command
   :param: ``dry_run`` Flag, if changes will be canceled
   :param: ``verbose`` Flag, set verbose mode
   :param: ``quiet`` Flag, set quiet mode (no output)
   :param: ``token`` Token
   :param: ``tenv`` Token if set by environment variable
   :return: ``None``
   """
   config = ctx.obj['config']
   conffile = configparser.ConfigParser()
   conffile.optionxform = str
   if config is not None and os.path.isfile(config) == True:
      conffile.read(config)
   session = ctx.obj['session']
   
   if not token:
      if not tenv:
         if os.path.isfile('./config.cfg') == False and 'github' not in conffile:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         if 'github' in conffile and 'token' not in conffile['github']:
            print('No GitHub token has been provided', file=sys.stderr)
            sys.exit(3)
         else: t = conffile['github']['token']
      else: t = tenv
   else: t = token  
   
   session = setup(session, t)
   
   repos = []
   errors = 0
   sum = 0
   
   # vyber, kde menit labely
   if not all_repos:
      if not 'repos' in conffile:
         print('No repositories specification has been found', file=sys.stderr)
         sys.exit(7)
      else: 
         for repo in conffile['repos']:
            if conffile.getboolean('repos', repo):
               repos.append(repo)
   else: 
      reposlist = session.get('https://api.github.com/user/repos?per_page=100&page=1')
      if 'message' in reposlist.json() and reposlist.json()['message'] == 'Bad credentials':
         print("GitHub: ERROR " + str(reposlist.status_code) + ' - ' + reposlist.json()['message'], file=sys.stderr)
         sys.exit(4)

      if reposlist.status_code != 200:
         print("GitHub: ERROR " + str(reposlist.status_code) + ' - ' + reposlist.json()['message'], file=sys.stderr)
         sys.exit(10)

      for repo in reposlist.json():
         repos.append(repo['full_name'])
   
   c = 0
   labels = {}
   ok = 0
   level = 1
   error_code = 0
   if verbose: level = 2
   if quiet: level = 0
   if verbose and quiet: level = 1
   err = 0
   if dry_run: err = 2
   
   # vyber labelu
   if not template_repo:
      if not 'others' in conffile:
         if not 'labels' in conffile:
            print('No labels specification has been found', file=sys.stderr)
            sys.exit(6)
         else: 
            # update labels z configu
            for label in conffile['labels']:
               labels[label] = conffile['labels'][label]   
            labels_lower = {k.lower():v for k,v in labels.items()}      
      else: 
         # update template repo z configu
         list = session.get('https://api.github.com/repos/' + conffile['others']['template-repo'] + '/labels?per_page=100&page=1')
         if list.status_code == 404: 
            printextra(level, conffile['others']['template-repo'] + '; ' + str(list.status_code) + ' - ' + list.json()['message'], 'LBL', 1)
            errors = errors + 1
         for label in list.json():
            labels[label['name']] = label['color']
         labels_lower = {k.lower():v for k,v in labels.items()}     
   else: 
      # update --template-repo z prepinace
      list = session.get('https://api.github.com/repos/' + template_repo + '/labels?per_page=100&page=1')
      if list.status_code == 404: 
         printextra(level, template_repo + '; ' + str(list.status_code) + ' - ' + list.json()['message'], 'LBL', 1)
         errors = errors + 1
      for label in list.json():
         labels[label['name']] = label['color'] 
      labels_lower = {k.lower():v for k,v in labels.items()}  
   
   for repo in repos:
      sum = sum + 1
      list = session.get('https://api.github.com/repos/' + repo + '/labels?per_page=100&page=1') 
      if list.status_code != 200:
         printextra(level, repo + '; ' + str(list.status_code) + ' - ' + list.json()['message'], 'LBL', 1)
         error_code = 10
         errors = errors + 1
         continue
      for label in list.json():
         if label['name'] in labels_lower:
            for l in labels:
               if l.lower() == label['name']:
                  break
            if labels_lower[label['name']] != label['color']:
               colors = json.dumps({"name": l, "color": labels_lower[label['name']]})
               if not dry_run: req = session.patch('https://api.github.com/repos/' + repo + '/labels/' + label['name'].lower(), data=colors) 
               if dry_run or req.status_code == 200:
                  printextra(level, repo + '; ' + l + '; ' + labels_lower[label['name']], 'UPD', err)
               else:
                  printextra(level, repo + '; ' + l + '; ' + labels_lower[label['name']] + '; ' + str(req.status_code) + ' - ' + req.json()['message'], 'UPD', 1)
                  errors = errors + 1
         elif mode == 'replace':
            if not dry_run: req = session.delete('https://api.github.com/repos/' + repo + '/labels/' + label['name'])
            if dry_run or req.status_code == 204:
               printextra(level, repo + '; ' + label['name'] + '; ' + label['color'], 'DEL', err)
            else:
               printextra(level, repo + '; ' + label['name'] + '; ' + label['color'] + '; ' + str(req.status_code) + ' - ' + req.json()['message'], 'DEL', 1)
               errors = errors + 1
      for label in labels:
         for label2 in list.json():
            if label.lower() == label2['name']: ok = 1
         if ok != 1: 
            colors = json.dumps({"name": label, "color": labels[label]})
            if not dry_run: req = session.post('https://api.github.com/repos/' + repo + '/labels', data=colors) 
            if dry_run or req.status_code == 201:
               printextra(level, repo + '; ' + label + '; ' + labels[label], 'ADD', err)
            else:
               printextra(level, repo + '; ' + label + '; ' + labels[label] + '; ' + str(req.status_code) + ' - ' + req.json()['message'], 'ADD', 1)
               errors = errors + 1
               error_code = 10
                       
         ok = 0
   if errors != 0:      
      printextra(4+level, str(errors) + ' error(s) in total, please check log above', '', err)      
   else:
      printextra(4+level, str(sum) + ' repo(s) updated successfully', '', err)    
   
   sys.exit(error_code)         

# TODO: instantiate LabelordWeb app
# Be careful with configs, this is module-wide variable,
# you want to be able to run CLI app as it was in task 1.
from flask import Flask, current_app, render_template, request, Response, json
app = LabelordWeb(__name__)


@cli.command()
@click.option('-h', '--host', default='127.0.0.1', help='Host address')
@click.option('-p', '--port', default='5000', help='Port')
@click.option('-d', '--debug', is_flag=True, envvar='FLASK_DEBUG', help='Debug mode')
@click.pass_context
def run_server(ctx, host, port, debug):
    """
    Run a server with Flask app.
         
    :param: ``ctx`` Context, from Click
    :param: ``host`` Hostname for interface (default 127.0.0.1)
    :param: ``port`` Port for interface (default 5000)     
    :param: ``debug`` Flag, set debug mode
    :return: ``None``
    """
    # TODO: implement the command for starting web app (use app.run)
    # Don't forget to app the session from context to app
    config = ctx.obj['config']
    if config is not None and os.path.isfile(config) == True:
      os.environ['LABELORD_CONFIG'] = config  
      app.reload_config()
     
    #current_app.session = ctx.obj['session']
    app.run(debug=debug, host=host, port=int(port))


def main():
    cli(obj={})