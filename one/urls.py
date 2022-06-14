from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home',views.home,name='home'),  
    path('login',views.login,name='login') ,
    path('register',views.register,name='register'),
    path('subjects',views.subjects,name='subjects'), 
    path('showdashboard',views.showdashboard,name='showdashboard'), 
    path('shownotification',views.shownotification,name='shownotification'), 
    path('timetable',views.timetable,name='timetable'),
    path('viewtable',views.viewtable,name='viewtable'),

]
