from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from restservice.serializers import *

from utility.utils import *


<<<<<<< HEAD
def insights(request, client_name):
=======
def serve_client(request, client_name):
>>>>>>> c247437c9a9fb797f15bad5a00e43fa428c11f32
    try:
        user_entry = Users.objects.get(name=client_name)
    except ObjectDoesNotExist:
        # TODO: this happens if the user doesn't have an account, give them an error page or something
        pass

<<<<<<< HEAD
    return render(request, 'webinterface/templates/insights/insights.html')
=======
    # TODO: Render the page for this user
    pass
>>>>>>> c247437c9a9fb797f15bad5a00e43fa428c11f32
