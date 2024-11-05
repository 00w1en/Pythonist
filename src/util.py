import ctypes

LONG = ctypes.c_long
WORD = ctypes.c_ushort
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(DWORD)

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

VK_BACK = 0x08
VK_LSHIFT = 0xA0

KEY_0 = 0x30
KEY_1 = 0x31
KEY_2 = 0x32
KEY_3 = 0x33
KEY_4 = 0x34
KEY_5 = 0x35
KEY_6 = 0x36
KEY_7 = 0x37
KEY_8 = 0x38
KEY_9 = 0x39
KEY_A = 0x41
KEY_B = 0x42
KEY_C = 0x43
KEY_D = 0x44
KEY_E = 0x45
KEY_F = 0x46
KEY_G = 0x47
KEY_H = 0x48
KEY_I = 0x49
KEY_J = 0x4A
KEY_K = 0x4B
KEY_L = 0x4C
KEY_M = 0x4D
KEY_N = 0x4E
KEY_O = 0x4F
KEY_P = 0x50
KEY_Q = 0x51
KEY_R = 0x52
KEY_S = 0x53
KEY_T = 0x54
KEY_U = 0x55
KEY_V = 0x56
KEY_W = 0x57
KEY_X = 0x58
KEY_Y = 0x59
KEY_Z = 0x5A

BLACK_KEYS = (1, 3, 6, 8, 10)
NOTES = {
    36: KEY_1,  # C2 
    37: KEY_1,  # C#2
    38: KEY_2,  # D2
    39: KEY_2,  # D#2
    40: KEY_3,  # E2
    41: KEY_4,  # F2
    42: KEY_4,  # F#2
    43: KEY_5,  # G2
    44: KEY_5,  # G#2
    45: KEY_6,  # A2
    46: KEY_6,  # A#2
    47: KEY_7,  # B2
    48: KEY_8,  # C3
    49: KEY_8,  # C#3
    50: KEY_9,  # D3
    51: KEY_9,  # D#3
    52: KEY_0,  # E3
    53: KEY_Q,  # F3
    54: KEY_Q,  # F#3
    55: KEY_W,  # G3
    56: KEY_W,  # G#3
    57: KEY_E,  # A3
    58: KEY_E,  # A#3
    59: KEY_R,  # B3
    60: KEY_T,  # C4
    61: KEY_T,  # C#4
    62: KEY_Y,  # D4
    63: KEY_Y,  # D#4
    64: KEY_U,  # E4
    65: KEY_I,  # F4
    66: KEY_I,  # F#4
    67: KEY_O,  # G4
    68: KEY_O,  # G#4
    69: KEY_P,  # A4
    70: KEY_P,  # A#4
    71: KEY_A,  # B4
    72: KEY_S,  # C5
    73: KEY_S,  # C#5
    74: KEY_D,  # D5
    75: KEY_D,  # D#5
    76: KEY_F,  # E5
    77: KEY_G,  # F5
    78: KEY_G,  # F#5
    79: KEY_H,  # G5
    80: KEY_H,  # G#5
    81: KEY_J,  # A5
    82: KEY_J,  # A#5
    83: KEY_K,  # B5
    84: KEY_L,  # C6
    85: KEY_L,  # C#6
    86: KEY_Z,  # D6
    87: KEY_Z,  # D#6
    88: KEY_X,  # E6
    89: KEY_C,  # F6
    90: KEY_C,  # F#6
    91: KEY_V,  # G6
    92: KEY_V,  # G#6
    93: KEY_B,  # A6
    94: KEY_B,  # A#6
    95: KEY_N,  # B6
    96: KEY_M,  # C7
}

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', LONG),
                ('dy', LONG),
                ('mouseData', DWORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))
                
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', WORD),
                ('wScan', WORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))
                
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', DWORD),
                ('wParamL', WORD),
                ('wParamH', WORD))
                
class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))
                
class INPUT(ctypes.Structure):
    _fields_ = (('type', DWORD),
                ('union', _INPUTunion))
                
def SendInput(*inputs):
    cInputs = len(inputs)
    LPINPUT = INPUT * cInputs  # INPUT LPINPUT[cInputs]
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return ctypes.windll.user32.SendInput(cInputs, pInputs, cbSize)
    
def Keyboard(code, flags=0):
    return INPUT(INPUT_KEYBOARD, _INPUTunion(ki=KEYBDINPUT(code, 0, flags, 0, None)))

def IsKeyPressed(code):
    return (ctypes.windll.user32.GetAsyncKeyState(code) & 0x8000)

def TurnON(pitch: int) -> None:
    if (pitch % 12) in BLACK_KEYS:
        SendInput(Keyboard(VK_LSHIFT))
    SendInput(Keyboard(NOTES[pitch]))

def TurnOFF(pitch: int) -> None:
    if (pitch % 12) in BLACK_KEYS:
        SendInput(Keyboard(VK_LSHIFT, KEYEVENTF_KEYUP))
    SendInput(Keyboard(NOTES[pitch], KEYEVENTF_KEYUP))

def ReadValue(data) -> int:
    byte = 0x80
    value = next(data)

    # Check MSB, if set, more bytes need reading
    if (value & 0x80):
        value &= 0x7F  # Mask out the MSB
        while (byte & 0x80):
            byte = next(data)
            value = (value << 7) | (byte & 0x7F)  # Shift left and add the next 7 bits

    # Return final construction
    return value
