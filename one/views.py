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
        global uname,psd,mail,mail_id,sem,psd
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
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    data = {} 
    for k,v in subjects['subjects'].items():
        d1 = {}
        for k1,v1 in v.items():
            # if k1 != 'percentage':
            d1.update({k1:v1}) 
        data.update({k:d1}) 
    
    result = list(data.keys()) 
    result.remove('total') 
    attended_periods = 0
    total_periods = 0 
    for i in range(len(result)):  
        x = database.child(mail).child('semester').child(semester).child('subjects').child(result[i]).child('attend').get().val() 
        y = database.child(mail).child('semester').child(semester).child('subjects').child(result[i]).child('total').get().val() 
        attended_periods += int(x)
        total_periods += int(y) 
    z = round( (float(attended_periods) / float(total_periods))*100.0 ,2 ) 
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('attend').set(attended_periods)  
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('total').set(total_periods)  
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('percentage').set(z)  


    if int(streak) > 0:
        sub = {'show':data,'sem':semester,'streak':streak,'cls':'cls'}  
    else:
        sub = {'show':data,'sem':semester,'streak':streak}   
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
        data = {'email':mail_id,'password':psd,'username':uname ,'semester':sem} 
        database.child(usr).child('login').set(data) 
        subjects = sub['sub'] 
        data = {'attend':0,'total':0,'percentage':0} 
        data1 = {'streak':0,'update_timetable':0}  
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
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    if int(streak) > 0:
        data = {'show':data,'sem':semester,'usr':uname,'streak':streak,'cls':'cls'}
    else:
        data = {'show':data,'sem':semester,'usr':uname,'streak':streak} 
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
    global uname,sem 
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val()
    if int(streak) > 0:
        data = {'usr':uname,'sem':semester,'streak':streak,'cls':'cls'}    
    else:
        data = {'usr':uname,'sem':semester,'streak':streak}   
    template = loader.get_template('currsem.html') 
    return HttpResponse(template.render(data,request)) 


def homepage(request):
    semester = database.child(mail).child('login').child('semester').get().val()
    data = {'sem':semester,'usr':uname} 
    return render(request,'home.html',data)

def subjectspage(request):
    return render(request,'subjects.html')  

def add_sem_subjects(request):
    return render(request,'add_sem_subjects.html') 

def add_subjects(request): 
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
            return render(request,'add_sem_timetable.html',sub) 
        else:
            data = {'msg':['Semester already exist']} 
            return render(request,'add_sem_subjects.html',data)   

def add_sem_timetable(request):
    if request.method == 'POST': 
        global sem,sub  
        subjects = sub['sub'] 
        data = {'attend':0,'total':0,'percentage':0} 
        data1 = {'streak':0,'update_timetable':0}  
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
    tasks = database.child(mail).child('todo').get().val()
    if tasks == None:
        data = {'tasks':[],'usr':uname,'t':6}  
    else:
        tasks = dict(tasks) 
        d = list(tasks.values())  
        d = 6 - len(d)
        data = {'tasks':tasks.values(),'usr':uname,'t':d} 
    return render(request,'todo.html',data)  

def todosubmit(request):
    temp = 'task'
    task_list = request.POST['taskslist']  
    task_list = task_list.split(',')
    task_list.pop() 
    t = {}  
    for i in range(len(task_list)):
        if task_list[i][-1] == '*':
            t.update({temp+str(i) : task_list[i][0:len(task_list[i])-1]}) 
        else:
            t.update({temp + str(i) : task_list[i]})  
    database.child(mail).child('todo').set(t) 
    tasks = database.child(mail).child('todo').get().val()
    if tasks == None:
        data = {'tasks':[],'usr':uname,'t':6}  
    else:
        tasks = dict(tasks) 
        d = list(tasks.values())  
        d = 6 - len(d)
        data = {'tasks':tasks.values(),'usr':uname,'t':d} 
    return render(request,'todo.html',data)  

def profilepage(request):
    sem = database.child(mail).child('semester').get().val() 
    if sem == None:
        sem = 0     
        data = {'usr':uname,'mail':mail_id,'password':psd,'sem':'Semester registered : '+str(sem)}
    else:
        sem = dict(sem) 
        sem = list(sem.keys())
        sem = len(sem) 
        data = {'usr':uname,'mail':mail_id,'password':psd,'sem':'Semester registered : '+str(sem)} 
    return render(request,'profilepage.html',data) 

def newpassword(request): 
    p = request.POST['newpassword']  
    details = dict(database.child(mail).child('login').get().val()) 
    details['password'] = p 
    global psd
    psd = p  
    database.child(mail).child('login').set(details) 
    sem = database.child(mail).child('semester').get().val() 
    if sem == None:
        sem = 0     
        data = {'usr':uname,'mail':mail_id,'password':psd,'sem':'Semester registered : '+str(sem)}
    else:
        sem = dict(sem) 
        sem = list(sem.keys())
        sem = len(sem) 
        data = {'usr':uname,'mail':mail_id,'password':psd,'sem':'Semester registered : '+str(sem)} 
    return render(request,'profilepage.html',data) 

def update_timetable(request):
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
    global uname,sub
    sem = database.child(mail).child('login').child('semester').get().val()
    semester = sem 
    sub = dict(database.child(mail).child('semester').child(sem).child('subjects').get().val())
    sub = list(sub.keys()) 
    sub.remove('total') 
    for i in range(len(sub)):
        sub[i] += '*'
    sub.append('No period') 
    m1 = data['monday'][0] 
    m2 = data['monday'][1] 
    m3 = data['monday'][2] 
    m4 = data['monday'][3] 
    m5 = data['monday'][4] 
    m6 = data['monday'][5] 
    m7 = data['monday'][6]  

    tu1 = data['tuesday'][0] 
    tu2 = data['tuesday'][1] 
    tu3 = data['tuesday'][2] 
    tu4 = data['tuesday'][3] 
    tu5 = data['tuesday'][4] 
    tu6 = data['tuesday'][5] 
    tu7 = data['tuesday'][6]    

    w1 = data['wednesday'][0] 
    w2 = data['wednesday'][1] 
    w3 = data['wednesday'][2] 
    w4 = data['wednesday'][3] 
    w5 = data['wednesday'][4] 
    w6 = data['wednesday'][5] 
    w7 = data['wednesday'][6]    

    th1 = data['thrusday'][0] 
    th2 = data['thrusday'][1] 
    th3 = data['thrusday'][2] 
    th4 = data['thrusday'][3] 
    th5 = data['thrusday'][4] 
    th6 = data['thrusday'][5] 
    th7 = data['thrusday'][6] 

    f1 = data['friday'][0] 
    f2 = data['friday'][1] 
    f3 = data['friday'][2] 
    f4 = data['friday'][3] 
    f5 = data['friday'][4] 
    f6 = data['friday'][5] 
    f7 = data['friday'][6] 

    s1 = data['saturday'][0] 
    s2 = data['saturday'][1] 
    s3 = data['saturday'][2] 
    s4 = data['saturday'][3] 
    s5 = data['saturday'][4] 
    s6 = data['saturday'][5] 
    s7 = data['saturday'][6]    
    data = {
        'show':data,'sem':semester,'usr':uname,'sub':sub,'sem':semester,
        'm1':m1,'m2':m2,'m3':m3,'m4':m4,'m5':m5,'m6':m6,'m7':m7,
        'tu1':tu1,'tu2':tu2,'tu3':tu3,'tu4':tu4,'tu5':tu5,'tu6':tu6,'tu7':tu7,
        'w1':w1,'w2':w2,'w3':w3,'w4':w4,'w5':w5,'w6':w6,'w7':w7, 
        'th1':th1,'th2':th2,'th3':th3,'th4':th4,'th5':th5,'th6':th6,'th7':th7,
        'f1':f1,'f2':f2,'f3':f3,'f4':f4,'f5':f5,'f6':f6,'f7':f7, 
        's1':s1,'s2':s2,'s3':s3,'s4':s4,'s5':s5,'s6':s6,'s7':s7          
    }   
    return render(request,'update_timetable.html',data)   

def update_timetable_subjects(request):
    m = request.POST['monday']
    tu = request.POST['tuesday']
    w = request.POST['wednesday']
    th = request.POST['thrusday']
    f = request.POST['friday']
    s = request.POST['saturday']
    m = list(m.split(','))
    tu = list(tu.split(','))
    w = list(w.split(','))
    th = list(th.split(','))
    f = list(f.split(','))
    s = list(s.split(','))
    time = ['9-10','10-11','11-12','1-2','2-3','3-4','4-5']  

    semester = database.child(mail).child('login').child('semester').get().val()

    print('monday    -->',m)
    print('tuesday   -->',tu)
    print('wednesday -->',w)
    print('thrusday  -->',th)
    print('friday    -->',f)
    print('saturday  -->',s)   
    if len(m) != 0:
        for i in range(len(m)):
            if m[i] != '':
                if m[i] == 'No period':
                    d = m[i] 
                else:
                    d = m[i][0:len(m[i])-1]  
                database.child(mail).child('semester').child(semester).child('timetable').child('monday').child(time[i]).set(d) 

    if len(tu) != 0:
        for i in range(len(tu)):
            if tu[i] != '':
                if tu[i] == 'No period':
                    d = tu[i] 
                else:
                    d = tu[i][0:len(tu[i])-1] 
                database.child(mail).child('semester').child(semester).child('timetable').child('tuesday').child(time[i]).set(d) 
    
    if len(w) != 0:
        for i in range(len(w)):
            if w[i] != '': 
                if w[i] == 'No period':
                    d = w[i] 
                else:
                    d = w[i][0:len(w[i])-1] 
                database.child(mail).child('semester').child(semester).child('timetable').child('wednesday').child(time[i]).set(d) 

    if len(th) != 0:
        for i in range(len(th)):
            if th[i] != '': 
                if th[i] == 'No period':
                    d = th[i] 
                else:
                    d = th[i][0:len(th[i])-1] 
                database.child(mail).child('semester').child(semester).child('timetable').child('thrusday').child(time[i]).set(d) 
    
    if len(f) != 0:
        for i in range(len(f)):
            if f[i] != '': 
                if f[i] == 'No period':
                    d = f[i] 
                else:
                    d = f[i][0:len(f[i])-1] 
                database.child(mail).child('semester').child(semester).child('timetable').child('friday').child(time[i]).set(d)

    if len(s) != 0:
        for i in range(len(s)):
            if s[i] != '':  
                if s[i] == 'No period':
                    d = s[i] 
                else:
                    d = s[i][0:len(s[i])-1]  
                database.child(mail).child('semester').child(semester).child('timetable').child('saturday').child(time[i]).set(d)  

    

    
    
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
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    if int(streak) > 0:
        data = {'show':data,'sem':semester,'usr':uname,'streak':streak,'cls':'cls'}  
    else:
        data = {'show':data,'sem':semester,'usr':uname,'streak':streak} 
    return render(request,'viewtable.html',data)  

def update_subjects(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    subjects = dict(database.child(mail).child('semester').child(semester).get().val()) 
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    data = {} 
    for k,v in subjects['subjects'].items():
        d1 = {}
        for k1,v1 in v.items():
            if k1 != 'percentage':
                d1.update({k1:v1})
        data.update({k:d1})
    if int(streak) > 0:
        sub = {'show':data,'sem':semester,'streak':streak,'cls':'cls'} 
    else:
        sub = {'show':data,'sem':semester,'streak':streak}   
    return render(request,'update_subjects.html',sub) 

def update_sem_subjects(request):
    semester = database.child(mail).child('login').child('semester').get().val() 
    subjects = dict(database.child(mail).child('semester').child(semester).get().val()) 
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    data = {} 
    for k,v in subjects['subjects'].items():
        d1 = {}
        for k1,v1 in v.items():
            if k1 != 'percentage':
                d1.update({k1:v1})
        data.update({k:d1})
    
    result = list(data.keys()) 
    result.remove('total') 
    attended_periods = 0
    total_periods = 0 
    for i in range(len(result)):
        x = result[i]+'_attend'
        y = result[i]+'_total'
        x = request.POST[x] 
        y = request.POST[y]
        x = int(x)
        y = int(y)  
        attended_periods += int(x)
        total_periods += int(y) 
        z = round((float(x) / float(y) )*100.0,2)  
        database.child(mail).child('semester').child(semester).child('subjects').child(result[i]).child('attend').set(x) 
        database.child(mail).child('semester').child(semester).child('subjects').child(result[i]).child('total').set(y)
        database.child(mail).child('semester').child(semester).child('subjects').child(result[i]).child('percentage').set(z)

    z = round( (float(attended_periods) / float(total_periods))*100.0 ,2 ) 
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('attend').set(attended_periods)  
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('total').set(total_periods)  
    database.child(mail).child('semester').child(semester).child('subjects').child('total').child('percentage').set(z)  

    semester = database.child(mail).child('login').child('semester').get().val() 
    subjects = dict(database.child(mail).child('semester').child(semester).get().val()) 
    streak = database.child(mail).child('semester').child(semester).child('streak').get().val() 
    data = {}  
    for k,v in subjects['subjects'].items():
        d1 = {}
        for k1,v1 in v.items():
            # if k1 != 'percentage':
            d1.update({k1:v1}) 
        data.update({k:d1})   
    
    if int(streak) > 0: 
        sub = {'show':data,'sem':semester,'streak':streak,'cls':'cls'} 
    else:
        sub = {'show':data,'sem':semester,'streak':streak}   
    return render(request,'viewsubjects.html',sub) 