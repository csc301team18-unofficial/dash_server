import requests
from nutrition import nutriconstants as nc


class Meal:
    """
    Container / utility class that represents a meal that the user is trying to log.
    A meal is made up of multiple food objects.
    """

    def __init__(self, name):
        self.name = name
        self.k_cal = 0
        self.carb = 0
        self.protein = 0
        self.fat = 0
        # Generates a meal ID using Python's builtin has function, based on the name of the meal
        self.meal_id = hash(name)

    def add_food(self, food):
        """
        Adds a Food to the meal, and updates meal macros accordingly
        :param food: A Food object
        """
        self.k_cal += food.k_cal
        self.protein += food.protein
        self.carb += food.carb
        self.fat += food.fat


class Food:
    """
    Container / utility class that represents a food that the user is trying to log.
    """
    def __init__(self, food_id, food_name, k_cal, carb, protein, fat):
        self.id = food_id   # integer type, acquired from nutritics
        self.name = food_name
        self.k_cal = k_cal
        self.carb = carb
        self.protein = protein
        self.fat = fat


class NutriHandler:
    """
    Utility class used to make API calls for a particular client.
    TODO: Also used to make logging calls to the database???
    """
    def __init__(self, client_id):
        """
        :param client_id: The client's ID #TODO: ID TOKEN??
        """
        self.client_id = client_id
        print("Created a client nutrition handler for client {}".format(client_id))


    def build_food_req_string(self, food_name):
        """
        Build a request URL to get a single-item list from Nutritics for a food, with all macros for that food.
        :param food_name: The name of the food we're searching for
        :return: The URL to set the GET request to
        """
        reqstr = nc.FOOD_BASE_URL + food_name + nc.ALL_ATTRS + nc.LIMIT_ONE
        return reqstr

    def food_request(self, food_name, serving_size):
        """
        Makes a request to get info for a certain food.
        :param food_name: The name of the food
        :return: A Food object
        """
        # Make request to Nutritics
        r = requests.get(self.build_food_req_string(food_name), auth=(nc.NUTRITICS_USER, nc.NUTRITICS_PSWD))
        if r.status_code != 200:
            # There's been an error with the get request, so the operation fails
            # This is handled somewhere by the parent call
            return None

        food_data = r.json()[1]

        # Construct a food object from the request json
        food = Food(
            food_data["id"],
            food_data["name"],
            food_data["energyKcal"]["val"],
            food_data["carbohydrate"]["val"],
            food_data["protein"]["val"],
            food_data["fat"]["val"],
        )

        return food

    def log_food(self, food):
        """
        TODO:
        Log the food to the database for this client.
        :param food: The food to be logged
        :return: True if logging is successful, False if any error occurs
        """
        return False

    def log_meal(self, meal):
        """
        TODO:
        Log the meal to the database for this client.
        :param meal: THe meal to be logged
        :return: True if the loggin gis successful, False if any error occurs
        """

        # TODO: MAKE SURE THE MEAL CONTAINS AT LEAST ONE FOOD BEFORE LOGGING
        return False

    def get_serving_size(self):
        """
        Runs a query on the database to get the client's preferred serving size
        :return: The client's preferred serving size TODO: (grams???)
        """
        # TODO: Is this necessary?
        pass
