from pydub import AudioSegment
from pydub.playback import play
from typing import cast, Callable
import random
import asyncio
import board
import neopixel

# Configuration
LEDS = 17
LED_PIN = board.D21
ORDER = neopixel.GRB
BRIGHTNESS = 0.1  # Adjust as needed (0.0 to 1.0)

GREEN = (0, 255, 0)
YELLOW = (255, 100, 0)
RED = (255, 0, 0)
OFF = (0, 0, 0)

# Initialize NeoPixel Strip
strip = neopixel.NeoPixel(
    LED_PIN, # type: ignore
    LEDS,
    brightness=BRIGHTNESS,
    auto_write=False,
    pixel_order=ORDER
)

def set_green():
    for i in range(0, 4):  # LEDs 0 to 4 inclusive
        strip[i] = GREEN
    strip.show()

def set_yellow():
    for i in range(4,8):  # LEDs 5 to 8 inclusive
        strip[i] = YELLOW
    strip.show()

def set_red():
    for i in range(8,12):  # LEDs 9 to 12 inclusive
        strip[i] = RED
    strip.show()

def clear_leds():
    strip.fill(OFF)
    strip.show()

def set_colors():
    set_green()
    set_yellow()
    set_red()


def speedup(sound: AudioSegment, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


def split_song_into_steps(segments: list[AudioSegment]):
    n = 5
    result: list[list[AudioSegment]] = []
    for segment in segments:
        length = len(segment)
        base = length // n
        remainder = length % n
        steps: list[AudioSegment] = []
        for i in range(n):
            start = i*base
            end = (i+1) * base + (remainder if i == (n-1) else 0)
            step = cast(AudioSegment, segment[start:end])
            step = speedup(step, 1.0 + 0.1 * i)
            steps.append(step)
        result.append(steps)
    return result


def get_segments(song: AudioSegment) -> list[AudioSegment]:
    remaining_duration = len(song)
    first = random.randint(remaining_duration // 4, remaining_duration // 3)
    remaining_duration -= first
    second = random.randint(remaining_duration // 4, remaining_duration // 2)
    remaining_duration -= second
    first_segment = cast(AudioSegment, song[:first])
    second_segment = cast(AudioSegment, song[first:second+first])
    third_segment = cast(AudioSegment, song[second+first:])
    return [first_segment, second_segment,third_segment]

def concatenate_steps(steps: list[list[AudioSegment]]) -> AudioSegment:
    full_audio = AudioSegment.empty()
    for segment in steps:
        for step in segment:
            full_audio += step
    return full_audio

async def blink_led(speed: float, duration: float, led_function: Callable):
    end_time = asyncio.get_event_loop().time() + duration/1000
    interval = 1.0/speed
    last_time = asyncio.get_event_loop().time()
    led_function()
    is_on = True
    while True:
        current_time = asyncio.get_event_loop().time()
        if current_time >= end_time:
            clear_leds()
            return
        if current_time > last_time + interval:
            if is_on:
                clear_leds()
                is_on = False
            else:
                led_function()
                is_on = True
            last_time = current_time


async def control_leds(segments: list[list[AudioSegment]]):
    base_speed = 1.0
    color_functions = [set_green, set_yellow, set_red]
    random.shuffle(color_functions)
    for i,segment in enumerate(segments):
        color_function = color_functions[i]
        led_speed = base_speed
        for step in segment:
            duration = len(step)
            await blink_led(led_speed, duration, color_function)
            led_speed += 1
        base_speed = 1.0


async def main():
    sound_file: AudioSegment = AudioSegment.from_wav('theme.wav')
    segments = get_segments(sound_file)
    stepped_segments: list[list[AudioSegment]] = split_song_into_steps(segments)
    full_audio = concatenate_steps(stepped_segments)
    await asyncio.gather(
        asyncio.to_thread(play, full_audio),
        control_leds(stepped_segments)
    )

if __name__ == "__main__":
    asyncio.run(main())
