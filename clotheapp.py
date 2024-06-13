import requests
from datetime import datetime
import smtplib
import json
import os  # Import os module for environment variables

def choose_clothes(temperature, weather, rain_percentage):
    clothes = ""
    if temperature < 10:
        clothes = "Manteau, écharpe et gants"
    elif 10 <= temperature < 20:
        clothes = "Pull et pantalon"
    else:
        clothes = "T-shirt et shorts"

    if weather in ["Rain", "Drizzle", "Thunderstorm"] or rain_percentage > 30:
        clothes += " et k-way"
    
    return clothes

def get_clothing_recommendations():
    api_key = os.getenv('OPENWEATHER_API_KEY')  # Use environment variable for API key
    city = 'Paris'
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"

    weekly_clothes = []
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data:
            for item in data['list']:
                if item['dt_txt'].endswith("00:00:00"):
                    date = item['dt_txt'].split(" ")[0]
                    weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                    temp = item['main']['temp']
                    weather_condition = item['weather'][0]['main']
                    rain_percentage = item['pop'] * 100
                    clothing_recommendation = choose_clothes(temp, weather_condition, rain_percentage)
                    weekly_clothes.append(f"Le {weekday}, vous devriez porter : {clothing_recommendation}")
    return "\n".join(weekly_clothes)

def send_email(message_body):
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = sender_email  # Assuming you're sending to yourself for now
    password = os.getenv('EMAIL_PASSWORD')
    subject = "Clothe This Week"
    text = f"Subject: {subject}\n\n{message_body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
        print("Email has been sent to " + receiver_email)
    except smtplib.SMTPException as e:
        print(f"An error occurred: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    # Obtenir les recommandations vestimentaires
    clothing_message = get_clothing_recommendations()
    # Envoyer l'email avec les recommandations
    send_email(clothing_message)
