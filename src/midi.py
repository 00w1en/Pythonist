from struct import unpack
from util import ReadValue

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

        # Loop through each track 
        for track in range(data[2]):
            print("[+] NEW TRACK")
            trackid = file.read(4)  # Read track identifier
            if trackid != b'MTrk':  # Verify track header
                file.close()
                raise TypeError("Bad track header in MIDI file.")

            # Track size 
            trksz = unpack(">l", file.read(4))[0]
            print("[+] Track size:", trksz)

            trackend = False
            self.tracks.append([])  # Initialize a new list for track events

            # Process track events until the end of the track
            while not trackend:
                data = []
                tick = ReadValue(file)    # Read delta time
                status = file.read(1)[0]  # Read event status byte

                # Check for Running Status
                if (status < 0x80):
                    status = self.tracks[track][-1][0]  # Use the last status byte
                    file.seek(-1, 1)                    # Rewind one byte

                if ((status & 0xF0) == 0x80):    # Note Off event 
                    pitch = file.read(1)[0]
                    velocity = file.read(1)[0]
                    data.extend([pitch, velocity])
                elif ((status & 0xF0) == 0x90):  # Note On event
                    pitch = file.read(1)[0]
                    velocity = file.read(1)[0]
                    data.extend([pitch, velocity])
                elif ((status & 0xF0) == 0xA0):  # Key Pressure event
                    pitch = file.read(1)[0]
                    velocity = file.read(1)[0]
                    data.extend([pitch, velocity])
                elif ((status & 0xF0) == 0xB0):  # Control Change event
                    control = file.read(1)[0]
                    value = file.read(1)[0]
                    data.extend([control, value])
                elif ((status & 0xF0) == 0xC0):  # Program Change event
                    program = file.read(1)[0]
                    data.append(program)
                elif ((status & 0xF0) == 0xD0):  # Channel Pressure event
                    channelpressure = file.read(1)[0]
                    data.append(channelpressure)
                elif ((status & 0xF0) == 0xE0):  # Pitch Bend event
                    LS7B = file.read(1)[0]
                    MS7B = file.read(1)[0]
                    data.extend([LS7B, MS7B])
                elif ((status & 0xF0) == 0xF0):  # Meta and System Exclusive events
                    if (status == 0xFF):           # Meta Event
                        msgtype = file.read(1)[0]  # Meta event type
                        msglen = ReadValue(file)   # Meta event data length

                        if msgtype == 0x00:
                            print("Sequence Number:", file.read(1), file.read(1))
                        elif msgtype == 0x01:
                            print("Text:", file.read(msglen))
                        elif msgtype == 0x02:
                            print("Copyright:", file.read(msglen))
                        elif msgtype == 0x03:
                            print("Track Name:", file.read(msglen))
                        elif msgtype == 0x04:
                            print("Instrument Name:", file.read(msglen))
                        elif msgtype == 0x05:
                            print("Lyrics:", file.read(msglen))
                        elif msgtype == 0x06:
                            print("Marker:", file.read(msglen))
                        elif msgtype == 0x07:
                            print("Cue:", file.read(msglen))
                        elif msgtype == 0x20:
                            print("Prefix:", file.read(1))
                        elif msgtype == 0x21:
                            print("Prefix port:", file.read(1))
                        elif msgtype == 0x2F:  # End of Track event
                            trackend = True
                        elif msgtype == 0x51:  # Tempo event
                            if (self.tempo == 0):
                                self.tempo |= (file.read(1)[0] << 16)
                                self.tempo |= (file.read(1)[0] << 8)
                                self.tempo |= (file.read(1)[0] << 0)
                                bpm = (60000000 / self.tempo)
                                print("Tempo:", self.tempo, "(", bpm, "bpm)")
                            else:
                                tempo = 0
                                tempo |= (file.read(1)[0] << 16)
                                tempo |= (file.read(1)[0] << 8)
                                tempo |= (file.read(1)[0] << 0)
                                bpm = (60000000 / tempo)
                                print("Tempo:", tempo, "(", bpm, "bpm)")
                        elif msgtype == 0x54:
                            print("SMPTE: H:", file.read(1), "M:", file.read(1), "S:", file.read(1), "FR:", file.read(1), "FF:", file.read(1))
                        elif msgtype == 0x58:
                            print("Time Signature:", file.read(1), "/", (2 << file.read(1)[0]))
                            print("ClocksPerTick:", file.read(1))
                            print("32per24Clocks:", file.read(1))
                        elif msgtype == 0x59:
                            print("Key Signature:", file.read(1))
                            print("Minor Key:", file.read(1))
                        elif msgtype == 0x7F:
                            print("Sequencer Specific:", file.read(msglen))
                        else:
                            print("Unrecognised MetaEvent:", msgtype)
                    if (status == 0xF0):  # System Exclusive Begin
                        print("System Exclusive Begin:", file.read(ReadValue(file)))
                    if (status == 0xF7):  # System Exclusive End
                        print("System Exclusive End:", file.read(ReadValue(file)))
                else:
                    print("Unrecognised Status Byte:", status)

                # Append event (status, tick, data) to the track list
                self.tracks[track].append(((status & 0xF0), tick, data))

        file.close()

    def get_notes(self) -> list:
        notes = []
        for track in self.tracks:
            absolute_time = 0
            for event in track:
                status, tick, data = event
                absolute_time += tick
                if status in (0x80, 0x90):
                    notes.append((status, absolute_time, data))

        notes.sort(key=lambda note: note[1])
        return notes
