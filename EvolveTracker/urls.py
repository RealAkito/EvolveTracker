"""EvolveTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout
from EvolveTracker.apps.bugs import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_logout, {'next_page': '/'}, name='logout'),
    # rest of our views
    url(r'^$', views.index),
    # The user can go to the ticket via the database id
    path('ticket/<int:id>', views.ticketid),
    # or the ticket id.
    path('ticket/<str:uuid>', views.ticketuuid),
]
