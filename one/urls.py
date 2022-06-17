from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home',views.home,name='home'),  
    path('login',views.login,name='login') ,
    path('register',views.register,name='register'),
    path('subjects',views.subjects,name='subjects'),  
    path('timetable',views.timetable,name='timetable'),
    path('semester',views.semester,name='semester'), 
    path('viewtable',views.viewtable,name='viewtable'),
    path('currsem',views.currsem,name='currsem'),
    path('homepage',views.homepage,name='homepage'),
    path('viewsubjetcs',views.viewsubjects,name='viewsubjetcs'),  
    path('subjectspage',views.subjectspage,name='subjectspage'), 
    path('contact',views.contact,name='contact'),   
    path('delsem',views.delsem,name='delsem'), 

]
