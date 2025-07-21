# File: tracker/forms.py 0.1.2
from django import forms
from .models import MigraineEntry, UserProfile, UserProfileSupplement, UserProfileMedication, Medication

class MigraineForm(forms.ModelForm):
    medications = forms.ModelMultipleChoiceField(
        queryset=Medication.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = MigraineEntry
        fields = ['date', 'trigger', 'medications', 'triggers', 'patterns', 'biorhythms', 'duration', 'severity', 'improved', 'workout_time', 'workout_intensity', 'sleep_time', 'screen_time', 'stress_level']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthdate', 'zip_code', 'drinks_from_plastic', 'regular_exercise', 'smoking', 'alcohol_frequency', 'caffeine_intake', 'hydration_level', 'consistent_sleep']

class SupplementForm(forms.ModelForm):
    class Meta:
        model = UserProfileSupplement
        fields = ['name', 'dosage', 'timing']

class MedicationForm(forms.ModelForm):
    class Meta:
        model = UserProfileMedication
        fields = ['name', 'dosage', 'timing']