from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from restservice.serializers import *
from utility.utils import *


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def username(request, client_id):
    """
    Get the user's monstrous name! Returns a single item JSON response.
    """
    if request.method == 'GET':
        user_obj = get_or_create_user_and_goals(client_id)[0]
        response = {"username": user_obj.name}

        return JSONResponse(response, status=status.HTTP_200_OK)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_food_entry(request, client_id):
    """
    TODO:
    Gets a JSON object from the client defining the food's name, and optionally the serving size used.
    Logs the food using the specified serving size, or the default serving size

    Update user's points.

    Example JSON request:
    {
        "food_name": "banana",
        "serving": 120
    }

    """
    if request.method == 'POST':
        user_obj, user_goals = get_or_create_user_and_goals(client_id)

        food_entry_json = JSONParser().parse(request)

        Entry.objects.create(
            user_id=client_id,
            name=monsterurl.get_monster(),
            serving_size=100,
            sprint=1,
            points=0
        )

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def log_meal_entry(request, client_id):
    """
    Log an existing meal (a meal exists if it is in the MealCache). If the meal does not exist, throws a 400 BAD REQUEST
    error (DialogFlow then tells the user they must create the meal before logging it).
    """
    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        meal_data = JSONParser().parse(request)
        if "meal_name" in meal_data:
            meal_name = meal_data["meal_name"]
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        meal = MealCache.objects.get(user_id=user.user_id).objects.get(meal_name=meal_name)
        new_entry = Entry.objects.create()
        # TODO: Complete this!
        pass

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def create_meal(request, client_id):
    """
    Create a meal and add it to the MealCache. A meal belongs to a specific user, and is associated with
    :param request:
    :param client_id:
    :return:
    """
    if request.method == 'POST':
        user, user_goals = get_or_create_user_and_goals(client_id)

        meal_data = JSONParser().parse(request)
        meal_name = meal_data["meal_name"]

        food_details = meal_data["food_details"]

        mb = utils.MealBuilder(meal_name, user)

        # Iterate through the food items in the JSON
        for food_title in utilconstants.FOOD_ENUM:

            if food_title in food_details:
                food = food_details[food_title]

                if "name" in food:
                    food_name = food["name"]
                else:
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

                if "serving" in food:
                    serving_size = food["serving"]
                else:
                    serving_size = user.serving_size

                mb.add_food(food_name, serving_size)

        try:
            mb.create_meal_record()
            return HttpResponse(status=status.HTTP_200_OK)

        # TODO: Figure out exactly which error is raised when two records try to have the same primary key
        except Exception:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)

    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def water(request, client_id):
    """
    TODO:
    Get the quantity of water consumed today
    or
    Log some amount of water
    Data about user's water intake is stored in DailyFood table.
    """
    if request.method == 'GET':
        user, user_goals = get_or_create_user_and_goals()
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
    """
    Get the user's current macro and water goals
    or
    Update the user's current macro and water goals
    """
    if request.method == 'GET':
        user, user_goals = get_or_create_user_and_goals(client_id)
        goals_serializer = GoalsSerializer(user_goals)
        return JSONResponse(goals_serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        user, user_goals = get_or_create_user_and_goals(client_id)
        raw_goal_data = JSONParser().parse(request)

        for goal_param in utilconstants.GOAL_PARAM_NAMES:
            if goal_param in raw_goal_data:
                param = raw_goal_data[goal_param]
                setattr(user_goals, goal_param, param)

        user_goals.save()

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def points(request, client_id):
    """
    Handles GET points requests. Returns a JSON representation of the user's score.
    :param request: HTTP request
    :param client_id: Client's unique ID
    :return: HttpResponse with status 400 if request was invalid or 500 if request was not sucessful,
    and a JSONResponse containing an int otherwise
    """
    # if user is not in database yet, add user to database
    if request.method == 'GET':
        user_obj = get_or_create_user_and_goals(client_id)[0]
        user_serializer = UserSerializer(user_obj)
        # create new dict with just points data
        data = {"points": user_serializer.data["points"]}

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
