from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from restservice.models import *

from nutrition import nutrihandler as nh
import monsterurl as namegen


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def food_info(request, client_id, food_name):
    """
    Handles GET FoodInfo requests. Returns a JSON representation of the Food Class,
    using NutriHandler.py
    :param request: The request that's received
    :param client_id: The client's unique ID
    :param food_name:
    :return:
    """
    if request.method == 'GET':
        try:
            user_entry = Users.objects.get(user_id=client_id)
        except ObjectDoesNotExist:
            # TODO: Create a new user entry
            user_entry = create_new_user(client_id)

        serving_size = getattr(user_entry, 'serving_size')

        # TODO: THIS ENTIRE THING


    else:
        # TODO: Return a "bad request" error response
        pass


# *********************************
#   Helper functions
# *********************************
def create_new_user(client_id):
    """
    Creates a new user account.
    :param client_id: Unique client ID sent by DialogFlow. Client ID's are tied to Google accounts.
    :return:
    """
    new_user = Users(
        user_id=client_id,
        name=namegen.get_monster(),
        serving_size=100,
        streak=0,
        score=0
    )
    new_user.save()
    return new_user
