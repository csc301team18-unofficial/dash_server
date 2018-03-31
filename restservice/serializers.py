from rest_framework import serializers

from restservice.models import *
from utility import utilconstants
from utility import utils


class FoodCacheSerializer(serializers.Serializer):
    food_hash = serializers.CharField(read_only=True, max_length=32)
    food_name = serializers.CharField(max_length=100)
    kilocalories = serializers.IntegerField()
    fat_grams = serializers.IntegerField()
    carb_grams = serializers.IntegerField()
    protein_grams = serializers.IntegerField()

    def create(self, validated_data):
        """
        :param validated_data: a dict where each key corresponds to a field in FoodCache
        """
        return FoodCache.objects.create(
            food_id=validated_data["food_id"],
            food_name=validated_data["food_name"],
            kilocalories=validated_data["kilocalories"],
            fat_grams=validated_data["fat_grams"],
            carb_grams=validated_data["carb_grams"],
            protein_grams=validated_data["protein_grams"]
        )

    def update(self, instance, validated_data):
        instance.food_name = validated_data.get('name', instance.food_name)
        instance.kilocalories = validated_data.get('kilocalories', instance.kilocalories)
        instance.fat_grams = validated_data.get('fat_grams', instance.fat_grams)
        instance.carb_grams = validated_data.get('carb_grams', instance.carb_grams)
        instance.protein_grames = validated_data.get('protein_grams', instance.protein_grames)
        instance.save()
        return instance


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=20, read_only=True)
    name = serializers.CharField(max_length=150)
    serving_size = serializers.IntegerField(default=100)
    sprint = serializers.IntegerField()
    points = serializers.IntegerField()

    def create(self, validated_data):
        """
        :param validated_data: a dict where each key corresponds to a field in Users
        """
        return Users.objects.create(
            user_id=validated_data["user_id"],
            name=validated_data["name"],
            serving_size=validated_data["serving_size"],
            sprint=validated_data["streak"],
            points=validated_data["points"],
        )

    def update(self, instance, validated_data):
        """
        :param instance: a User instance to update
        :param validated_data: an int corresponding to a User instance's new points
        :return: updated instance with the new code
        """
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.name = validated_data.get('name', instance.name)
        instance.serving_size = validated_data.get('serving_size', instance.name)
        instance.sprint = validated_data.get('streak', instance.streak)
        instance.points = validated_data.get('points', instance.points)
        instance.save()

        return instance


class GoalsSerializer(serializers.Serializer):
    goal_id = serializers.CharField(max_length=32)
    user_id = serializers.CharField()
    water_ml = serializers.IntegerField()
    protein_grams = serializers.IntegerField()
    fat_grams = serializers.IntegerField()
    carb_grams = serializers.IntegerField()
    kilocalories = serializers.IntegerField()

    def create(self, validated_data):
        """
        :param validated_data: a dict where each key corresponds to a field in Users
        """
        fat_grams = validated_data["fat_grams"]
        protein_grams = validated_data["protein_grams"]
        carb_grams = validated_data["carb_grams"]
        kilocalories = utils.calories_from_macros(carb_grams, fat_grams, protein_grams)

        return Users.objects.create(
            goal_id=validated_data["goal_id"],
            user_id=validated_data["user_id"],
            water_ml=validated_data["water_ml"],
            fat_grams=fat_grams,
            protein_grams=protein_grams,
            carb_grams=carb_grams,
            kilocalories=kilocalories
        )

    def update(self, instance, validated_data):
        # TODO: Remove this in production
        print("GAMESERIALIZER UPDATE CALLED, SOMETHING HAS GONE HORRIBLY WRONG")

        for goal_param in utilconstants.GOAL_PARAM_NAMES:
            try:
                value = validated_data[goal_param]
                setattr(instance, goal_param, value)
            except KeyError:
                print("The value for {} was not specified, so it was not updated".format(goal_param))

        instance.kilocalories = utils.calories_from_macros(
            instance.carb_grams,
            instance.fat_grams,
            instance.protein_grams
        )

        instance.save()

        return instance
