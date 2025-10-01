from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        managed = False
        db_table = 'auth_user'


class Nutrient(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    daily_dose_min = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, verbose_name='Дневная норма (г/кг массы тела) от')
    daily_dose_max = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, verbose_name='Дневная норма (г/кг массы тела) до')
    short_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name='Краткое описание')
    full_desc = models.TextField(blank=True, null=True, verbose_name='Полное описание')
    img_url = models.URLField(blank=True, null=True, verbose_name='Ссылка на изображение')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Нутриент'
        verbose_name_plural = 'Нутриенты'


class Dish(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название блюда")
    nutrients = models.JSONField(verbose_name="Пищевая ценность на 100г", default=dict, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"


class DishCompositionRequest(models.Model):
    class CompositionRequestStatus(models.TextChoices):
        DRAFT = "DR", _("Draft")
        DELETED = "DE", _("Deleted")
        FORMED = "FO", _("Formed")
        COMPLETED = "CO", _("Completed")
        REJECTED = "RE", _("Rejected")

    status = models.CharField(
        max_length=2,   
        choices=CompositionRequestStatus.choices,
        default=CompositionRequestStatus.DRAFT,
        verbose_name='Статус'
    )

    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    formation_datetime = models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования')
    completion_datetime = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_orders', verbose_name='Клиент')
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='managed_orders', blank=True, null=True, verbose_name='Менеджер')

    body_mass = models.IntegerField(blank=True, default=70)
    dish_mass = models.IntegerField(blank=True, default=500)
    dish = models.ForeignKey(Dish, on_delete=models.DO_NOTHING, blank=True, default=Dish.objects.first().pk)

    
    def calculate_nutrients(self):
        req_nutrients = DishCompositionNutrients.objects.filter(dish_composition_request = self.id)
        
        for nutrient in req_nutrients:
            nutrient.quantity_in_dish = self.dish.nutrients[f'{nutrient.nutrient.name}'] * (self.dish_mass / 1000)
            nutrient.daily_dose_percentage = (nutrient.quantity_in_dish / float((self.body_mass * (nutrient.nutrient.daily_dose_max + nutrient.nutrient.daily_dose_min) / 2))) * 100
            nutrient.save()
            #print(f"Произошел рассчет нутриентов: {nutrient.quantity_in_dish}, {nutrient.daily_dose_percentage}")


    def __setattr__(self, name, value):
        if name == "status" and value == 'CO':
            self.calculate_nutrients()

        return super().__setattr__(name, value)
    

    def __str__(self):
        return f"Запрос на описание блюда №{self.id}"
    

    class Meta:
        verbose_name = 'Описание блюда'
        verbose_name_plural = 'Описания блюд'


class DishCompositionNutrients(models.Model):
    dish_composition_request = models.ForeignKey(DishCompositionRequest, on_delete=models.DO_NOTHING, verbose_name='Запрос на описание')
    nutrient = models.ForeignKey(Nutrient, on_delete=models.DO_NOTHING, verbose_name='Нутриент')
    quantity_in_dish = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, verbose_name='Количество в блюде')
    daily_dose_percentage = models.IntegerField(verbose_name='Доля в дневной норме', blank=True, null=True)

    def __str__(self):
        return f"{self.dish_composition_request.id}-{self.nutrient.id}"

    class Meta:
        unique_together = ('dish_composition_request', 'nutrient')

        verbose_name = 'Список нутриентов в запросе на описание'
        verbose_name_plural = 'Списки нутриентов в запросах на описание'