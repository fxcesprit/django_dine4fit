from django.db import models

# Create your models here.

class Nutrient(models.Model):
    name = models.CharField(max_length=50)
    daily_dose_min = models.DecimalField(max_digits=10, decimal_places=1)
    daily_dose_max = models.DecimalField(max_digits=10, decimal_places=1)
    short_desc = models.CharField(max_length=255)
    full_desc = models.TextField()
    img_url = models.URLField()

    def __str__(self):
        return self.name