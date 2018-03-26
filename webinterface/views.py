from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from restservice.serializers import *

from utility.utils import *


def serve_client(request, client_name):
    try:
        user_entry = Users.objects.get(name=client_name)
    except ObjectDoesNotExist:
        # TODO: this happens if the user doesn't have an account, give them an error page or something
        pass

    # TODO: Render the page for this user
    pass
