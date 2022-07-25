from ast import excepthandler
from ctypes import POINTER
from ctypes.wintypes import PINT 
from dataclasses import dataclass
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
from django.http import HttpRequest, HttpResponse,HttpResponseRedirect
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

mail_id = ''
mail = ''
psd = ''
uname = ''
sem = '' 
sub = {} 


def login(request):
    if request.method == 'POST': 
        user = request.POST['user']
        password = request.POST['password']
        usr = list(user.split('.')) 
        usr = ''.join(usr)  
        usr_name = database.child(usr).child('login').child('username').get().val() 
        global uname,psd,mail,mail_id 
        uname = usr_name
        mail = usr 
        mail_id = database.child(usr).child('login').child('email').get().val()
        psd = database.child(usr).child('login').child('password').get().val() 
        if  mail_id == user:
            if psd == password:
                data = {'usr':usr_name,'url':'semester'}  
                template = loader.get_template('home.html')     
                return HttpResponse(template.render(data,request)) 
            else:
                data= {'msg':['Invalid password']} 
                return render(request,'login.html',data)  
        else: 
            data = {'msg':['User not found']} 
            return render(request,'login.html',data)  



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
        
        email = database.child(usr).child('login').child('email').get().val()
        if email != user:
            global uname,mail,mail_id,psd 
            uname = name 
            mail_id = user 
            mail = usr
            psd = password 
            template = loader.get_template('subjects.html')
            return HttpResponse(template.render()) 
        else: 
            data = {'error':['User already exists']} 
            return render(request,'register.html',data)  
    else:
        data = {'error':['User already exists']} 
        return render(request,'register.html',data)  

def subjects(request):
    if request.method == 'POST': 
        subjects = request.POST['subjects'] 
        semester = request.POST['semester']
        global sem,sub,mail_id
        sem = semester 
        SEM  = database.child(mail).child('semester').get().val()
        if SEM != None: 
            SEM = dict(SEM)   
            SEM = list(SEM.keys())  
        if SEM == None or sem not in SEM: 
            subjects = list(subjects.split(','))
            subjects.pop() 
            sub = {'sub':subjects,'sem':semester}
            sub['sub'].append('No period')  
            
            # global mail,mail_id 
            # usr = list(mail.split('.')) 
            # usr = ''.join(usr)
            # data = {'email':mail_id,'password':psd,'username':uname ,'semester':semester} 
            # database.child(usr).child('login').set(data)
            # data = {'attend':0,'total':0,'percentage':0} 
            # for i in range(len(subjects)): 
            #     if subjects[i] != 'No period':
            #         database.child(mail).child('semester').child(semester).child('subjects').child(subjects[i]).set(data)
            # database.child(mail).child('semester').child(semester).child('subjects').child('total').set(data)  
            return render(request,'timetable.html',sub) 
        else:
            data = {'msg':['Semester already exist']} 
            return render(request,'subjects.html',data)  

def viewsubjects(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    subjects = dict(database.child(mail).child('semester').child(semester).get().val()) 
    sub = {'show':subjects['subjects'],'sem':semester}  
    for k,v in sub['show'].items():
        print(k,'-->',v) 
    template = loader.get_template('viewsubjects.html')      
    return HttpResponse(template.render(sub,request))      

def shownotification(reuqest):
    template = loader.get_template('shownotification.html')
    return HttpResponse(template.render()) 
def timetable(request):
    if request.method == 'POST': 
        global mail,mail_id,sem,sub 
        usr = list(mail.split('.')) 
        usr = ''.join(usr)  
        data = {'todo':{'task1':'sudeep','task2' :'chinnu'}} 
        database.child(usr).set(data) 
        data = {'email':mail_id,'password':psd,'username':uname ,'semester':sem} 
        database.child(usr).child('login').set(data)
        subjects = sub['sub'] 
        data = {'attend':0,'total':0,'percentage':0} 
        data1 = {'streak':0} 
        database.child(mail).child('semester').child(sem).set(data1)  
        for i in range(len(subjects)): 
            if subjects[i] != 'No period':
                database.child(mail).child('semester').child(sem).child('subjects').child(subjects[i]).set(data)
        database.child(mail).child('semester').child(sem).child('subjects').child('total').set(data)  
        
        data  = []
        name = ['m','tu','w','th','f','s']
        for i in range(6): 
            temp = [] 
            for j in range(7):
                p = str(name[i] + str(j+1))
                temp.append(request.POST[p]) 
            data.append(temp)
        day = ['monday','tuesday','wednesday','thrusday','friday','saturday']
        time = {'9-10':0,'10-11':0,'11-12':0,'1-2':0,'2-3':0,'3-4':0,'4-5':0} 
        for i in range(len(data)):
            j = 0
            for k,v in time.items():
                time[k] = data[i][j] 
                j += 1   
            database.child(mail).child('semester').child(sem).child('timetable').child(day[i]).set(time) 
        data = {'usr':uname} 
        return render(request,'home.html',data)  


def viewtable(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    timetable = dict(database.child(mail).child('semester').child(semester).child('timetable').get().val()) 
    day = ['monday','tuesday','wednesday','thrusday','friday','saturday']
    time = ['9-10','10-11','11-12','1-2','2-3','3-4','4-5'] 
    data = {}
    for i in range(6):
        temp = [] 
        for j in range(7):
            temp.append(timetable[day[i]][time[j]]) 
        data.update({day[i]:temp}) 
        i += 1 
    global uname 
    data = {'show':data,'sem':semester,'usr':uname} 
    return render(request,'viewtable.html',data)   



def semester(request):
    global uname 
    if database.child(mail).child('semester').get().val() == None:
        data = {'usr':uname}
        return render(request,'semester.html',data)
    subs = dict(database.child(mail).child('semester').get().val()) 
    semester = database.child(mail).child('login').child('semester').get().val()
    subs = list(subs.keys()) 
    data = {'usr':uname,'sem':semester,'subs':subs} 
    template = loader.get_template('semester.html')
    return HttpResponse(template.render(data,request)) 

def currsem(request):
    semester = request.POST['sems']
    database.child(mail).child('login').child('semester').set(semester)  
    global uname
    data = {'usr':uname,'sem':semester}  
    template = loader.get_template('currsem.html') 
    return HttpResponse(template.render(data,request)) 


def homepage(request):
    semester = database.child(mail).child('login').child('semester').get().val()
    data = {'sem':semester,'usr':uname} 
    return render(request,'home.html',data)

def subjectspage(request):
    return render(request,'subjects.html')  

def contact(request):
    data = {'usr':uname}  
    template = loader.get_template('contact.html')
    return HttpResponse(template.render(data,request))  


def delsem(request):
    del_sem = request.POST['delsem'] 
    global mail
    global uname
    database.child(mail).child('semester').child(del_sem).remove() 
    if database.child(mail).child('semester').get().val() == None:
        semester = database.child(mail).child('login').child('semester').get().val()
        data = {'sem':semester,'usr':uname} 
        return render(request,'semester.html') 
    subs = dict(database.child(mail).child('semester').get().val()) 
    semester = database.child(mail).child('login').child('semester').get().val()
      
    subs = list(subs.keys()) 
    data = {'usr':uname,'sem':semester,'subs':subs} 
    template = loader.get_template('semester.html')
    return HttpResponse(template.render(data,request)) 

def todo(request):
    tasks = dict(database.child(mail).child('todo').get().val()) 
    data = {'tasks':tasks.values(),'usr':uname} 
    return render(request,'todo.html',data)  

def profilepage(request):
    data = {'usr':uname}
    return render(request,'profilepage.html',data)  