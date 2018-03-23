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
    """
    def __init__(self, default_serving_size=100):
        """
        :param default_serving_size: Default serving size for any food object that's generated. Used to scale Nutritics
                    data. Defaults to 100 (for getFoodInfo requests)
        """
        self.client_default_serve_size = default_serving_size

    def food_request(self, food_name, serving_size=None):
        """
        Makes a request to get info for a certain food.
        :param food_name: The name of the food
        :param serving_size: The serving size of the food. By default is None, and is then later
                    evaluated to be the default serving size for the client. Can be overridden to
                    use a custom serving size indicated by the client
        :return: A Food object
        """
        # Make request to Nutritics
        r = requests.get(build_food_req_string(food_name), auth=(nc.NUTRITICS_USER, nc.NUTRITICS_PSWD))
        if r.status_code != 200:
            # There's been an error with the get request, so the operation fails
            raise RuntimeError("Nutritics request failed.")

        food_data = r.json()[1]

        scale = self.client_default_serve_size / 100
        if serving_size is not None:
            scale = serving_size / 100

        # Construct a food object from the request json
        food = Food(
            food_data["id"],
            food_data["name"],
            food_data["energyKcal"]["val"]*scale,
            food_data["carbohydrate"]["val"]*scale,
            food_data["protein"]["val"]*scale,
            food_data["fat"]["val"]*scale,
        )

        return food


def build_food_req_string(food_name):
    """
    Build a request URL to get a single-item list from Nutritics for a food, with all macros for that food.
    :param food_name: The name of the food we're searching for
    :return: The URL to set the GET request to
    """
    reqstr = nc.FOOD_BASE_URL + food_name + nc.ALL_ATTRS + nc.LIMIT_ONE
    return reqstr
