"""dashserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from restservice import views

urlpatterns = [
    url(r'^foodinfo/(?P<client_id>.+?)/(?P<food_name>.+?)/$', views.food_info),  # GET info about a certain food
    url(r'^points/(?P<client_id>.+?)/$', views.points),  # GET points
    url(r'^water/(?P<client_id>.+?)/$', views.log_water),  # POST water consumption
    url(r'^goals/(?P<client_id>.+?)/$', views.goals),  # GET or PUT current macros
    url(r'^username/(?P<client_id>.+?)/$', views.username),  # GET username
    url(r'^create_meal/(?P<client_id>.+?)/$', views.create_meal),  # POST create a meal
    url(r'^log_meal/(?P<client_id>.+?)/$', views.log_meal),  # POST log a meal
    url(r'^log_food/(?P<client_id>.+?)/$', views.log_food),  # POST log a food
    url(r'^points/(?P<client_id>.+?)/$', views.points),  # GET points
    url(r'^today/(?P<client_id>.+?)/$', views.today_info),  # GET info about today's consumption

]
