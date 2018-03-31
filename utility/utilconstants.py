import pytz

NUTRITICS_USER = "dashserver7"
NUTRITICS_PSWD = "csc301!!"

FOOD_BASE_URL = "https://www.nutritics.com/api/v1.1/LIST/&food="
ALL_ATTRS = "&attr=name,energyKcal,carbohydrate,protein,fat"
PROTEIN_ATTR = "&attr=name,protein"
FAT_ATTR = "&attr=name,fat"
CARBS_ATTR = "&attr=name,carbohydrate"

LIMIT_ONE = "&limit=1"

GOAL_PARAM_NAMES = ["water_ml", "fat_grams", "protein_grams", "carb_grams"]

FOOD_ENUM = ["food1", "food2", "food3", "food4", "food5"]
