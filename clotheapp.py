import requests
from datetime import datetime, timedelta
import smtplib
import os

# Dictionnaire pour la traduction des jours de la semaine
days_in_french = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche"
}

def choose_clothes(temperature, weather, rain_percentage):
    clothes = ""
    if temperature < 10:
        clothes = "Manteau, écharpe et gants"
    elif 10 <= temperature < 20:
        clothes = "Pull et pantalon"
    else:
        clothes = "T-shirt et shorts"

    if weather in ["pluie", "bruine", "orage"] or rain_percentage > 30:
        clothes += " et k-way"
    
    return clothes

def get_weather_forecast():
    api_key = os.getenv('OPENWEATHER_API_KEY')  # Utiliser la variable d'environnement pour la clé API
    city = 'Paris'
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=fr"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Erreur lors de la récupération des données météorologiques")

def get_tomorrow_clothing_recommendations(data):
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    morning_forecast = None
    evening_forecast = None

    for item in data['list']:
        forecast_time = datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
        if forecast_time.date() == tomorrow:
            if forecast_time.hour == 6:  # Prévision du matin
                morning_forecast = item
            elif forecast_time.hour == 18:  # Prévision du soir
                evening_forecast = item

    if morning_forecast and evening_forecast:
        morning_temp = morning_forecast['main']['temp']
        morning_weather = morning_forecast['weather'][0]['description']
        morning_rain_percentage = morning_forecast['pop'] * 100

        evening_temp = evening_forecast['main']['temp']
        evening_weather = evening_forecast['weather'][0]['description']
        evening_rain_percentage = evening_forecast['pop'] * 100

        morning_clothes = choose_clothes(morning_temp, morning_weather, morning_rain_percentage)
        evening_clothes = choose_clothes(evening_temp, evening_weather, evening_rain_percentage)

        message = (
            f"Prévisions météo pour demain:\n"
            f"Matin: {morning_temp}°C, {morning_weather.capitalize()}, Pluie: {morning_rain_percentage}%.\n"
            f"Recommandation vestimentaire: {morning_clothes}\n\n"
            f"Soir: {evening_temp}°C, {evening_weather.capitalize()}, Pluie: {evening_rain_percentage}%.\n"
            f"Recommandation vestimentaire: {evening_clothes}\n\n\n\n\n"
        )
        return message
    else:
        return "Prévisions météorologiques pour demain indisponibles.\n\n\n\n\n"

def get_weekly_clothing_recommendations(data):
    weekly_clothes = []
    forecasts_by_day = {}

    for item in data['list']:
        date = item['dt_txt'].split(" ")[0]
        if date not in forecasts_by_day:
            forecasts_by_day[date] = []
        forecasts_by_day[date].append(item)

    for date, forecasts in forecasts_by_day.items():
        forecast_date = datetime.strptime(date, "%Y-%m-%d").date()
        if forecast_date <= datetime.now().date() + timedelta(days=1):
            continue  # Ignore today's and tomorrow's forecasts

        morning_forecast = None
        evening_forecast = None
        for forecast in forecasts:
            forecast_time = datetime.strptime(forecast['dt_txt'], "%Y-%m-%d %H:%M:%S")
            if forecast_time.hour == 6:
                morning_forecast = forecast
            elif forecast_time.hour == 18:
                evening_forecast = forecast

        if morning_forecast and evening_forecast:
            morning_temp = morning_forecast['main']['temp']
            morning_weather = morning_forecast['weather'][0]['description']
            morning_rain_percentage = morning_forecast['pop'] * 100

            evening_temp = evening_forecast['main']['temp']
            evening_weather = evening_forecast['weather'][0]['description']
            evening_rain_percentage = evening_forecast['pop'] * 100

            morning_clothes = choose_clothes(morning_temp, morning_weather, morning_rain_percentage)
            evening_clothes = choose_clothes(evening_temp, evening_weather, evening_rain_percentage)

            weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            weekday_french = days_in_french[weekday]
            weekly_clothes.append(
                f"Le {weekday_french}:\n"
                f"Matin: {morning_temp}°C, {morning_weather.capitalize()}, Pluie: {morning_rain_percentage}%.\n"
                f"Recommandation vestimentaire: {morning_clothes}\n"
                f"Soir: {evening_temp}°C, {evening_weather.capitalize()}, Pluie: {evening_rain_percentage}%.\n"
                f"Recommandation vestimentaire: {evening_clothes}\n"
            )

    return "\n\n\n\n\n".join(weekly_clothes)

def send_email(subject, message_body):
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = sender_email  # Supposons que vous vous envoyez l'email à vous-même pour le moment
    password = os.getenv('EMAIL_PASSWORD')
    text = f"Subject: {subject}\n\n{message_body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text.encode('utf-8'))
        print("L'email a été envoyé à " + receiver_email)
    except smtplib.SMTPException as e:
        print(f"Une erreur est survenue: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    # Obtenir les prévisions météo
    weather_data = get_weather_forecast()
    
    # Obtenir les recommandations vestimentaires pour demain
    daily_clothing_message = get_tomorrow_clothing_recommendations(weather_data)
    
    # Obtenir les recommandations vestimentaires pour la semaine
    weekly_clothing_message = get_weekly_clothing_recommendations(weather_data)

    # Combiner les messages pour envoyer un seul email
    combined_message = daily_clothing_message + weekly_clothing_message

    # Envoyer l'email avec les recommandations
    send_email("Prévisions Météo et Recommandations Vestimentaires", combined_message)
