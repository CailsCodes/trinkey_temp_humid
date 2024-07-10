from math import exp
from time import sleep, monotonic

import adafruit_sht4x
import board
import touchio
import usb_cdc
from neopixel import NeoPixel
from rainbowio import colorwheel

colours = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "purple": (255, 0, 255),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255),
    "off": (0, 0, 0)
    }

# Initiate data connections
pixels = NeoPixel(board.NEOPIXEL, 1, auto_write=False, brightness=0.4)
touch_pad = touchio.TouchIn(board.TOUCH)
i2c = board.I2C()  # uses board.SCL and board.SDA
serial = usb_cdc.data

sht = adafruit_sht4x.SHT4x(i2c)
sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION # don't know what this does but it's in the docs


def get_temp_humid():
    temperature, relative_humidity = sht.measurements
    return temperature, relative_humidity

def calculate_VPD(temperature, relative_humidity):
    "Calculate Vapour-Pressure Deficit"
    svp = 0.6108 * exp(17.27 * temperature / (temperature + 237.3))
    avp = relative_humidity / 100 * svp
    vpd = svp - avp
    return vpd

def clear_pixels():
    pixels.fill(colours["off"])
    pixels.show()

def blink(colour="green", n=3):
    clear_pixels()
    for _ in range(n):
        pixels.fill(colours[colour])
        pixels.show()
        sleep(0.5)
        clear_pixels()
        sleep(0.5)

def buffer_cycle(colour="blue"):
    pixels.fill(colours[colour])
    pixels.show()
    sleep(0.2)
    clear_pixels()
    sleep(0.2)

def wait_for_connection():
    while not serial.connected:
        buffer_cycle()
    blink("green", n=1)
    serial.write(b'connected')

def send_data(t,h,v):
    text = ','.join([str(t),str(h),str(b)])
    msg = bytearray(text, 'utf-8')
    serial.write(msg)
    blink(n=1)

def main():
    clear_pixels()
    wait_for_connection()

    while serial.connected:
        pixels.fill(colorwheel((monotonic()*50)%255) )
        t,h = get_temp_humid()
        v = calculate_VPD(t,h)
        send_data(t,h,v)
        sleep(10)
        # sleep(60*10) # every 10 minutes
    main()

        
if __name__ == '__main__':
    main()