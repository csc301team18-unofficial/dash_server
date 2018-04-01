from django.shortcuts import render

from django.http import HttpResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from restservice.models import *

from utility.utils import *


def insights(request, client_name):

    try:
        # user_data = get_relevant_user_data(client_name)
        return render(request, "insights/insights.html", get_dummy_data_for_html())

    except ObjectDoesNotExist:
        # TODO: The user doesn't have an account, so render an error page telling them to use the app at least once
        # TODO: or something like that
        print("user account for {} does not exist".format(client_name))
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def get_dummy_data_for_html():
    """
    Return dummy dictionary to display on HTML.

    :param userid: User id
    :return: dict
    """
    user_dict = {
        'username': "Grievous",
        'streak': 29,
        'user_score': 101,
        'curr_user_carbs': 120,
        'user_carbs_goal': 200,
        'user_carbs_percentage': 60,
        'curr_user_protein': 150,
        'user_protein_goal': 200,
        'user_protein_percentage': 75,
        'curr_user_fat': 20,
        'user_fat_goal': 50,
        'user_fat_percentage': 40,
        'curr_user_cals': 1260,
        'user_cals_goal': 2050,
        'user_cals_percentage': 61,
        'breakfast_foods': ["Toast", "Eggs", "Banana"],
        'lunch_foods': ["Pizza", "Apple"],
        'dinner_foods': ["Pasta", "Broccoli"]
    }
    return user_dict
