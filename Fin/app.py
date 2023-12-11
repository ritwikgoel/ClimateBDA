# app.py
from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_images', methods=['POST'])
def fetch_images():
    selected_date = request.form['datepicker']

    # Run the Python script to generate images
    subprocess.run(['python3', 'predictions.py', selected_date])

    return render_template('display_images.html', selected_date=selected_date)

@app.route('/openweather')
def openweather():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    date = request.args.get('date')

    try:
        openweather_data = predictions.get_weather_data(date, latitude, longitude)
        return jsonify(openweather_data)
    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)