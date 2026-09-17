from machine import Pin, ADC, I2C, PWM
import time
import math

# =========================================================
# ROCKFALL PREDICTION SYSTEM
# ESP32 + MicroPython
# =========================================================

# -------------------------
# ANALOG SENSORS
# -------------------------

rain_sensor = ADC(Pin(34))
moisture_sensor = ADC(Pin(35))
displacement_sensor = ADC(Pin(32))

# ESP32 ADC range
rain_sensor.atten(ADC.ATTN_11DB)
moisture_sensor.atten(ADC.ATTN_11DB)
displacement_sensor.atten(ADC.ATTN_11DB)


# -------------------------
# VIBRATION SENSOR
# -------------------------

vibration_sensor = Pin(27, Pin.IN, Pin.PULL_UP)


# -------------------------
# LEDs
# -------------------------

green_led = Pin(25, Pin.OUT)
yellow_led = Pin(26, Pin.OUT)
red_led = Pin(14, Pin.OUT)


# -------------------------
# BUZZER
# -------------------------

buzzer = PWM(Pin(13))
buzzer.freq(2000)
buzzer.duty(0)


# -------------------------
# I2C
# MPU6050 + OLED
# -------------------------

i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=400000
)

print("I2C Devices Found:", i2c.scan())


# =========================================================
# OLED
# =========================================================

oled = None

try:
    from ssd1306 import SSD1306_I2C

    devices = i2c.scan()

    if 0x3C in devices:
        oled = SSD1306_I2C(
            128,
            64,
            i2c,
            addr=0x3C
        )

        print("OLED detected successfully")

    else:
        print("OLED not detected")
        print("System will continue without OLED")

except Exception as e:
    print("OLED error:", e)
    oled = None


# =========================================================
# MPU6050
# =========================================================

MPU6050_ADDR = 0x68

mpu_available = False

try:

    devices = i2c.scan()

    if MPU6050_ADDR in devices:

        # Wake up MPU6050
        i2c.writeto_mem(
            MPU6050_ADDR,
            0x6B,
            b'\x00'
        )

        time.sleep(0.1)

        mpu_available = True

        print("MPU6050 detected successfully")

    else:

        print("MPU6050 not detected")
        print("Tilt will be set to 0 degrees")

except Exception as e:

    print("MPU6050 error:", e)
    mpu_available = False


# =========================================================
# FUNCTIONS
# =========================================================

def read_percentage(adc):
    """
    Convert ADC value (0-4095)
    into percentage (0-100).
    """

    value = adc.read()

    percentage = int((value / 4095) * 100)

    if percentage < 0:
        percentage = 0

    if percentage > 100:
        percentage = 100

    return percentage


# ---------------------------------------------------------
# Read MPU6050 acceleration
# ---------------------------------------------------------

def read_mpu6050():

    if not mpu_available:
        return 0

    try:

        data = i2c.readfrom_mem(
            MPU6050_ADDR,
            0x3B,
            6
        )

        # Combine high and low bytes
        ax = (data[0] << 8) | data[1]
        ay = (data[2] << 8) | data[3]
        az = (data[4] << 8) | data[5]

        # Convert to signed values
        if ax > 32767:
            ax -= 65536

        if ay > 32767:
            ay -= 65536

        if az > 32767:
            az -= 65536

        # Convert to g
        ax = ax / 16384.0
        ay = ay / 16384.0
        az = az / 16384.0

        # Calculate tilt angle
        angle_x = math.degrees(
            math.atan2(
                ax,
                math.sqrt(ay * ay + az * az)
            )
        )

        angle_y = math.degrees(
            math.atan2(
                ay,
                math.sqrt(ax * ax + az * az)
            )
        )

        tilt = max(
            abs(angle_x),
            abs(angle_y)
        )

        return int(tilt)

    except Exception as e:

        print("MPU read error:", e)
        return 0


# ---------------------------------------------------------
# Convert tilt angle to score
# ---------------------------------------------------------

def calculate_tilt_score(tilt):

    if tilt < 10:
        return 0

    elif tilt < 20:
        return 30

    elif tilt < 30:
        return 60

    else:
        return 100


# ---------------------------------------------------------
# Display on OLED
# ---------------------------------------------------------

def display_oled(
    rainfall,
    moisture,
    displacement,
    tilt,
    vibration,
    score,
    risk
):

    if oled is None:
        return

    try:

        oled.fill(0)

        oled.text("ROCKFALL ALERT", 0, 0)

        oled.text(
            "Rain: " + str(rainfall) + "%",
            0,
            10
        )

        oled.text(
            "Moist: " + str(moisture) + "%",
            0,
            20
        )

        oled.text(
            "Move: " + str(displacement) + "%",
            0,
            30
        )

        oled.text(
            "Tilt: " + str(tilt) + " deg",
            0,
            40
        )

        oled.text(
            risk,
            0,
            50
        )

        oled.show()

    except Exception as e:

        print("OLED display error:", e)


# ---------------------------------------------------------
# LED control
# ---------------------------------------------------------

def set_leds(risk):

    # First turn everything OFF
    green_led.value(0)
    yellow_led.value(0)
    red_led.value(0)

    # LOW
    if risk == "LOW":

        green_led.value(1)

    # MEDIUM
    elif risk == "MEDIUM":

        yellow_led.value(1)

    # HIGH
    elif risk == "HIGH":

        red_led.value(1)


# ---------------------------------------------------------
# Buzzer control
# ---------------------------------------------------------

def set_buzzer(risk):

    if risk == "HIGH":

        buzzer.duty(512)

    else:

        buzzer.duty(0)


# =========================================================
# START
# =========================================================

print()
print("===================================")
print("   ROCKFALL PREDICTION SYSTEM")
print("===================================")
print("System Started")
print()


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # ---------------------------------
    # Read sensors
    # ---------------------------------

    rainfall = read_percentage(rain_sensor)

    moisture = read_percentage(moisture_sensor)

    displacement = read_percentage(
        displacement_sensor
    )


    # ---------------------------------
    # Read tilt
    # ---------------------------------

    tilt = read_mpu6050()

    tilt_score = calculate_tilt_score(tilt)


    # ---------------------------------
    # Read vibration
    # ---------------------------------

    if vibration_sensor.value() == 0:

        vibration = 100

    else:

        vibration = 0


    # ---------------------------------
    # Calculate risk score
    # ---------------------------------

    score = (
        rainfall * 0.25
        + moisture * 0.20
        + displacement * 0.25
        + tilt_score * 0.20
        + vibration * 0.10
    )

    score = int(score)


    # ---------------------------------
    # Risk classification
    # ---------------------------------

    # Strong vibration + dangerous
    # environmental condition
    if vibration == 100 and (
        rainfall >= 60
        or moisture >= 60
        or displacement >= 60
    ):

        risk = "HIGH"


    elif score >= 60:

        risk = "HIGH"


    elif score >= 30:

        risk = "MEDIUM"


    else:

        risk = "LOW"


    # ---------------------------------
    # LEDs
    # ---------------------------------

    set_leds(risk)


    # ---------------------------------
    # Buzzer
    # ---------------------------------

    set_buzzer(risk)


    # ---------------------------------
    # OLED
    # ---------------------------------

    display_oled(
        rainfall,
        moisture,
        displacement,
        tilt,
        vibration,
        score,
        risk
    )


    # ---------------------------------
    # Serial Monitor
    # ---------------------------------

    print("-----------------------------------")

    print(
        "Rainfall      :",
        rainfall,
        "%"
    )

    print(
        "Soil Moisture :",
        moisture,
        "%"
    )

    print(
        "Displacement  :",
        displacement,
        "%"
    )

    print(
        "Tilt          :",
        tilt,
        "degrees"
    )

    print(
        "Vibration     :",
        vibration
    )

    print(
        "Risk Score    :",
        score
    )

    print(
        "Risk Level    :",
        risk
    )

    print("-----------------------------------")


    # Wait 1 second
    time.sleep(1)
