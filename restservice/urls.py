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
    url(r'^foodinfo/(?P<client_id>.+?)/(?P<food_name>.+?)$', views.food_info),


    url(r'^points/(?P<client_id>.+?)/$', views.get_points),  # GET points
    url(r'^water/(?P<client_id>.+?)/.*?$', views.water),  # GET water goals
    url(r'^goals/(?P<client_id>.+?)/.*?$', views.goals),  # GET current macros

    # POST Request URLs


    # Testing URLs ~ Dash
    url(r'^goals/(?P<client_id>.+?)/.*?$', views.goals),

]
