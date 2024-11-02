import time
from midi import Midi
from util import TurnON, TurnOFF

if __name__ == "__main__":
    time.sleep(3)
    midi = Midi()
    midi.parse_file("blacktrain.mid")

    notes = midi.get_notes()
    
    current_time = 0
    active_notes = {}

    for note in notes:
        status, start_time, data = note
        pitch, velocity = data
        if not (36 <= pitch <= 96):
            continue

        delay = start_time - current_time
        current_time = start_time

        time.sleep(midi.tempo/1000000/midi.resolution*delay)

        if status == 0x90:
            if velocity == 0:
                if pitch in active_notes:
                    TurnOFF(pitch)
                    del active_notes[pitch]
            else:
                if pitch in active_notes:
                    TurnOFF(pitch)
                TurnON(pitch)
                active_notes[pitch] = current_time
        else:
            if pitch in active_notes:
                TurnOFF(pitch)
                del active_notes[pitch]
