from django.conf.urls import url
from webinterface import views

urlpatterns = [
    url(r'^(?P<client_name>.+?)/$', views.insights, name='insights')
]
