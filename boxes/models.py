from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Box(models.Model):
    name = models.CharField(max_length=255)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Internal length must be greater than zero.')],
        help_text='Internal length in cm'
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Internal width must be greater than zero.')],
        help_text='Internal width in cm'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Internal height must be greater than zero.')],
        help_text='Internal height in cm'
    )
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Maximum weight capacity must be greater than zero.')],
        help_text='Maximum weight capacity in kg'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message='Cost must be greater than zero.')],
        help_text='Cost in Indian Rupees (INR)'
    )

    class Meta:
        verbose_name = 'Box'
        verbose_name_plural = 'Boxes'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height} cm, max {self.max_weight} kg, INR {self.cost})"
