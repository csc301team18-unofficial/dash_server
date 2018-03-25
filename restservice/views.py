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
def logFood(request, client_id):
    if request.method == 'GET':
        get_or_create_user(client_id)
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
        user = get_or_create_user(client_id)

        try:
            points_serializer = UserScoreSerializer(user.score)
            # TO DO: create JSON object from the points variable (only 1 field)
            return JSONResponse(points_serializer.data, status=status.HTTP_200_OK)
        except RuntimeError:
            # should never reach this block because users that don't exist
            # are added to the database
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


# def get_ranking(request, client_id):
#     """
#     Handles GET ranking requests. Returns a JSON representation of the User Class.
#     :param request:
#     :param client_id:
#     :return: HttpResponse with status 400 or 500 if request was not sucessful,
#     and a JSONResponse containing an int otherwise
#     """
#     # if user is not in database yet, add user to database
#     if request.method == 'GET':
#         user = get_or_create_user(client_id)
#
#         try:
#             points_serializer = UserScoreSerializer(user.score)
#             # TO DO: create JSON object from the points variable (only 1 field)
#             return JSONResponse(points_serializer.data, status=status.HTTP_200_OK)
#         except RuntimeError:
#             # should never reach this block because users that don't exist
#             # are added to the database
#             return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     else:
#         return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


# @csrf_exempt
# def log_food(request, client_id, food_name, serving_size):
#     """
#     Handles GET FoodInfo requests. Returns a JSON representation of the Food Class,
#     using NutriHandler.py
#     :param request: The request that's received
#     :param client_id: The client's unique ID
#     :param food_name:
#     :return:
#     """
#
#     if request.method == 'POST':
#         user_entry = get_or_create_user(client_id)
#         # TO DO:
#         # - log_food == post request (client, food, serving size(optional))
#         # - make row with food_name and nutritics response in DailyFood table
#         # - send back HTTP200 response (good) or HTTP500 (bad)
#         # write new DailyFood deserializer (json to models)
#
#     else:
#         return JSONResponse(status=status.HTTP_400_BAD_REQUEST)

#@csrf_exempt
#def water_comms(request, client_id)

#@csrf_exempt
#def water(request, client_id,)


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
