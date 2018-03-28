from django.shortcuts import render

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from restservice.serializers import *
from django.views.decorators.csrf import csrf_exempt

from rest_framework.parsers import JSONParser

from utility.utils import get_food, md5_hash_string
import monsterurl


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def username(request, client_id):
    if request.method == 'POST':
        user_obj = get_or_create_user_and_goals(client_id)[0]

        response = {"username": user_obj.name}
        return JSONResponse(response, status=status.HTTP_200_OK)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_food_entry(request, client_id):
    """
    Gets a JSON object from the client defining the food's name, and optionally the serving size used.
    Logs the food using the specified serving size, or the default serving size
    """
    if request.method == 'POST':
        user_obj, user_goals = get_or_create_user_and_goals(client_id)


    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def log_meal_entry(request, client_id):

    if request.method == 'POST':
        # TODO: Parse JSON for meal name
        user_obj, user_goals = get_or_create_user_and_goals(client_id)

        mb = utils.MealBuilder(user_obj)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
def water(request, client_id):
    """
    Get the quantity of water consumed today or
    Log some amount of water
    """
    if request.method == 'GET':
        pass
        # SYNTAX FOR LOOKUP OF WATER INFORMATION FOR A USER:
        # from DailyFood get all entries where user_id=client_id &&
        # food_entry_id=(food entries with food_name=water)
        data = ""
        return JSONResponse(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        pass

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def goals(request, client_id):
    if request.method == 'GET':
        user, user_goals = get_or_create_user_and_goals(client_id)
        goals_serializer = GoalsSerializer(user_goals)
        return JSONResponse(goals_serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        parser = JSONParser()
        raw_goal_data = parser.parse(request)
        print(raw_goal_data)

        parsed_goal_data = dict()

        for goal_param in utilconstants.GOAL_PARAM_NAMES:
            try:
                param = raw_goal_data[goal_param]
                parsed_goal_data[goal_param] = param
                setattr(user_goals, goal_param, param)
            except KeyError:
                parsed_goal_data[goal_param] = None

        user_goals.save()

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def points(request, client_id):
    # TODO: every DailyFood call should also award points to/penalize users

    """
    Handles GET points requests. Returns a JSON representation of the user's score.
    :param request: HTTP request
    :param client_id: Client's unique ID
    :return: HttpResponse with status 400 or 500 if request was not sucessful,
    and a JSONResponse containing an int otherwise
    """
    # if user is not in database yet, add user to database
    if request.method == 'GET':
        user_obj = get_or_create_user_and_goals(client_id)[0]

        # parse JSON object to return a JSON object with just the "points"
        # gets serialized user from database
        user_serializer = UserSerializer(user_obj)

        # create new dict with just points data
        data = {"points": user_serializer.data["score"]}

        return JSONResponse(data, status=status.HTTP_200_OK)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def food_info(request, client_id, food_name):
    """
    Handles GET FoodInfo requests. Returns a JSON representation of the FoodCache, using utils.py
    :param request: HTTP request
    :param client_id: The client's unique ID
    :param food_name: The name of the food the client is searching for
    :return:
    """
    # if user is not in database yet, add user to database
    if request.method == 'GET':
        get_or_create_user_and_goals(client_id)

        try:
            food_cache_obj = get_food(food_name)
            food_cache_serializer = FoodCacheSerializer(food_cache_obj)
            return JSONResponse(food_cache_serializer.data, status=status.HTTP_200_OK)

        except RuntimeError:
            # This happens if the Nutritics API call in get_food() fails
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


# *********************************
#   Helper functions
# *********************************
def get_or_create_user_and_goals(client_id):
    """
    TODO: THIS FUNCTION HAS TO BE CALLED AT THE BEGINNING OF EVERY REQUEST-HANDLING FUNCTION IN THIS CLASS
    TODO: THERE ARE NO EXCEPTIONS TO THIS, OR IT'LL BREAK EVERYTHING
    Checks if the client already has a registered account, or if one needs to be made.
    Gets the account if it already exists, or makes a new one if it doesn't.
    """
    try:
        user_entry = Users.objects.get(user_id=client_id)
    except ObjectDoesNotExist:
        user_entry = Users.objects.create(
                user_id=client_id,
                name=monsterurl.get_monster(),
                serving_size=100,
                streak=0,
                score=0
            )

    try:
        goal_entry = Goals.objects.get(user_id=client_id)
    except ObjectDoesNotExist:
        goal_entry = Goals.objects.create(
                goal_id=md5_hash_string(client_id),
                user_id=user_entry,
                water_ml=3500,
                protein_grams=50,
                fat_grams=70,
                carb_grams=310,
                kilocalories=2070
        )

    return user_entry, goal_entry


def calculate_points(user):
    """
    This function calculates points to award or deduct from the user.
    The closer the user gets to their goals, the more points they're awarded.
    However, if they move past any of their targets, they should be penalised.
    :param user: The user who's points should be calculated
    """
    pass