from django.shortcuts import render

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from restservice.serializers import *

from nutrition.nutrihandler import *
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
    :param food_name: The name of the food the client is searching for
    :return:
    """
    if request.method == 'GET':
        get_or_create_user(client_id)

        nh = NutriHandler()

        try:
            food_cache_obj = nh.get_food(food_name)
            food_cache_serializer = FoodCacheSerializer(food_cache_obj)

        except RuntimeError:
            # This happens if the Nutritics API call in get_food() fails
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(food_cache_serializer.data)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

#@csrf_exempt
#def water(request, client_id,)

# *********************************
#   Helper functions
# *********************************
def get_or_create_user(client_id):
    """
    Checks if the client already has a registered account, or if one needs to be made.
    Gets the account if it already exists, or makes a new one if it doesn't.
    """
    try:
        user_entry = Users.objects.get(user_id=client_id)
    except ObjectDoesNotExist:
        user_entry = create_new_user(client_id)

    return user_entry


def create_new_user(client_id):
    """
    TODO: THIS FUNCTION HAS TO BE CALLED AT THE BEGINNING OF EVERY REQUEST-HANDLING FUNCTION IN THIS CLASS
    TODO: THERE ARE NO EXCEPTIONS TO THIS, OR IT'LL BREAK EVERYTHING
    Creates a new user account.
    :param client_id: Unique client ID sent by DialogFlow. Client ID's are tied to Google accounts.
    :return:
    """
    # returns a tuple of (new_user, created)
    # and we select just the new_user object
    new_user = Users.objects.create(
        user_id=client_id,
        name=namegen.get_monster(),
        serving_size=100,
        streak=0,
        score=0
    )

    return new_user
