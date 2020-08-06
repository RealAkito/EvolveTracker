from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from EvolveTracker.apps.bugs import views

urlpatterns = [
    # The user can go to the ticket via the database id
    path('<int:id>', views.ticketid, name='ticketid'),
    # or the ticket id.
    path('<str:uuid>', views.ticketuuid, name='ticketuuid'),
    # new ticket
    path('new/', views.newticket, name='newticket')
]