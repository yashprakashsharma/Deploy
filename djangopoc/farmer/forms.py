from django import forms
from .models import FarmerHistory, ICOEntity
from django.core.validators import RegexValidator, MaxLengthValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
import datetime

class FarmerHistoryForm(forms.ModelForm):
    season = forms.ChoiceField(
        choices=FarmerHistory.SEASON_CHOICES,
        # widget=forms.Select(attrs={'class': 'form-control'})
    )

     # Numeric and length 4 for year, first digit not 0, and less than current year
    current_year = datetime.datetime.now().year
    year = forms.IntegerField(
        validators=[
            RegexValidator(
                regex=r'^[1-9]\d{3}$',
                message='Enter a valid year.',
                code='invalid_year',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year', 'minlength': '4', 'maxlength': '4'})
    )

    # Alphabet + space for first name, not empty string, not only spaces
    crop = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+([ ][a-zA-Z]+)*$',
                message=_('Enter a valid crop name.'),
                code='invalid_crop_name',
            ),
            MaxLengthValidator(limit_value=20, message='Crop name must not exceed 20 characters.')
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crop Name', 'minlength': '1', 'maxlength': '20', 'pattern': '^[a-zA-Z]+([ ][a-zA-Z]+)*$', 'title': 'Enter valid cropname'})
    )

    area_cultivated = forms.FloatField(
        validators=[MinValueValidator(1, message='Area cultivated must be more than 1 square meters.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Area in square meters.', 'min': '1'})
    )

    revenue = forms.FloatField(
        validators=[MinValueValidator(0, message='Revenue generated must be more than 0.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Revenue Generated(in Rs)', 'min': '0'})
    )

    expenses = forms.FloatField(
        validators=[MinValueValidator(0, message='Expenses must be more than 0.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Expenses incurred(in Rs)', 'min': '1'})
    )


    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and int(year) >= self.current_year:
            raise forms.ValidationError('Enter a valid year.')
        return year
    class Meta:
        model = FarmerHistory
        fields = ['season', 'year', 'crop', 'area_cultivated', 'revenue', 'expenses']




class ICOEntityForm(forms.ModelForm):
    crop = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+([ ][a-zA-Z]+)*$',
                message=_('Enter a valid crop name.'),
                code='invalid_crop_name',
            ),
            MaxLengthValidator(limit_value=20, message='Crop name must not exceed 20 characters.')
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crop Name', 'minlength': '1', 'maxlength': '20', 'pattern': '^[a-zA-Z]+([ ][a-zA-Z]+)*$', 'title': 'Enter valid cropname'})
    )

    land_area = forms.FloatField(
        validators=[MinValueValidator(1, message='Land area must be more than 1 square meter.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Land Area in square meters', 'min': '1', 'step': '0.01'})
    )

    capital = forms.FloatField(
        validators=[MinValueValidator(1, message='Capital must be more than 1.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Initial Capital(Rs)', 'min': '100', 'step': '0'})
    )

    quantity = forms.IntegerField(
        validators=[MinValueValidator(1, message='Quantity must be more than 1.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'No of ICO stocks', 'min': '1'})
    )

    closes_on = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Closing Date'}),
        input_formats=['%Y-%m-%dT%H:%M']  # Adjust the date-time format based on your requirements
    )

    return_date = forms.DateTimeField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Return Date'}),
        input_formats=['%Y-%m-%dT%H:%M']  # Adjust the date-time format based on your requirements
    )

    class Meta:
        model = ICOEntity
        fields = ['crop', 'land_area', 'capital', 'quantity', 'closes_on', 'return_date']



class ICOReturnsForm(forms.Form):
    revenue = forms.IntegerField(label='Revenue', required=True, min_value=0)
    # expenses = forms.IntegerField(label='Expenses', required=True, min_value=0)