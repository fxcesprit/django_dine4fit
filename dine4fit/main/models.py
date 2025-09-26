from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Nutrient(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    daily_dose_min = models.DecimalField(max_digits=10, decimal_places=1, blank=True, verbose_name='Дневная норма (г/кг массы тела) от')
    daily_dose_max = models.DecimalField(max_digits=10, decimal_places=1, blank=True, verbose_name='Дневная норма (г/кг массы тела) до')
    short_desc = models.CharField(max_length=255, blank=True, verbose_name='Краткое описание')
    full_desc = models.TextField(blank=True, verbose_name='Полное описание')
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

    body_mass = models.IntegerField(blank=True)
    dish_mass = models.IntegerField(blank=True)
    dish = models.ForeignKey(Dish, on_delete=models.DO_NOTHING, blank=True)

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