from pydub import AudioSegment
from pydub.playback import play
from typing import cast
import random
import asyncio

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

async def blink_led(speed: float, duration: float):
    end_time = asyncio.get_event_loop().time() + duration/1000
    interval = 1.0/speed
    last_time = asyncio.get_event_loop().time()
    print("ON")
    is_on = True
    while True:
        current_time = asyncio.get_event_loop().time()
        if current_time >= end_time:
            print("OFF, this section is stopped")
            return
        if current_time > last_time + interval:
            if is_on:
                print("OFF")
                is_on = False
            else:
                print("ON")
                is_on = True
            last_time = current_time


async def control_leds(segments: list[list[AudioSegment]]):
    base_speed = 1.0
    for segment in segments:
        led_speed = base_speed
        for step in segment:
            duration = len(step)
            await blink_led(led_speed, duration)
            led_speed += 0.5
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
