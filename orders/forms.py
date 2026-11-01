"""
PackWise - Order Forms
"""

from django import forms
from django.core.exceptions import ValidationError
from orders.models import Order
from products.models import Product


class OrderCreateForm(forms.Form):
    order_number = forms.CharField(
        max_length=100,
        required=True,
        label="Order Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. ORD-2026-001',
            'id': 'id_order_number',
            'required': 'required'
        })
    )

    def clean_order_number(self):
        order_number = self.cleaned_data.get('order_number', '').strip()
        if not order_number:
            raise ValidationError("Order number cannot be empty.")
        if Order.objects.filter(order_number=order_number).exists():
            raise ValidationError(
                f"Order number '{order_number}' already exists. Please choose a unique order number."
            )
        return order_number

