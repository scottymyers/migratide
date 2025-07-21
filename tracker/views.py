# File: tracker/views.py  0.1.2
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.db.models.functions import TruncMonth
from .models import MigraineEntry, UserProfile, Medication, UserProfileSupplement, UserProfileMedication
from .forms import MigraineForm, ProfileForm, SupplementForm, MedicationForm
import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
import json
from collections import Counter
from datetime import date, timedelta
import requests
import csv
import logging

# Set up logging
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def log_migraine(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = MigraineForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            if not profile.is_paid:
                entry.triggers = entry.patterns = entry.biorhythms = ''
                entry.duration = None
                entry.severity = 0
                entry.improved = False
                entry.workout_time = None
                entry.workout_intensity = ''
                entry.sleep_time = None
                entry.screen_time = None
                entry.stress_level = 0
            # Weather fetch for all users
            if profile.zip_code and profile.zip_code.isdigit() and len(profile.zip_code) == 5:
                try:
                    response = requests.get(
                        f"http://api.openweathermap.org/data/2.5/weather?zip={profile.zip_code},us&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
                    )
                    response.raise_for_status()
                    data = response.json()
                    entry.weather_pressure = data['main']['pressure']
                    entry.weather_temperature = data['main']['temp']
                    entry.weather_description = data['weather'][0]['description']
                    profile.cached_weather_pressure = entry.weather_pressure
                    profile.cached_weather_temperature = entry.weather_temperature
                    profile.cached_weather_description = entry.weather_description
                    profile.last_weather_fetch = timezone.now()
                    profile.save()
                except requests.exceptions.RequestException as e:
                    logger.error(f"Weather API error: {e}")
                    entry.weather_pressure = entry.weather_temperature = None
                    entry.weather_description = ''
            else:
                entry.weather_pressure = entry.weather_temperature = None
                entry.weather_description = ''
            entry.save()
            medications = form.cleaned_data['medications']
            selected_medications = []
            global_meds = ['Pain Killer', 'Sumatriptan', 'Naratriptan', 'Nurtec', 'Rizatriptan', 'Almotriptan', 'Eletriptan', 'Frovatriptan', 'Zolmitriptan', 'Ubrelvy', 'Topiramate']
            for med in medications:
                medication, created = Medication.objects.get_or_create(
                    name=med.name,
                    defaults={'user': request.user if med.name not in global_meds else None}
                )
                selected_medications.append(medication)
            entry.medications.set(selected_medications)
            return redirect('dashboard')
    else:
        form = MigraineForm()
    return render(request, 'log.html', {'form': form, 'is_paid': profile.is_paid})

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    entries = MigraineEntry.objects.filter(user=request.user).order_by('-date')

    latest_weather = {
        'pressure': profile.cached_weather_pressure,
        'temperature': profile.cached_weather_temperature,
        'description': profile.cached_weather_description or 'N/A',
        'date': profile.last_weather_fetch.date() if profile.last_weather_fetch else None
    }

    fetch_weather = (
        not latest_weather['pressure'] or
        (timezone.now() - profile.last_weather_fetch > timedelta(minutes=30) if profile.last_weather_fetch else True)
    )

    if entries and entries[0].weather_pressure:
        latest_weather = {
            'pressure': entries[0].weather_pressure,
            'temperature': entries[0].weather_temperature,
            'description': entries[0].weather_description or 'N/A',
            'date': entries[0].date
        }
    elif fetch_weather and profile.zip_code and len(profile.zip_code) == 5 and profile.zip_code.isdigit():
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?zip={profile.zip_code},us&appid={settings.OPENWEATHERMAP_API_KEY}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            latest_weather = {
                'pressure': data['main']['pressure'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'] or 'N/A',
                'date': date.today()
            }
            profile.cached_weather_pressure = latest_weather['pressure']
            profile.cached_weather_temperature = latest_weather['temperature']
            profile.cached_weather_description = latest_weather['description']
            profile.last_weather_fetch = timezone.now()
            profile.save()
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather fetch failed: {e}")
            latest_weather['description'] = 'Fetch Error'

    dates = [e.date for e in entries]
    triggers = [e.trigger for e in entries if e.trigger]
    top_triggers = Counter(triggers).most_common(5)
    freq = entries.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id')).order_by('month')
    freq_labels = [f['month'].strftime('%Y-%m') for f in freq] or ['No Data']
    freq_values = [f['count'] for f in freq] or [0]

    biorhythms = profile.calculate_biorhythms() if profile.birthdate else {'physical': 0, 'emotional': 0, 'intellectual': 0}
    bio_data = []
    for i in range(30):
        day = date.today() - timedelta(days=i)
        bio = profile.calculate_biorhythms(day) if profile.birthdate else {'physical': 0, 'emotional': 0, 'intellectual': 0}
        had_migraine = entries.filter(date=day)
        migraine_severity = had_migraine.aggregate(avg_sev=Avg('severity'))['avg_sev'] if had_migraine.exists() else None
        bio_data.append({'day': day.strftime('%Y-%m-%d'), 'physical': bio['physical'], 'emotional': bio['emotional'], 'intellectual': bio['intellectual'], 'migraine_severity': migraine_severity * 10 if migraine_severity else None})
    bio_data.reverse()

    context = {
        'entries': entries,
        'top_triggers': json.dumps(top_triggers or []),
        'freq_labels': json.dumps(freq_labels),
        'freq_values': json.dumps(freq_values),
        'bio_data': json.dumps(bio_data),
        'current_biorhythms': biorhythms,
        'is_paid': profile.is_paid,
        'latest_weather': latest_weather,
        'weather_error': "Unable to fetch weather. Check ZIP code or API." if not latest_weather['date'] else None,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    supplements = UserProfileSupplement.objects.filter(user=request.user)
    medications = UserProfileMedication.objects.filter(user=request.user)

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        supplement_form = SupplementForm(request.POST, prefix='supplement')
        medication_form = MedicationForm(request.POST, prefix='medication')

        if profile_form.is_valid():
            profile_form.save()

        if supplement_form.is_valid():
            supplement = supplement_form.save(commit=False)
            supplement.user = request.user
            supplement.save()

        if medication_form.is_valid():
            medication = medication_form.save(commit=False)
            medication.user = request.user
            medication.save()

        return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
        supplement_form = SupplementForm(prefix='supplement')
        medication_form = MedicationForm(prefix='medication')

    return render(request, 'profile.html', {
        'profile_form': profile_form,
        'supplement_form': supplement_form,
        'medication_form': medication_form,
        'supplements': supplements,
        'medications': medications,
        'is_paid': profile.is_paid,
    })

@login_required
def subscribe(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': 'Annual Subscription'},
                'unit_amount': 1000,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
        client_reference_id=str(request.user.id)
    )
    return redirect(session.url)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError:
        return JsonResponse({'status': 'invalid_payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'status': 'invalid_signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.is_paid = True
                profile.subscription_expiry = timezone.now() + timezone.timedelta(days=365)
                profile.save()
            except User.DoesNotExist:
                return JsonResponse({'status': 'user_not_found'}, status=400)
    return JsonResponse({'status': 'success'})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def success(request):
    return render(request, 'success.html', {'message': 'Subscription successful!'})

def cancel(request):
    return render(request, 'cancel.html', {'message': 'Subscription canceled.'})

@login_required
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="migraine_data.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Trigger', 'Severity', 'Improved', 'Workout Time', 'Workout Intensity',
        'Sleep Time', 'Screen Time', 'Weather Pressure', 'Weather Temperature',
        'Weather Description', 'Stress Level', 'Medications', 'Supplements', 'Drinks from Plastic'
    ])
    entries = MigraineEntry.objects.filter(user=request.user)
    profile = UserProfile.objects.get(user=request.user)
    supplements = UserProfileSupplement.objects.filter(user=request.user)
    profile_meds = UserProfileMedication.objects.filter(user=request.user)
    for entry in entries:
        meds = ', '.join([med.name for med in entry.medications.all()])
        supps = ', '.join([f"{supp.name} ({supp.dosage})" for supp in supplements])
        writer.writerow([
            entry.date, entry.trigger, entry.severity, entry.improved,
            entry.workout_time, entry.workout_intensity, entry.sleep_time,
            entry.screen_time, entry.weather_pressure, entry.weather_temperature,
            entry.weather_description, entry.stress_level, meds, supps,
            profile.drinks_from_plastic
        ])
    return response

@login_required
def admin_page(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    users = User.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            if action == 'toggle_paid':
                profile.is_paid = not profile.is_paid
                profile.save()
            elif action == 'delete':
                user.delete()
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            pass
        return redirect('admin_page')

    all_entries = MigraineEntry.objects.all().order_by('-date')
    freq = all_entries.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id')).order_by('month')
    freq_labels = [f['month'].strftime('%Y-%m') for f in freq] or ['No Data']
    freq_values = [f['count'] for f in freq] or [0]
    triggers = [e.trigger for e in all_entries if e.trigger]
    top_triggers = Counter(triggers).most_common(5)

    bio_data = []
    for i in range(30):
        day = date.today() - timedelta(days=i)
        profiles_with_birth = UserProfile.objects.exclude(birthdate=None)
        if profiles_with_birth:
            avg_bio = {
                'physical': sum(p.calculate_biorhythms(day)['physical'] for p in profiles_with_birth) / profiles_with_birth.count(),
                'emotional': sum(p.calculate_biorhythms(day)['emotional'] for p in profiles_with_birth) / profiles_with_birth.count(),
                'intellectual': sum(p.calculate_biorhythms(day)['intellectual'] for p in profiles_with_birth) / profiles_with_birth.count(),
            }
            had_migraine = all_entries.filter(date=day).exists()
            bio_data.append({'day': day.strftime('%Y-%m-%d'), **avg_bio, 'migraine': had_migraine})
    bio_data.reverse()

    context = {
        'users': users,
        'entries': all_entries[:10],
        'top_triggers': json.dumps(top_triggers or []),
        'freq_labels': json.dumps(freq_labels),
        'freq_values': json.dumps(freq_values),
        'bio_data': json.dumps(bio_data),
    }
    return render(request, 'admin_page.html', context)

@login_required
def upgrade(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.POST.get('upgrade_checkbox'):
            profile.is_paid = True
            profile.subscription_expiry = timezone.now() + timedelta(days=365)
            profile.save()
            return redirect('dashboard')
    return render(request, 'upgrade.html')