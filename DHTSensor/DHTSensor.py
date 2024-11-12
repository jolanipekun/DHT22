import Adafruit_DHT
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, jsonify
import time

# Initialize Flask app
app = Flask(__name__)

# Set up DHT22 Sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4  # GPIO pin where the sensor is connected

# Set up Servo motor
SERVO_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency
servo.start(0)

# Default threshold and speed
TEMP_THRESHOLD = 30.0  # Temperature threshold in Celsius
servo_speed = 2.0      # Default speed in duty cycle

def read_temperature():
    """Reads temperature from the DHT22 sensor."""
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if temperature is not None:
        return temperature
    return None

def move_servo(temp):
    """Moves servo if temperature exceeds the threshold."""
    if temp > TEMP_THRESHOLD:
        servo.ChangeDutyCycle(servo_speed)
    else:
        servo.ChangeDutyCycle(0)  # Stop servo

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_threshold', methods=['POST'])
def update_threshold():
    global TEMP_THRESHOLD
    TEMP_THRESHOLD = float(request.form['threshold'])
    return jsonify(success=True)

@app.route('/control_servo', methods=['POST'])
def control_servo():
    global servo_speed
    servo_speed = float(request.form['speed'])
    return jsonify(success=True)

@app.route('/metrics')
def metrics():
    temp = read_temperature()
    move_servo(temp)
    return jsonify(temperature=temp, threshold=TEMP_THRESHOLD, servo_speed=servo_speed)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        pass
    finally:
        servo.stop()
        GPIO.cleanup()
