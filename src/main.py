import time, util
from midi import Midi

if __name__ == "__main__":
    filepath = input("MIDI file path: ")
    delay = float(input("Start delay time: "))

    midi = Midi()
    midi.parse_file(filepath)
    time.sleep(delay)

    notes = midi.get_notes()
    
    current_time = 0
    active_notes = {}

    for note in notes:
        if util.IsKeyPressed(util.VK_BACK):
            break

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
                    util.TurnOFF(pitch)
                    del active_notes[pitch]
            else:
                if pitch in active_notes:
                    util.TurnOFF(pitch)
                util.TurnON(pitch)
                active_notes[pitch] = current_time
        else:
            if pitch in active_notes:
                util.TurnOFF(pitch)
                del active_notes[pitch]

    if util.IsKeyPressed(util.VK_LSHIFT):
        util.SendInput(util.Keyboard(util.VK_LSHIFT, util.KEYEVENTF_KEYUP))
