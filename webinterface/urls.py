from django.conf.urls import url
from webinterface import views

urlpatterns = [
<<<<<<< HEAD
    url(r'^(?P<client_name>.+?)/$', views.insights, name='insights')
	]
=======
    url(r'^(?P<client_name>.+?)/$', views.serve_client)
]
>>>>>>> c247437c9a9fb797f15bad5a00e43fa428c11f32
