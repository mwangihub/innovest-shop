from django import forms

from shop.models import Item, RELATED_DB_TYPES


class MyModel2Form(forms.ModelForm):
    """
    TODO: Test if this form can be implemented in admin panel
    """
    class Meta:
        model = Item
        fields = '__all__'
        labels = {'choice_field': 'Choice Field'}
        widgets = {'choice_field': forms.Select(choices=RELATED_DB_TYPES)}
