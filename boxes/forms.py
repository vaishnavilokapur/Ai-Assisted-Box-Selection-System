from django import forms
from .models import Box


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ['name', 'length', 'width', 'height', 'max_weight', 'cost']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Small Parcel, Medium Shipper'
            }),
            'length': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'max_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
        }
        labels = {
            'name': 'Box Name',
            'length': 'Internal Length (cm)',
            'width': 'Internal Width (cm)',
            'height': 'Internal Height (cm)',
            'max_weight': 'Maximum Weight Capacity (kg)',
            'cost': 'Packaging Cost (₹)',
        }

