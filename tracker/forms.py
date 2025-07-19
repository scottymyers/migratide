from django import forms
from .models import MigraineEntry, TRIGGER_CHOICES, Medication, UserProfile, UserProfileSupplement, UserProfileMedication
from django_select2.forms import Select2MultipleWidget

class MigraineForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    trigger = forms.ChoiceField(choices=TRIGGER_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    medications = forms.ModelMultipleChoiceField(
        queryset=Medication.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-placeholder': 'Select or add medications'}),
        required=False
    )
    stress_level = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 11)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = MigraineEntry
        fields = [
            'date', 'trigger', 'medications', 'duration', 'severity', 'improved',
            'workout_time', 'workout_intensity', 'sleep_time', 'screen_time',
            'stress_level'
        ]
        widgets = {
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1:30:00'}),
            'severity': forms.NumberInput(attrs={'min': 1, 'max': 10, 'class': 'form-control'}),
            'improved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'workout_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0:45:00'}),
            'workout_intensity': forms.Select(attrs={'class': 'form-select'}),
            'sleep_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 7:00:00'}),
            'screen_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2:00:00'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthdate', 'drinks_from_plastic', 'zip_code']
        widgets = {
            'birthdate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'drinks_from_plastic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 90210'}),
        }

class SupplementForm(forms.ModelForm):
    class Meta:
        model = UserProfileSupplement
        fields = ['name', 'dosage', 'timing']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500mg'}),
            'timing': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Daily at 8 AM'}),
        }

class MedicationForm(forms.ModelForm):
    class Meta:
        model = UserProfileMedication
        fields = ['name', 'dosage', 'timing']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50mg'}),
            'timing': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. As needed'}),
        }