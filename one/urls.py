from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings 

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
    path('todo',views.todo,name='todo'), 
    path('profilepage',views.profilepage,name='profilepage'),
    path('todosubmit',views.todosubmit,name='todosubmit'),
    path('newpassword',views.newpassword,name='newpassword'),
    path('add_sem_subjects',views.add_sem_subjects,name='add_sem_subjects'), 
    path('add_sem_subjects',views.add_sem_subjects,name='add_sem_subjects'),  
    path('add_subjects',views.add_subjects,name='add_subjects'),  
    path('add_sem_timetable',views.add_sem_timetable,name='add_sem_timetable'),  


]

urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT) 
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)   