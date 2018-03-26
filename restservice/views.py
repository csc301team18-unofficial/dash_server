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


def log_food(request, client_id):
    if request.method == 'POST':
        get_or_create_user(client_id)

        """
        - Get food info using get_food()
        - Get serving size to scale values by (either from request args or from user)
        - Scale food macro values by serving size
        - Add a new FoodEntry, and link to a new DailyFood Entry
        - Add points if the user is still within their macro goals
        - Return a 200_OK response if everything works out, and return a 500_ISE response if anything breaks
        """
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def log_water(request, client_id):
    if request.method == 'POST':
        pass
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def water_goals(request, client_id):
    if request.method == 'GET':
        # TODO: Return how much water the user has had in the last 24 hours
        pass
    elif request.method == 'POST':
        # TODO: Log some water
        pass
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def macros(request, client_id):
    if request.method == 'GET':
        # TODO: Return what the user's current macros are
        pass
    elif request.method == 'POST':
        # TODO: Update the user's current macros
        pass
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def food_info(request, client_id, food_name):
    """
    Handles GET FoodInfo requests. Returns a JSON representation of the Food Class,
    using NutriHandler.py
    :param request: HTTP request
    :param client_id: The client's unique ID
    :param food_name: The name of the food the client is searching for
    :return:
    """
    # if user is not in database yet, add user to database
    if request.method == 'GET':
        get_or_create_user(client_id)

        nh = NutriHandler()

        try:
            food_cache_obj = nh.get_food(food_name)
            food_cache_serializer = FoodCacheSerializer(food_cache_obj)
            return JSONResponse(food_cache_serializer.data, status=status.HTTP_200_OK)

        except RuntimeError:
            # This happens if the Nutritics API call in get_food() fails
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def get_points(request, client_id):
    """
    Handles GET points requests. Returns a JSON representation of the user's score.
    :param request: HTTP request
    :param client_id: Client's unique ID
    :return: HttpResponse with status 400 or 500 if request was not sucessful,
    and a JSONResponse containing an int otherwise
    """
    # if user is not in database yet, add user to database
    if request.method == 'GET':
        user_obj = get_or_create_user(client_id)

        # parse JSON object to return a JSON object with just the "points"
        # gets serialized user from database
        user_serializer = UserSerializer(user_obj)

        # create new dict with just points data
        data = {"points" : user_serializer.data["score"]}

        return JSONResponse(data, status=status.HTTP_200_OK)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



# *********************************
#   Helper functions
# *********************************
def get_or_create_user(client_id):
    """
    TODO: THIS FUNCTION HAS TO BE CALLED AT THE BEGINNING OF EVERY REQUEST-HANDLING FUNCTION IN THIS CLASS
    TODO: THERE ARE NO EXCEPTIONS TO THIS, OR IT'LL BREAK EVERYTHING
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
