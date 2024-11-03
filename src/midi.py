from struct import unpack
from util import ReadValue

# MIDI Event Types
NOTE_OFF = 0x80
NOTE_ON = 0x90
KEY_PRESSURE = 0xA0
CONTROL_CHANGE = 0xB0
PROGRAM_CHANGE = 0xC0
CHANNEL_PRESSURE = 0xD0
PITCH_BEND = 0xE0
SYSTEM_EXCLUSIVE_START = 0xF0
SYSTEM_EXCLUSIVE_END = 0xF7

# Meta Event Types
META_EVENT = 0xFF
SEQUENCE_NUMBER = 0x00
TEXT_EVENT = 0x01
COPYRIGHT_NOTICE = 0x02
TRACK_NAME = 0x03
INSTRUMENT_NAME = 0x04
LYRICS = 0x05
MARKER = 0x06
CUE_POINT = 0x07
MIDI_CHANNEL_PREFIX = 0x20
MIDI_PORT = 0x21
END_OF_TRACK = 0x2F
TEMPO_CHANGE = 0x51
SMPTE_OFFSET = 0x54
TIME_SIGNATURE = 0x58
KEY_SIGNATURE = 0x59
SEQUENCER_SPECIFIC = 0x7F

# Event Lengths (in bytes) for each MIDI Event Type
EVENTS = {NOTE_OFF: 2, NOTE_ON: 2, KEY_PRESSURE: 2, CONTROL_CHANGE: 2, PROGRAM_CHANGE: 1, CHANNEL_PRESSURE: 1, PITCH_BEND: 2}
META_EVENTS = (SEQUENCE_NUMBER, TEXT_EVENT, COPYRIGHT_NOTICE, TRACK_NAME, INSTRUMENT_NAME, LYRICS, MARKER, CUE_POINT, MIDI_CHANNEL_PREFIX, MIDI_PORT, END_OF_TRACK, TEMPO_CHANGE, SMPTE_OFFSET, TIME_SIGNATURE, KEY_SIGNATURE, SEQUENCER_SPECIFIC)

class Event(object):
    def __init__(self, status: int = META_EVENT, tick: int = 0, length: int = 1, data: list = []) -> None:
        self.length = length
        self.status = status
        self.tick = tick
        self.data = data

class Midi(object):
    def __init__(self) -> None:
        self.tempo = 0
        self.tracks = []     # List to store MIDI track data
        self.resolution = 0  # Time resolution in ticks per quarter note 

    def parse_file(self, filepath: str) -> None:
        file = open(filepath, "rb")

        # Read MIDI Header
        fileid = file.read(4)  # Read the file identifier
        if fileid != b'MThd':  # Verify that the file is a valid MIDI file
            file.close()
            raise TypeError("Bad header in MIDI file.")

        # Unpack header data: header size, format, number of tracks, resolution 
        data = unpack(">lhhh", file.read(10))
        self.resolution = data[3]  # Ticks per quarter note 

        print("[+] Header size:", data[0])
        print("[+] Format:", data[1])
        print("[+] Tracks:", data[2])
        print("[+] Parts Per Quarter:", data[3])

        tracks = []
        for _ in range(data[2]):
            print("[+] NEW TRACK")
            trackid = file.read(4)  # Read track identifier
            if trackid != b'MTrk':  # Verify track header
                file.close()
                raise TypeError("Bad track header in MIDI file.")

            trksz = unpack(">l", file.read(4))[0]
            print("[+] Track size:", trksz)

            tracks.append(iter(file.read(trksz)))

        file.close()

        for trackdata in tracks:
            self.tracks.append(self.parse_track(trackdata))

    def parse_track(self, trackdata) -> list:
        track = []  # Initialize a new list for track events
        prevsts = 0
        trackend = False

        while not trackend:
            data = []
            tick = ReadValue(trackdata)  # Read delta time
            status = next(trackdata)     # Read event status byte
            event = Event(status=status, tick=tick)

            # Process Meta Event 
            if event.status == META_EVENT:
                msgtype = next(trackdata)
                if msgtype not in META_EVENTS:
                    print("Unknown Meta MIDI Event:", msgtype)
                else:
                    event.length = ReadValue(trackdata)
                    data = [next(trackdata) for _ in range(event.length)]
                    if msgtype == END_OF_TRACK:
                        trackend = True
                    elif msgtype == TEMPO_CHANGE and self.tempo == 0:
                        self.tempo |= (data[0] << 16)
                        self.tempo |= (data[1] << 8)
                        self.tempo |= (data[2] << 0)
                        bpm = (60000000 / self.tempo)
                        print("Tempo:", self.tempo, "(", bpm, "bpm)")

            # Process System Exclusive Event
            elif event.status == SYSTEM_EXCLUSIVE_START:
                while True:
                    datum = next(trackdata)
                    if datum == SYSTEM_EXCLUSIVE_END:
                        break
                    data.append(datum)

            # Process MIDI Event
            else:
                # Check for Running Status
                if (event.status < NOTE_OFF):
                    data.append(event.status)
                    event.status = prevsts
                    event.length = EVENTS[prevsts] - 1
                else:
                    event.length = EVENTS[(event.status & 0xF0)]

                data += [next(trackdata) for _ in range(event.length)]

                event.status &= 0xF0
                prevsts = event.status

            event.data = data
            track.append(event)

        return track

    def get_notes(self) -> list:
        notes = []
        for track in self.tracks:
            absolute_time = 0
            for event in track:
                absolute_time += event.tick
                if event.status in (NOTE_OFF, NOTE_ON):
                    notes.append((event.status, absolute_time, event.data))

        notes.sort(key=lambda note: note[1])
        return notes
