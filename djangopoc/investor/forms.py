from django import forms

class BuyICOForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)