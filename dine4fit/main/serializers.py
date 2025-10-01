from rest_framework import serializers

from .models import DishCompositionNutrients, DishCompositionRequest, Nutrient, AuthUser


class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        #убрать служебные поля после тестов
        fields = ('name', 'daily_dose_min', 'daily_dose_max', 'short_desc', 'full_desc', 'img_url')


class DishCompositionNutrientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели связи M2M"""
    nutrient = NutrientSerializer(read_only=True)
    
    class Meta:
        model = DishCompositionNutrients 
        fields = ('nutrient', 'quantity_in_dish', 'daily_dose_percentage')  


class DishCompositionRequestSerializer(serializers.ModelSerializer):
    nutrients = DishCompositionNutrientSerializer(
        source='dishcompositionnutrients_set',
        many=True,
        read_only=True
    )
    class Meta:
        model = DishCompositionRequest
        fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager', 'body_mass', 'dish_mass', 'dish', 'nutrients')
        read_only_fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager')

class DishCompositionRequestFlatSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='client.username', read_only=True)
    manager = serializers.CharField(source='manager.username', read_only=True)
    class Meta:
        model = DishCompositionRequest
        fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager', 'body_mass', 'dish_mass', 'dish')
        read_only_fields = ('status', 'creation_datetime', 'formation_datetime', 'completion_datetime', 'client', 'manager')

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ('username', 'email', 'date_joined')