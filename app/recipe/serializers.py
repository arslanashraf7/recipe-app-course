from rest_framework import serializers

from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer to hold the Tag objects
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Serializer to hold and map the data of ingredients
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)
