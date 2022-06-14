from ast import excepthandler
from distutils.archive_util import make_archive
from distutils.command.config import config
from email import message
import imp
from json import load, loads
from multiprocessing import context
from re import template
import re
from unicodedata import name
from xml.sax.handler import DTDHandler
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect,render
from django.template import loader 
import pyrebase
from requests import request 
from django.contrib import messages

config = {
    "apiKey": "AIzaSyC_in9XEWPIeEcE7EwcDf8I3zocSCrFvPQ",
    "authDomain": "database-2749d.firebaseapp.com",
    "databaseURL": "https://database-2749d-default-rtdb.firebaseio.com",
    "projectId": "database-2749d",
    "storageBucket": "database-2749d.appspot.com",
    "messagingSenderId": "798947227480",
    "appId": "1:798947227480:web:f4251a29b4074dd9f0972d"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database() 

mailid = ''
mail = '' 
psd = '' 
sem = ''
uname = ''
sub = [] 


def login(request):
    if request.method == 'POST': 
        user = request.POST['user']
        password = request.POST['password']
        usr = list(user.split('.')) 
        usr = ''.join(usr)  
        print(usr,password) 
        mail_id = database.child(usr).child('login').child('email').get().val()
        mail_password = database.child(usr).child('login').child('password').get().val() 
        print(mail_id,mail_password) 
        if  mail_id == user:
            if mail_password == password:
                context = {
                    'sudeep' : [user,password] 
                } 
                global mail
                mail = usr 
                global psd
                psd = password
                template = loader.get_template('home.html')   
                return HttpResponse(template.render(context,request))
            else:
                messages.info(request,'Invalid password') 
                return render(request,'login.html') 
        else:
            messages.info(request,'User not found')
            return render(request,'login.html') 



def home(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render()) 

def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        user = request.POST['user'] 
        password = request.POST['password']
        usr = list(user.split('.')) 
        usr = ''.join(usr)
        global mailid
        mailid = user 
        email = database.child(usr).child('login').child('email').get().val()
        if email != user:
            global mail 
            mail = usr 
            global psd
            psd = password 
            global uname
            uname = name
            template = loader.get_template('subjects.html')
            return HttpResponse(template.render()) 
        else: 
            msg  = {
            'msg' : 'User already exists'
            }
            return render(request,'register.html',msg) 
    else:
        msg  = {
            'msg' : 'User already exists'
        }
        return render(request,'register.html',msg) 

def subjects(request):
    if request.method == 'POST': 
        subjects = request.POST['subjects'] 
        semester = request.POST['semester']
        global sem 
        sem = semester
        if len(subjects) != 0 and semester != '':
            subjects = list(subjects.split(','))
            subjects.pop() 
            global sub 
            sub = {'sub':subjects,'sem':semester}
            sub['sub'].append('No period')  
            global mail,mailid 
            usr = list(mail.split('.')) 
            usr = ''.join(usr)
            data = {'email':mailid,'password':psd,'username':uname ,'semester':semester} 
            database.child(usr).child('login').set(data)
            data = {'attend':0,'total':0} 
            for i in range(len(subjects)): 
                if subjects[i] != 'No period':
                    database.child(mail).child('semester').child(semester).child('subjects').child(subjects[i]).set(data)
            database.child(mail).child('semester').child(semester).child('subjects').child('total').set(data)  
        return render(request,'timetable.html',sub) 

def showdashboard(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    subjects = dict(database.child(mail).child('semester').child(semester).get().val()) 
    sub = {'show':subjects['subjects'],'sem':semester}  
    template = loader.get_template('showdashboard.html')      
    return HttpResponse(template.render(sub,request))      

def shownotification(reuqest):
    template = loader.get_template('shownotification.html')
    return HttpResponse(template.render()) 
def timetable(request):
    if request.method == 'POST': 
        data  = []
        name = ['m','tu','w','th','f','s']
        for i in range(6): 
            temp = [] 
            for j in range(7):
                p = str(name[i] + str(j+1))
                temp.append(request.POST[p]) 
            data.append(temp)
        for i in data:
            print(i) 
        day = ['monday','tuesday','wednesday','thrusday','friday','saturday']
        time = {'9-10':0,'10-11':0,'11-12':0,'1-2':0,'2-3':0,'3-4':0,'4-5':0} 
        print('semster -> ',sem) 
        for i in range(len(data)):
            j = 0
            for k,v in time.items():
                time[k] = data[i][j] 
                j += 1   
            database.child(mail).child('semester').child(sem).child('timetable').child(day[i]).set(time) 
        return render(request,'home.html') 
def viewtable(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    timetable = dict(database.child(mail).child('semester').child(semester).child('timetable').get().val()) 
    print(timetable) 
    day = ['monday','tuesday','wednesday','thrusday','friday','saturday']
    time = ['9-10','10-11','11-12','1-2','2-3','3-4','4-5'] 
    data = {}
    for i in range(6):
        temp = [] 
        for j in range(7):
            temp.append(timetable[day[i]][time[j]]) 
        data.update({day[i]:temp}) 
        i += 1 
    data = {'show':data,'sem':semester} 
    return render(request,'viewtable.html',data)   

