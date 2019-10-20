#!/usr/bin/env python

from ola.ClientWrapper import ClientWrapper
from neopixel import *
import math

# LED strip configuration:
LED_COUNT      = 80      # Number of LED pixels.
LED_PIN        = 10      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0
LED_STRIP      = ws.WS2812_STRIP

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()

# The maximum number of segments the LED strip is divided in
# If more bytes are received, they are ignored.
# If less bytes are received, the strip will be divided into less segements
STRIP_MAX_SEGMENTS = 16
DMX_BYTES_PER_SEGMENT = 3 # For RGB
DMX_UNIVERSE = 1

def cancel_draw(data):
  print('Incorrectly formatted message:')
  print(data)
  print('Will not draw the frame printed above.')

# Draw RGB data consisting of multiple RGB values.
# The strip is split into as many sections as required
# data can be any iterable, from DMX we expect byte arrays
def draw(data):
  print('Start message receive...')
  # Find out how many segments the strip should get split into
  # If the data sent doesn't divide evenly into segments, some bytes will be ignored
  num_segments = int(min(\
                     STRIP_MAX_SEGMENTS,\
                     math.floor(len(data)/DMX_BYTES_PER_SEGMENT)\
                    ))
  print('Will draw ' + str(num_segments) + ' segments.')

  # Determine how many LEDs belong to each segment
  leds_per_segment = int(math.ceil(LED_COUNT/num_segments))

  for fixture in range(0, num_segments):
    try:
      # decode received information
      r, g, b = data[fixture*DMX_BYTES_PER_SEGMENT:(fixture+1)*DMX_BYTES_PER_SEGMENT]
      # change led colour based on that
      for pixel in range(fixture*leds_per_segment, (fixture+1)*leds_per_segment):
        strip.setPixelColor(pixel, Color(r, g, b))
    except ValueError:
      cancel_draw(data)
      return
    print('CH: ', fixture, ', R: ', r, ', G: ', g, ', B: ', b)

  print('Finished message receive, start drawing ...')
  # Draw to all LEDs
  strip.show()
  print('Finished drawing.')

if __name__ == '__main__':
  # Show colour on startup
  draw([15, 15, 125])

  # Register DMX universe
  wrapper = ClientWrapper()
  client = wrapper.Client()
  client.RegisterUniverse(DMX_UNIVERSE, client.REGISTER, draw)
  wrapper.Run()

  # Turn off on shutdown
  draw([0, 0, 0])

  print('Exiting.')