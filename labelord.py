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

# Structure your implementation as you want (OOP, FP, ...)
# Try to make it DRY also for your own good


@click.group('labelord')                
@click.help_option('-h', '--help')
@click.version_option(version='labelord, version 0.1')
@click.option('-c', '--config', type=click.Path(exists=True), help='Config file')    
@click.option('-t', '--token', help='Token')
@click.pass_context
def cli(ctx, config, token):
   
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
   """List repos."""
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
   """List labels."""
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

#####################################################################
# STARING NEW FLASK SKELETON (Task 2 - flask)


class LabelordWeb(flask.Flask):

   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
        # You can do something here, but you don't have to...
        # Adding more args before *args is also possible
        # You need to pass import_name to super as first arg or
        # via keyword (e.g. import_name=__name__)
        # Be careful not to override something Flask-specific
        # @see http://flask.pocoo.org/docs/0.12/api/
        # @see https://github.com/pallets/flask

   def inject_session(self, session):
        # TODO: inject session for communication with GitHub
        # The tests will call this method to pass the testing session.
        # Always use session from this call (it will be called before
        # any HTTP request). If this method is not called, create new
        # session.
        self.session = session

   def reload_config(self):
        # TODO: check envvar LABELORD_CONFIG and reload the config
        # Because there are problems with reimporting the app with
        # different configuration, this method will be called in
        # order to reload configuration file. Check if everything
        # is correctly set-up
        
        conffile = configparser.ConfigParser()
        conffile.optionxform = str
        
        if 'LABELORD_CONFIG' in os.environ:
           config = os.environ['LABELORD_CONFIG']
           conffile.read(config) 
        else:
           if os.path.isfile('./config.cfg') == True:
              conffile.read('./config.cfg')
              config = './config.cfg'
        
        if os.path.isfile('./config.cfg') == False and 'github' not in conffile:
           print('No GitHub token has been provided', file=sys.stderr)
           sys.exit(3)
        if 'github' in conffile and 'token' not in conffile['github']:
           print('No GitHub token has been provided', file=sys.stderr)
           sys.exit(3)
        else: self.token = conffile['github']['token']
        
        self.session = setup(self.session, self.token)
        
        if 'github' in conffile and 'webhook_secret' not in conffile['github']:
           print('No webhook secret has been provided', file=sys.stderr)
           sys.exit(8)
        else: self.secret = conffile['github']['webhook_secret']
        
        self.repos = []
        if not 'repos' in conffile:
           print('No repositories specification has been found', file=sys.stderr)
           sys.exit(7)      
        for repo in conffile['repos']:
           if conffile.getboolean('repos', repo):
              self.repos.append(repo)  
        
        self.labels = {}
        if 'labels' in conffile:
           for label in conffile['labels']:
              self.labels[label] = conffile['labels'][label]
              
        self.ename = ''
        self.dname = ''                 


# TODO: instantiate LabelordWeb app
# Be careful with configs, this is module-wide variable,
# you want to be able to run CLI app as it was in task 1.
from flask import Flask, current_app, render_template, request, Response, json
app = LabelordWeb(__name__)

# TODO: implement web app
# hint: you can use flask.current_app (inside app context)

@app.template_filter('link')
def convert_time(text):
    """Convert the repo name to link"""
    return 'https://github.com/' + text

@app.route('/', methods=['GET'])
def get():
   if not current_app.session:
      session = requests.Session()
      current_app.inject_session(session)
   if not current_app.repos:
      current_app.reload_config()   
   return render_template('get.html', repos=current_app.repos)
   
@app.route('/', methods=['POST'])
def post():
   if not current_app.session:
      session = requests.Session()
      current_app.inject_session(session)
   if not current_app.repos:
      current_app.reload_config()
      
   data = json.loads(request.data)
   
   datas = {'hello': 'world', 'number': 3}
   js = json.dumps(datas)
   
   if request.headers['Content-Type'] != 'application/json':
      resp = Response(js, status=200, mimetype='application/json')
      return resp
        
   signature = 'sha1=' + hmac.new(bytes(current_app.secret, encoding="UTF-8"), request.data, hashlib.sha1).hexdigest()
   if not 'X-Hub-Signature' in request.headers or signature != request.headers['X-Hub-Signature']:
      resp = Response(js, status=401, mimetype='application/json')
      return resp
      
   if request.headers['X-GitHub-Event'] != 'ping' and request.headers['X-GitHub-Event'] != 'label':
      resp = Response(js, status=200, mimetype='application/json')
      return resp   
   
   
   
   if request.headers['X-GitHub-Event'] == 'ping':
      resp = Response(js, status=200, mimetype='application/json')
      return resp       
   
   else:
      if data['action'] == 'created':
         if data['repository']['full_name'] not in current_app.repos: 
            resp = Response(js, status=400, mimetype='application/json')
            return resp 
         for repo in current_app.repos: 
            if repo != data['repository']['full_name']:
               colors = json.dumps({"name": data['label']['name'], "color": data['label']['color']})
               list = current_app.session.post('https://api.github.com/repos/' + repo + '/labels', data=colors)
      
      elif data['action'] == 'deleted':
         if data['repository']['full_name'] not in current_app.repos: 
            resp = Response(js, status=400, mimetype='application/json')
            return resp 
         for repo in current_app.repos:
            if repo != data['repository']['full_name'] and current_app.dname != data['label']['name']:
               list = current_app.session.delete('https://api.github.com/repos/' + repo + '/labels/' + data['label']['name'])
         # TODO
         current_app.dname = data['label']['name']
      
      elif data['action'] == 'edited':  
         if data['repository']['full_name'] not in current_app.repos: 
            resp = Response(js, status=400, mimetype='application/json')
            return resp 
         for repo in current_app.repos:
            if 'name' not in data['changes'] or 'from' not in data['changes']['name']:
               colorname = data['label']['name']    
            else: colorname = data['changes']['name']['from']   
            if repo != data['repository']['full_name'] and current_app.ename != data['label']['name']:
               colors = json.dumps({"name": data['label']['name'], "color": data['label']['color']})
               list = current_app.session.patch('https://api.github.com/repos/' + repo + '/labels/' + colorname, data=colors)
         # TODO
         current_app.ename = data['label']['name']
         
      resp = Response(js, status=200, content_type='application/json', mimetype='application/json')
      resp.headers['Link'] = 'https://api.github.com/'
       
      return resp

@cli.command()
@click.option('-h', '--host', default='127.0.0.1', help='Host address')
@click.option('-p', '--port', default='5000', help='Port')
@click.option('-d', '--debug', is_flag=True, envvar='FLASK_DEBUG', help='Debug mode')
@click.pass_context
def run_server(ctx, host, port, debug):
    """Run a server with Flask app"""
    # TODO: implement the command for starting web app (use app.run)
    # Don't forget to app the session from context to app
    config = ctx.obj['config']
    if config is not None and os.path.isfile(config) == True:
      os.environ['LABELORD_CONFIG'] = config
      app.reload_config()
     
    #current_app.session = ctx.obj['session']
    app.run(debug=debug, host=host, port=int(port))


# ENDING  NEW FLASK SKELETON
#####################################################################

if __name__ == '__main__':
    cli(obj={})