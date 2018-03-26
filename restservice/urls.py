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
    # GET Request URLs
    url(r'^foodinfo/(?P<client_id>.+?)/food_name=(?P<food_name>.+?)/$', views.get_food_info),
    url(r'^points/(?P<client_id>.+?)/$', views.get_points), # GET points
    url(r'^watergoals/(?P<client_id>.+?)/.*?$', views.get_post_water_goals), # GET water goals
    url(r'^macros/(?P<client_id>.+?)/.*?$', views.get_post_macros), # GET current macros
    url(r'^macros/(?P<client_id>.+?)/.*?$', views.get_post_water) # GET current water

    # POST Request URLs

]
