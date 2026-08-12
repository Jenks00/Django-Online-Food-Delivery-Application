from django import forms

from customer.models import MenuItem


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'image', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
