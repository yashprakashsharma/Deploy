# yourapp/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator, MaxLengthValidator, MinValueValidator, FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Farmer, Investor

def validate_pdf(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError('Only PDF files are allowed.')

class CustomUserCreationForm(UserCreationForm):
    # Alphanumeric + special characters for username
    username = forms.CharField(
        validators=[
            MaxLengthValidator(50, message='username must be of length less than 50.'),
            RegexValidator(
                regex=r'^[a-zA-z0-9]+$',
                message=_('Enter a valid username containing alphanumeric characters.'),
                code='invalid_username',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'maxlength': '50', 'minlength': '1', 'pattern': '^[^\s]+$', 'title': 'No spaces allowed'})
    )

    # Valid email address
    email = forms.EmailField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.(com|edu|net)',
                message=_('Invalid email address'),
                code='invalid_email',
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'abc@gmail.com', 'pattern': '^[^\s]+$', 'title': 'No spaces allowed'}),
        max_length=50
    )

    # Alphabet + space for first name, not empty string, not only spaces
    first_name = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+([ ][a-zA-Z]+)*$',
                message=_('Enter a valid first name.'),
                code='invalid_first_name',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'maxlength': '30', 'minlength': '1', 'pattern': '^[a-zA-Z]+([ ][a-zA-Z]+)*$', 'title': 'Enter valid firstname'})
    )

    # Alphabet + space for last name, can be empty
    last_name = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]*$',
                message=_('Enter a valid last name. This value may contain only alphabet characters.'),
                code='invalid_last_name',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'maxlength': '30', 'pattern': '^[a-zA-Z]*$', 'title': 'Enter valid lastname'})
    )

    # Numeric and length 10 for phone
    phone = forms.CharField(
        validators=[
            RegexValidator(
                # regex=r'^\d{10}$',
                regex=r'^[1-9]\d{9}$',
                message=_('Enter a valid phone number. This value must be numeric and have a length of 10.'),
                code='invalid_phone',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Contact Number', 'maxlength': '10', 'minlength': '10'})
    )

    user_type = forms.ChoiceField(
        choices=[('F', 'Farmer'), ('I', 'Investor')],
        initial='I',  # You can set the initial value to 'I' or any other default value
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the form-control class to password and confirm password fields
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].widget.attrs['pattern'] = '^[^\s]+$'
        self.fields['password1'].widget.attrs['title'] = 'No spaces allowed'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm-password'
        self.fields['password2'].widget.attrs['pattern'] = '^[^\s]+$'
        self.fields['password2'].widget.attrs['title'] = 'No spaces allowed'
        # self.fields['user_type'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'user_type']

class LoginForm(forms.Form):
    # username = forms.CharField()
    # password = forms.CharField(widget=forms.PasswordInput)
    username = forms.EmailField(
        # validators=[EmailValidator(message=_('Enter a valid email address.'), code='invalid_email')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'youremail@gmail.com', 'pattern': '^[^\s]+$', 'title': 'No spaces allowed'}),
        max_length=50
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'pattern': '^[^\s]+$', 'title': 'No spaces allowed'})
    )

class FarmerRegistrationForm(forms.ModelForm):
    # Aadhar number validation: 12-digit number
    aadhar_number = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message='Invalid Aadhar Number.',
                code='invalid_aadhar_number',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Aadhar Number', 'maxlength': '12', 'minlength': '12' })
    )

    # PAN number validation: Length of 10, specific format
    pan_number = forms.CharField(
        validators=[
            MinLengthValidator(10, message='PAN number must be of length 10.'),
            RegexValidator(
                regex=r'^[A-Z]{5}\d{4}[A-Z]{1}$',
                message='Invalid PAN number.',
                code='invalid_pan_number_format',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'PAN Number', 'maxlength': '10', 'minlength': '10' })
    )

    # Land area validation: More than 1 square meters
    land_area = forms.FloatField(
        validators=[MinValueValidator(1, message='Land area must be more than 1 square meters.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Land Area in square meters.'})
    )

    documents = forms.FileField(
        label='Upload Documents (PDF only)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        validators=[FileExtensionValidator(['pdf']), validate_pdf],
    )
    class Meta:
        model = Farmer
        fields = ['aadhar_number', 'pan_number', 'land_area', 'documents']

class InvestorRegistrationForm(forms.ModelForm):
    # Aadhar number validation: 12-digit number
    aadhar_number = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message='Invalid Aadhar number.',
                code='invalid_aadhar_number',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'Aadhar Number', 'maxlength': '12', 'minlength': '12'})
    )

    # PAN number validation: Length of 10, specific format
    pan_number = forms.CharField(
        validators=[
            MinLengthValidator(10, message='PAN number must be of length 10.'),
            RegexValidator(
                regex=r'^[A-Z]{5}\d{4}[A-Z]{1}$',
                message='Invalid PAN number.',
                code='invalid_pan_number_format',
            ),
        ],
        widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': 'PAN Number', 'maxlength': '10', 'minlength': '10'})
    )

    documents = forms.FileField(
        label='Upload Documents (PDF only)',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        validators=[FileExtensionValidator(['pdf']), validate_pdf],
    )

    class Meta:
        model = Investor
        fields = ['aadhar_number', 'pan_number', 'documents']