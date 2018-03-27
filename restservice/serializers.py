from rest_framework import serializers
from restservice.models import *
import json
from utility import utilconstants


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
            food_hash=validated_data["food_hash"],
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
    streak = serializers.IntegerField()
    score = serializers.IntegerField()
    timezone = serializers.CharField(max_length=32)

    def create(self, validated_data):
        """
        :param validated_data: a dict where each key corresponds to a field in Users
        """
        return Users.objects.create(
            user_id = validated_data["user_id"],
            name = validated_data["name"],
            serving_size = validated_data["serving_size"],
            streak = validated_data["streak"],
            score = validated_data["score"],
            timezone = validated_data["timezone"]
        )

    def update(self, instance, validated_data):
        """
        :param instance: a User instance to update
        :param validated_data: an int corresponding to a User instance's new score
        :return: updated instance with the new code
        """
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.name = validated_data.get('name', instance.name)
        instance.serving_size = validated_data.get('serving_size', instance.name)
        instance.streak = validated_data.get('streak', instance.streak)
        instance.score = validated_data.get('score', instance.score)
        instance.timezone = validated_data.get('timezone', instance.timezone)
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
        # TODO: Remove print statement in production
        print("GOAL OBJECT CREATED BY SERIALIZER, THIS SHOULDN'T HAPPEN, PLS FIX")

        fat_grams = validated_data["fat_grams"]
        protein_grams = validated_data["protein_grams"]
        carb_grams = validated_data["carb_grams"]
        kilocalories = (fat_grams * 9) + (4 * (protein_grams + carb_grams))

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
        # TODO: Doesn't work, verify validated data and only take certain values

        for goal_param in utilconstants.GOAL_PARAM_NAMES:
            try:
                value = validated_data[goal_param]
                setattr(instance, goal_param, value)
            except KeyError:
                print("The value for {} was not specified, so it was not updated".format(goal_param))


        # instance.water_ml = validated_data.get('water_ml', instance.water_ml)
        # instance.carb_grams = validated_data.get('carb_grams', instance.carb_grams)
        # instance.fat_grams = validated_data.get('fat_grams', instance.fat_grams)
        # instance.protein_grams = validated_data.get('protein_grams', instance.protein_grams)

        instance.kilocalories = ((instance.carb_grams + instance.protein_grams) * 4) + (instance.fat_grams * 9)
        instance.save()

        return instance
