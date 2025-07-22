from django import forms
from .models import MigraineEntry, TRIGGER_CHOICES

class MigraineForm(forms.ModelForm):
    trigger = forms.ChoiceField(choices=TRIGGER_CHOICES, required=False)
    class Meta:
        model = MigraineEntry
        fields = ['date', 'trigger', 'triggers', 'patterns', 'biorhythms', 'medications', 'duration', 'severity', 'improved']
