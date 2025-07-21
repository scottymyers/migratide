# File: tracker/models.py 0.1.2
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import math

TRIGGER_CHOICES = [
    ('sugar', 'Sugar'),
    ('sleep', 'Lack of Sleep'),
    ('caffeine', 'Caffeine'),
    ('stress', 'Stress'),
    ('weather', 'Weather Changes'),
    ('alcohol', 'Alcohol'),
    ('dehydration', 'Dehydration'),
    ('hormones', 'Hormonal Changes'),
    ('food', 'Certain Foods (e.g., aged cheese, chocolate, MSG)'),
    ('exercise', 'Overexertion'),
    ('skipping_meals', 'Skipping Meals or Hunger'),
    ('strong_smells', 'Strong Smells (e.g., perfume, smoke)'),
    ('bright_lights', 'Bright Lights or Loud Noises'),
    ('smoking', 'Smoking'),
    ('unknown', 'Unknown'),
]

WORKOUT_INTENSITY_CHOICES = [
    ('low', 'Low'),
    ('moderate', 'Moderate'),
    ('high', 'High'),
]

ALCOHOL_CHOICES = [('none', 'None'), ('occasional', 'Occasional'), ('regular', 'Regular')]
CAFFEINE_CHOICES = [('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')]
HYDRATION_CHOICES = [('good', 'Good'), ('poor', 'Poor')]

class Medication(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    drinks_from_plastic = models.BooleanField(default=False)
    zip_code = models.CharField(max_length=10, blank=True)  # New field
    last_weather_fetch = models.DateTimeField(null=True, blank=True)
    cached_weather_pressure = models.FloatField(null=True, blank=True)
    cached_weather_temperature = models.FloatField(null=True, blank=True)
    cached_weather_description = models.CharField(max_length=100, blank=True)
    regular_exercise = models.BooleanField(default=False)
    smoking = models.BooleanField(default=False)
    alcohol_frequency = models.CharField(max_length=20, choices=ALCOHOL_CHOICES, default='none')
    caffeine_intake = models.CharField(max_length=20, choices=CAFFEINE_CHOICES, default='low')
    hydration_level = models.CharField(max_length=20, choices=HYDRATION_CHOICES, default='good')
    consistent_sleep = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def calculate_biorhythms(self, target_date=None):
        if not self.birthdate:
            return {'physical': 0, 'emotional': 0, 'intellectual': 0}
        target_date = target_date or timezone.now().date()
        days = (target_date - self.birthdate).days
        physical = math.sin(2 * math.pi * days / 23) * 100
        emotional = math.sin(2 * math.pi * days / 28) * 100
        intellectual = math.sin(2 * math.pi * days / 33) * 100
        return {'physical': round(physical, 2), 'emotional': round(emotional, 2), 'intellectual': round(intellectual, 2)}

class UserProfileSupplement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True)
    timing = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

class UserProfileMedication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, blank=True)
    timing = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

class MigraineEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES, blank=True)
    medications = models.ManyToManyField(Medication, blank=True)
    triggers = models.TextField(blank=True)
    patterns = models.TextField(blank=True)
    biorhythms = models.TextField(blank=True)
    duration = models.DurationField(null=True, blank=True)
    severity = models.IntegerField(default=0, blank=True)
    improved = models.BooleanField(default=False)
    workout_time = models.DurationField(null=True, blank=True)
    workout_intensity = models.CharField(max_length=20, choices=WORKOUT_INTENSITY_CHOICES, blank=True)
    sleep_time = models.DurationField(null=True, blank=True)
    screen_time = models.DurationField(null=True, blank=True)
    weather_pressure = models.FloatField(null=True, blank=True)  # hPa
    weather_temperature = models.FloatField(null=True, blank=True)  # Celsius
    weather_description = models.CharField(max_length=100, blank=True)  # New field (e.g., "clear", "rain")
    stress_level = models.IntegerField(default=0, blank=True)  # 1-10