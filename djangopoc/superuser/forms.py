from django import forms
from farmer.models import ICOEntity
from core.models import Farmer, Investor

class ICORejectionForm(forms.ModelForm):
    class Meta:
        model = ICOEntity
        fields = ['rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_rejection_reason(self):
        rejection_reason = self.cleaned_data.get('rejection_reason')

        if not rejection_reason.strip():
            raise forms.ValidationError("Please provide a rejection reason when rejecting an ICO.")
        
        return rejection_reason
    
class FarmerRejectionForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_rejection_reason(self):
        rejection_reason = self.cleaned_data.get('rejection_reason')

        if not rejection_reason.strip():
            raise forms.ValidationError("Please provide a rejection reason when rejecting an Farmer.")
        
        return rejection_reason
    

class InvestorRejectionForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['rejection_reason']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_rejection_reason(self):
        rejection_reason = self.cleaned_data.get('rejection_reason')

        if not rejection_reason.strip():
            raise forms.ValidationError("Please provide a rejection reason when rejecting an Investor.")
        
        return rejection_reason
