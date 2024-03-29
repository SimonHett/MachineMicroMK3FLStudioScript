    # name=Maschine MK3

import arrangement
import channels
import chordsets as cs
import device
import general
import midi
import mixer
import patterns
import plugins
import transport
import ui

from midi import *

MIDI_PORT = 0 # used for selecting what MIDI IN PORT plugins should have for communicating with the script
MIDI_PORT_SERUM = 1 # used for selecting what MIDI IN PORT Serum should have in order to change presets
SERUM_PRESET_PREV_CC = 22 # look for serum.cfg file on your computer, in it you can specify
SERUM_PRESET_NEXT_CC = 23 # what midi cc controls change presets, set it to these numbers

# Maschine indexed colors from controller editor manual
Black0 = 0
Black1 = 1
Black2 = 2
Black3 = 3
Red0 = 4
Red1 = 5
Red2 = 6
Red3 = 7
Orange0 = 8
Orange1 = 9
Orange2 = 10
Orange3 = 11
LightOrange0 = 12
LightOrange1 = 13
LightOrange2 = 14
LightOrange3 = 15
WarmYellow0 = 16
WarmYellow1 = 17
WarmYellow2 = 18
WarmYellow3 = 19
Yellow0 = 20
Yellow1 = 21
Yellow2 = 22
Yellow3 = 23
Lime0 = 24
Lime1 = 25
Lime2 = 26
Lime3 = 27
Green0 = 28
Green1 = 29
Green2 = 30
Green3 = 31
Mint0 = 32
Mint1 = 33
Mint2 = 34
Mint3 = 35
Cyan0 = 36
Cyan1 = 37
Cyan2 = 38
Cyan3 = 39
Turquoise0 = 40
Turquoise1 = 41
Turquoise2 = 42
Turquoise3 = 43
Blue0 = 44
Blue1 = 45
Blue2 = 46
Blue3 = 47
Plum0 = 48
Plum1 = 49
Plum2 = 50
Plum3 = 51
Violet0 = 52
Violet1 = 53
Violet2 = 54
Violet3 = 55
Purple0 = 56
Purple1 = 57
Purple2 = 58
Purple3 = 59
Magenta0 = 60
Magenta1 = 61
Magenta2 = 62
Magenta3 = 63
Fuchsia0 = 64
Fuchsia1 = 65
Fuchsia2 = 66
Fuchsia3 = 67
White0 = 68
White1 = 69
White2 = 70
White3 = 71

# Plugin and channel color in OMNI/PAD mode, feel free to change these with any others from the list

ChannelCoding = {
    0:  {"name": "Sampler",     "color": Green0,    "highlight": Green2},
    1:  {"name": "Hybrid",      "color": Blue1,     "highlight": Blue2},
    2:  {"name": "GenPlug",     "color": Violet1,   "highlight": Violet2},
    3:  {"name": "Layer",       "color": Mint1,     "highlight": Mint2},
    4:  {"name": "AudioClip",   "color": Magenta1,  "highlight": Magenta3},
    5:  {"name": "AutoClip",    "color": Fuchsia0,  "highlight": Fuchsia2},
    6:  {"name": "StepSeq",     "color": Black0,    "highlight": Purple3},
}

CHORDS_COLOR = Cyan2
CHORDS_HIGHLIGHTED = Cyan3
KEYBOARD_COLOR = Mint2
KEYBOARD_HIGHLIGHTED = Mint3

# reverse engineered codes for channel rack colors
WHITE = -1
RED = -4892325
YELLOW = -4872871
GREEN = -4872871
ORANGE = -4872871
DEFAULT = -12037802
BLUE = -13619057

# modes for the pads
OMNI = 0
KEYBOARD = 1
CHORDS = 2
STEP = 3

# modes for layer mode
NONE = 0
PAGE = 1
OPTION = 2
PATTERN = 3

# modes for 4D encoder
JOG = 0
VOLUME = 1
SWING = 2
TEMPO = 3

class MessageBuffer:
    def __init__(self, size):
        self.size = size
        self.data = []
    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.size
        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.size:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = self.__Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data


class Controller:
    def __init__(self):
        self.touch_strip = 0
        self.current_octave = 0
        self.current_offset = 0
        self.last_triggered = []
        self.encoder = 0
        self.active_chordset = 0
        self.current_group = cs.groups[0]
        self.scale = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
        self.program = 0
        self.padmode = OMNI
        self.overlaymode = NONE
        self.mute = 0
        self.channels = 0
        self.stepchannel = 0
        self.fixedvelocity = 0
        self.fixedvelocityvalue = 100
        self.safe_notes = []
        self.selected_track = 0
        self.mixer_snap = 0
        self.plugin_picker_active = 0
        self.msgbuffer = MessageBuffer(16)
        self.highlightcode = {
            0:      Black0,
            1:      Green2,
            2:      Yellow2,
            3:      Red2,
        }


    def update_maschine_touch_strip(self, data1, state):  # toggles LEDs between pitch, mod, perform and notes buttons
        for button in range(49, 53):
            if data1 != button:
                device.midiOutMsg(176, 0, button, 0)
            else:
                device.midiOutMsg(176, 0, button, state)

    def update_maschine_encoder(selfself, data1, state):  # toggles LEDs between volume, swing and tempo
        for button in range(44, 47):
            if data1 != button:
                device.midiOutMsg(176, 0, button, 0)
            else:
                device.midiOutMsg(176, 0, button, state)

    def note_off(self):
        if self.last_triggered != []:
            for note in range(0, 128):
                channels.midiNoteOn(channels.selectedChannel(), note, 0)
            for note in self.last_triggered:
                self.last_triggered.remove(note)
            return
        else:
            return


controller = Controller()

def update_led_state():
    if transport.isPlaying():
        device.midiOutMsg(176, 0, 57, 127)
    else:
        device.midiOutMsg(176, 0, 57, 0)
    if transport.isRecording():
        device.midiOutMsg(176, 0, 58, 127)
    else:
        device.midiOutMsg(176, 0, 58, 0)
    if ui.getVisible(midi.widBrowser):
        device.midiOutMsg(176, 0, 39, 127)
    else:
        device.midiOutMsg(176, 0, 39, 0)
    if ui.getVisible(midi.widMixer):
        device.midiOutMsg(176, 0, 37, 127)
    else:
        device.midiOutMsg(176, 0, 37, 0)
    if ui.getVisible(widPlaylist):
        device.midiOutMsg(176, 0, 36, 127)
    else:
        device.midiOutMsg(176, 0, 36, 0)
    if ui.getVisible(midi.widChannelRack):
        device.midiOutMsg(176, 0, 19, 127)
    else:
        device.midiOutMsg(176, 0, 19, 0)
    if ui.isMetronomeEnabled():
        device.midiOutMsg(176, 0, 56, 127)
    else:
        device.midiOutMsg(176, 0, 56, 0)
    if transport.isPlaying():
        device.midiOutMsg(176, 0, 59, 0)
    else:
        device.midiOutMsg(176, 0, 59, 127)
    if transport.getLoopMode():
        device.midiOutMsg(176, 0, 53, 127)
    else:
        device.midiOutMsg(176, 0, 53, 0)
    if ui.getSnapMode() == 3:
        device.midiOutMsg(176, 0, 48, 0)
    else:
        device.midiOutMsg(176, 0, 48, 127)

def update_mixer_track():
    # update track num
    device.midiOutMsg(176, 0, 70, mixer.trackNumber())
    return

def update_mixer_values():
    # update volume
    converted_volume = round(mixer.getTrackVolume(mixer.trackNumber()) * 125)
    device.midiOutMsg(176, 0, 71, converted_volume)
    # update panning
    converted_pan = round((mixer.getTrackPan(mixer.trackNumber()) * 63) + 63)
    device.midiOutMsg(176, 0, 72, converted_pan)
    # update stereo separation
    ssindex = midi.REC_Mixer_SS + mixer.getTrackPluginId(mixer.trackNumber(), 0)
    ssvalue = general.processRECEvent(ssindex, 1, midi.REC_GetValue) + 63
    device.midiOutMsg(176, 0, 73, ssvalue)
    return

def refresh_channels():
    if channels.channelCount() < controller.channels * 16:  #when changing filter group results in less channels than controller channels set
        controller.channels = channels.channelCount() // 16
    lower_channel = controller.channels * 16
    channelCount = channels.channelCount()
    for channel in range(16):
        if lower_channel + channel < channelCount:
            channeltype = channels.getChannelType(lower_channel + channel)
            color = ChannelCoding[channeltype]['highlight'] if (lower_channel + channel) == channels.selectedChannel() else ChannelCoding[channeltype]['color']
        else:
            color = Black0        
        device.midiOutMsg(144, 0, channel, color)

def refresh_selected_page():
    if controller.padmode == OMNI:
        refresh_channels()
    elif controller.padmode == CHORDS:
        refresh_chords()
    elif controller.padmode == KEYBOARD:
        refresh_keyboard()
    elif controller.padmode == STEP:
        refresh_grid()

def refresh_selector():
    selected_index = 0
    maximum_selection = 16
    if controller.padmode == OMNI:
        selected_index = controller.channels
        maximum_selection = ((channels.channelCount()-1) // 16) + 1
    elif controller.padmode == KEYBOARD:        
        selected_index = cs.groups.index(controller.current_group)  
        maximum_selection = len(cs.groups)        
    elif controller.padmode == CHORDS:
        selected_index = controller.active_chordset
        maximum_selection = len(cs.chdSet)
    elif controller.padmode == STEP:
        selected_index = controller.stepchannel
    for channel in range(16):
        color = Orange3 if channel == selected_index else Orange1
        color = Black0 if channel >= maximum_selection else color
        device.midiOutMsg(144, 0, channel, color)

def refresh_patterns():
    for pattern in range(0, 16):
        color = Lime1 if pattern < patterns.patternCount() else Black0
        color = Lime2 if patterns.isPatternSelected(pattern + 1) else color
        color = Lime3 if pattern == patterns.patternCount() else color
        device.midiOutMsg(144, 0, pattern, color)

def refresh_options():
    #Octave Buttons
    button_id_on  = 14 if controller.current_octave < 0 else 15
    button_id_off = 15 if controller.current_octave < 0 else 14              
    device.midiOutMsg(144, 0, button_id_on, controller.highlightcode[abs(controller.current_octave)])
    device.midiOutMsg(144, 0, button_id_off, Black0)
    #Semitone Buttons
    button_id_on  = 12 if controller.current_offset < 0 else 13
    button_id_off = 13 if controller.current_offset < 0 else 12              
    device.midiOutMsg(144, 0, button_id_on, 2 + abs(controller.current_offset*4))
    device.midiOutMsg(144, 0, button_id_off, Black0)  
    #Shortcut Buttons
    for button in range(12):
        device.midiOutMsg(144, 0, button, White1)  

def refresh_keyboard():
    for channel in range(16):
        device.midiOutMsg(144, 0, channel, KEYBOARD_COLOR)

def refresh_chords():
    for channel in range(16):
        device.midiOutMsg(144, 0, channel, CHORDS_COLOR)

def refresh_chan_screen():
    try:
        # refresh channel number
        device.midiOutMsg(176, 0, 74, channels.selectedChannel())
        # refresh offset volume
        id = midi.REC_Chan_OfsVol + channels.getRecEventId(channels.selectedChannel())
        value = channels.processRECEvent(id, 0, midi.REC_GetValue)
        device.midiOutMsg(176, 0, 75, round((value/25600) * 127) - 1)
        # refresh offset modx
        id = midi.REC_Chan_OfsFCut + channels.getRecEventId(channels.selectedChannel())
        value = general.processRECEvent(id, 0, midi.REC_GetValue)
        if -12 < value < 12:
            value = 0
        #print(value)
        device.midiOutMsg(176, 0, 76, round(((value + 256) / 512) * 127) - 1)
    except Exception as ex:
        print("exception: " + str(ex))
    return

def refresh_grid():
    lower_grid = controller.stepchannel * 16
    for gridbit in range(lower_grid, lower_grid + 16):
        color = 'color' if channels.getGridBit(channels.selectedChannel(), gridbit) == 0 else 'highlight'        
        device.midiOutMsg(144, 0, gridbit - lower_grid, ChannelCoding[6][color])
    return

def init_leds():
    print('init leds')
    for button in range(0, 127):
        device.midiOutMsg(176, 0, button, Black0)
    for note in range(0, 127):
        device.midiOutMsg(144, 0, note, Black0)
    device.midiOutMsg(176, 0, 3, int(transport.getSongPos() * 127))
    device.midiOutMsg(176, 0, 100, White1)
    device.midiOutMsg(176, 0, 30, Green0)
    device.midiOutMsg(176, 0, 31, Green0)
    device.midiOutMsg(176, 0, 33, Green0)
    device.midiOutMsg(176, 0, 34, Green0)
    device.midiOutMsg(176, 0, 35, 0)
    device.midiOutMsg(176, 0, 81, 127)
    device.midiOutMsg(176, 0, 77, 100)
    refresh_channels()
    refresh_chan_screen()
    return

def hex_it(data):
    if data:
        return data.hex()
    else:
        return "None"

def hex_string(string):
    s = string.encode('utf-8')
    hex_value = s.hex()
    return hex_value


def print_midi_info(event):  # quick code to see info about particular midi control (check format function in python)
    print("status: {}, channel: {}, note: {}, data1: {}, data2: {},, sysex: {}".format(event.status, event.midiChan,
                                                                                       event.note, event.data1,
                                                                                       event.data2,
                                                                                       hex_it(event.sysex)))

def OnInit():
    init_leds()
    update_led_state()
    update_mixer_values()
    refresh_chan_screen()
    refresh_channels()
    update_mixer_track()
    return

def OnDeInit():
    print("On Init:")
    for button in range(0, 127):
        device.midiOutMsg(176, 0, button, Black0)
    for note in range(0, 127):
        device.midiOutMsg(144, 0, note, Black0)
    return

def OnRefresh(flag):
    #print("Refresh Flag:" + str(flag))
    if flag == 256: # DIRTY LEDs
        update_led_state()
        return
    if flag == 263: # selecting mixer tracks
        update_mixer_track()
        return
    if flag == 4: # DIRTY MIXER CONTROLS
        if not controller.plugin_picker_active:
            update_mixer_values()
        return
    if flag == 260: # MAIN RECORDING FLAG
        if transport.isRecording():
            device.midiOutMsg(176, 0, 58, 127)
        else:
            device.midiOutMsg(176, 0, 58, 0)
        return
    if flag == 359 or flag == 375: # LOADING NEW CHANNELS (PLUGINS OR SAMPLES)
        if controller.padmode == OMNI:
            refresh_channels()            
            if not controller.plugin_picker_active:
                refresh_chan_screen()
            return
        elif controller.padmode == STEP: # LOADING NEW CHANNELS (PLUGINS OR SAMPLES)
            #refresh_grid()
            if not controller.plugin_picker_active:
                refresh_chan_screen()
            return
    if flag == 288: # CHANGING CHANNELS
        if controller.padmode == OMNI:
            refresh_channels()
        if controller.padmode == STEP:
            refresh_grid()
        if not controller.plugin_picker_active:
            refresh_chan_screen()
        update_led_state()
        return
    if flag == 311 and controller.padmode == OMNI: # DELETING CHANNELS
        #refresh_channels()
        if not controller.plugin_picker_active:
            refresh_chan_screen()
        return
    # if flag == 1024 or flag == 1056 or flag == 1280 and controller.padmode == STEP: # changing steps
    #     refresh_channels()
    if flag == 295:
        if not controller.plugin_picker_active:
            refresh_chan_screen()
        update_led_state()
        return
    if flag == 32:
        if not controller.plugin_picker_active:
            refresh_chan_screen()
        update_led_state()
        return
    if flag in [98560, 32768] and controller.padmode == OMNI:
        refresh_channels()
        return

def OnMidiIn(event):
    return


def OnMidiMsg(event):  # same as above, but executes after OnMidiIn
    return

def OnProgramChange(event): # status = 192, event.data1 = value, data2 = 0, port is from midi options!
    return

def OnControlChange(event):
    # --------------------------------------------------------------------------------------------------------
    #   TOUCH STRIP
    # --------------------------------------------------------------------------------------------------------
    if event.data1 == 49: # letting touch strip handle pitch
        if controller.touch_strip != 1:
            controller.touch_strip = 1
            device.midiOutMsg(event.status, 0, 3, 64)
            controller.update_maschine_touch_strip(49, 127)
            event.handled = True
            return
        else:
            controller.touch_strip = 0
            device.midiOutMsg(event.status, 0, 3, int(transport.getSongPos() * 127))
            controller.update_maschine_touch_strip(49, 0)
            event.handled = True
            return    
    if event.data1 == 50: # letting touch strip handle modwheel
        if controller.touch_strip != 2:
            controller.touch_strip = 2
            device.midiOutMsg(176, 0, 3, 0)
            controller.update_maschine_touch_strip(50, 127)
            event.handled = True
            return
        else:
            controller.touch_strip = 0
            device.midiOutMsg(event.status, 0, 3, int(transport.getSongPos() * 127))
            controller.update_maschine_touch_strip(50, 0)
            event.handled = True
            return
    if event.data1 == 51: # PERFORM FX
        mixer.linkTrackToChannel(0)
        ui.setHintMsg(channels.getChannelName(channels.selectedChannel()) + " linked to track " + str(mixer.trackNumber()))
        event.handled = True
        return  
    if event.data1 == 52: # NOTES
        transport.globalTransport(FPT_F11, 1)
        event.handled = True
        return   
    if event.data1 == 3: # touch strip coding
        if controller.touch_strip == 1:  # pitch
            channels.setChannelPitch(channels.selectedChannel(), float((event.data2 / 64) - 1))
            device.midiOutMsg(176, 0, 3, event.data2)
            event.handled = True
            return
        elif controller.touch_strip == 2:  # mod, the handled flag is false so its free to assign in FL
            device.midiOutMsg(176, 0, 3, event.data2)
            event.handled = False
            return
        else:
            song_length = transport.getSongLength(midi.SONGLENGTH_BARS)
            updated_position_in_bars = (int((event.data2 / 127) * song_length))
            updated_position = updated_position_in_bars / song_length
            transport.setSongPos(updated_position)
            device.midiOutMsg(176, 0, 3, int(transport.getSongPos() * 127))
            event.handled = True
            return
    if event.data1 == 2:
        if controller.touch_strip == 1:
            channels.setChannelPitch(channels.selectedChannel(), 0)
            device.midiOutMsg(176, 0, 3, 64)
        event.handled = True
        return
    # --------------------------------------------------------------------------------------------------------
    #   TRANSPORT CONTROLS
    # --------------------------------------------------------------------------------------------------------
    if event.data1 == 57:  # PLAY
        transport.start()
        if transport.isPlaying():
            device.midiOutMsg(176, 0, 57, 127)
        else:
            device.midiOutMsg(176, 0, 57, 0)
        event.handled = True
        return
    if event.data1 == 58 and controller.overlaymode == OPTION:
        if ui.isPrecountEnabled():
            transport.globalTransport(midi.FPT_CountDown, 1)
            ui.setHintMsg("Precount disabled")
            event.handled = True
            return
        transport.globalTransport(midi.FPT_CountDown, 1)
        ui.setHintMsg("Precount active")
        event.handled = True
        return
    if event.data1 == 58:  # RECORD
        transport.record()
        event.handled = True
        return
    if event.data1 == 59:  # STOP
        transport.stop()
        event.handled = True
        return
    if event.data1 == 53:  # RESTART
        transport.setLoopMode()
        event.handled = True
        return
    if event.data1 == 54:  # ERASE
        if event.data2 == 0:
            device.midiOutMsg(176, 0, 54, 0)
            event.handled = True
            return
        ui.delete()
        device.midiOutMsg(176, 0, 54, 127)
        event.handled = True
        return
    if event.data1 == 55:  # TAP TEMPO
        if event.data2 == 0:
            device.midiOutMsg(176, 0, 55, 0)
            event.handled = True
            return
        transport.globalTransport(106, 1)
        device.midiOutMsg(176, 0, 55, 127)
        event.handled = True
        return
    if event.data1 == 56: # FOLLOW (METRONOME)
        transport.globalTransport(midi.FPT_Metronome, 1)
        if ui.isMetronomeEnabled():
            device.midiOutMsg(176, 0, 56, 127)
            event.handled = True
            return
        device.midiOutMsg(176, 0, 56, 0)
        event.handled = True
        return
    #----------------------------------------------------------------------------------------------------------------------
    #   MODE PICKER
    #----------------------------------------------------------------------------------------------------------------------
    if event.data1 == 84:  # CHORDS
        for chordset in range(100, 108):
            device.midiOutMsg(176, 0, chordset, 0)
        for mode in range(81, 85):
            device.midiOutMsg(176, 0, mode, 0)
        for note in range(0, 16):
            device.midiOutMsg(144, 0, note, 0)
        controller.padmode = CHORDS
        controller.overlaymode = NONE
        controller.note_off()
        refresh_chords()
        print("Chords:")
        device.midiOutMsg(176, 0, 84, 127)
        device.midiOutMsg(176, 0, controller.active_chordset + 100, 44)
        event.handled = True
        return
    if event.data1 == 81:  # PAD MODE/OMNI MODE
        for channel in range(100, 108):
            device.midiOutMsg(176, 0, channel, 0)
        for mode in range(81, 85):
            device.midiOutMsg(176, 0, mode, 0)
        for note in range(0, 16):
            device.midiOutMsg(144, 0, note, 0)
        device.midiOutMsg(176, 0, 81, 127)
        controller.padmode = OMNI
        controller.overlaymode = NONE
        ui.showWindow(midi.widChannelRack)
        ui.setFocused(midi.widChannelRack)
        controller.note_off()
        refresh_channels()
        print("Pad Mode:")
        device.midiOutMsg(176, 0, controller.channels + 100, White3)
        event.handled = True
        return
    if event.data1 == 82:  # KEYBOARD
        for group in range(100, 108):
            device.midiOutMsg(176, 0, group, 0)
        for mode in range(81, 85):
            device.midiOutMsg(176, 0, mode, 0)
        for note in range(0, 16):
            device.midiOutMsg(144, 0, note, 0)
        device.midiOutMsg(176, 0, 82, 127)
        controller.padmode = KEYBOARD
        controller.overlaymode = NONE
        controller.note_off()
        refresh_keyboard()
        print("Keyboard:")
        device.midiOutMsg(176, 0, cs.groups.index(controller.current_group) + 100, 4)
        event.handled = True
        return
    if event.data1 == 83:  # STEP SEQUENCING
        for stepchannel in range(100, 108):
            device.midiOutMsg(176, 0, stepchannel, 0)
        for mode in range(81, 85):
            device.midiOutMsg(176, 0, mode, 0)
        for note in range(0, 16):
            device.midiOutMsg(144, 0, note, 0)
        device.midiOutMsg(176, 0, 83, 127)
        print("Step:")
        controller.padmode = STEP
        controller.overlaymode = NONE
        controller.note_off()
        device.midiOutMsg(176, 0, controller.stepchannel + 100, Purple1)
        print("loading new channels 4")
        refresh_grid()
        event.handled = True
        return
    # --------------------------------------------------------------------------------------------------------
    #   OTHER CONTROLS
    # --------------------------------------------------------------------------------------------------------
    if event.data1 == 80:
        if controller.fixedvelocity == 0:
            controller.fixedvelocity = 1
            device.midiOutMsg(176, 0, 80, 127)
            event.handled = True
            return
        controller.fixedvelocity = 0
        device.midiOutMsg(176, 0, 80, 0)
        event.handled = True
        return
    # if event.data1 == 85 and controller.overlaymode == OPTION and event.data2 != 0:
    #     arrangement.addAutoTimeMarker(arrangement.currentTime(True), "TRANSITION")
    #     ui.setHintMsg("Marker Added")
    #     event.handled = True
    #     return
    if event.data1 == 85: #SELECT Page Overlay
        if controller.overlaymode == PAGE:
            controller.overlaymode = NONE
            refresh_selected_page()
        else:            
            controller.overlaymode = PAGE
            refresh_selector()
        event.handled = True
        return
        # # SELECT NEXT SCENE IN THE SONG
        # if event.data2 == 0:
        #     device.midiOutMsg(176, 0, 85, 0)
        #     event.handled = True
        #     return
        # arrangement.jumpToMarker(1, 1)
        # device.midiOutMsg(176, 0, 85, 127)
        # event.handled = True
        
    if event.data1 == 86: # SELECT Pattern Overlay
        if controller.overlaymode == PATTERN:
            controller.overlaymode = NONE
            refresh_selected_page()
        else:
            controller.overlaymode = PATTERN
            refresh_patterns()
        event.handled = True
        return
    if event.data1 == 87: # OPEN EVENT (PIANO ROLL)
        if event.data2 == 0:
            ui.hideWindow(midi.widPianoRoll)
            event.handled = True
            return
        ui.showWindow(midi.widPianoRoll)
        event.handled = True
        return
    if event.data1 == 88: # HOLDING DOWN SHIFT ("VARIATION" BUTTON)
        if controller.overlaymode == OPTION:
            controller.overlaymode = NONE
            refresh_selected_page()
        else:
            controller.overlaymode = OPTION
            refresh_options()
        event.handled = True
        return
    if event.data1 == 89: # DUPLICATE
        if event.data2 == 0:
            ui.paste()
            device.midiOutMsg(176, 0, 89, 0)
            event.handled = True
            return
        ui.copy()
        device.midiOutMsg(176, 0, 89, 127)
        event.handled = True
        return
    if event.data1 == 90: # SELECT
        if event.data2 == 0:
            arrangement.liveSelection(arrangement.currentTime(1), 1)
            device.midiOutMsg(176, 0, 90, 0)
            event.handled = True
            return
        arrangement.liveSelection(arrangement.currentTime(1), 0)
        device.midiOutMsg(176, 0, 90, 127)
        event.handled = True
        return
    if event.data1 == 91:
        channels.soloChannel(channels.selectedChannel())        
        event.handled = True
        return

    if event.data1 == 92: # MUTE MIXER TRACK
        channels.muteChannel(channels.selectedChannel())
        event.handled = True
        return

    if event.data1 == 39 and event.data2 != 0: # SAMPLING
        # if not :
            
        #     event.handled = True
        #     return
        print("getVisible " + str(ui.getVisible(midi.widBrowser)) )
        if ui.getVisible(midi.widBrowser):
            ui.hideWindow(midi.widBrowser)
            event.handled = True
            return
        else:
            ui.showWindow(midi.widBrowser)
            ui.setFocused(midi.widBrowser)
            event.handled = True
            return
    if event.data1 == 40 and controller.overlaymode == OPTION:  # FILE Save button
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, 0)
            event.handled = True
            return
        transport.globalTransport(midi.FPT_Save, 1)
        device.midiOutMsg(176, 0, event.data1, 127)
        event.handled = True
        return
    if event.data1 == 40:  # FILE Save button
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, 0)
            event.handled = True
            return
        transport.globalTransport(midi.FPT_Menu, 1)
        device.midiOutMsg(176, 0, event.data1, 127)
        event.handled = True
        return
    if event.data1 == 22: # PREVIOUS FL PRESET
        if event.data2 != 0:
            channels.showEditor(channels.selectedChannel(), 1)
            device.midiOutMsg(176, 0, event.data1, 127)
            if plugins.isValid(channels.selectedChannel()):
                if ui.getFocusedPluginName() == "Serum":
                    message1 = 176 + (SERUM_PRESET_PREV_CC << 8) + (0 << 16) + (MIDI_PORT_SERUM << 24)
                    message2 = 176 + (SERUM_PRESET_PREV_CC << 8) + (127 << 16) + (MIDI_PORT_SERUM << 24)
                    device.forwardMIDICC(message1)
                    device.forwardMIDICC(message2)
                    event.handled = True
                    return
                else:
                    plugins.prevPreset(channels.selectedChannel())
                    event.handled = True
                    return
        device.midiOutMsg(176, 0, event.data1, 0)
        event.handled = True
        return
    if event.data1 == 23:
        if event.data2 != 0: # NEXT FL PRESET
            channels.showEditor(channels.selectedChannel(), 1)
            device.midiOutMsg(176, 0, event.data1, 127)
            if plugins.isValid(channels.selectedChannel()):
                if ui.getFocusedPluginName() == "Serum":
                    message1 = 176 + (SERUM_PRESET_NEXT_CC << 8) + (0 << 16) + (MIDI_PORT_SERUM << 24)
                    message2 = 176 + (SERUM_PRESET_NEXT_CC << 8) + (127 << 16) + (MIDI_PORT_SERUM << 24)
                    device.forwardMIDICC(message1)
                    device.forwardMIDICC(message2)
                    event.handled = True
                    return
                else:
                    plugins.nextPreset(channels.selectedChannel())
                    event.handled = True
                    return
        device.midiOutMsg(176, 0, event.data1, 0)
        event.handled = True
        return
    if event.data1 == 24 or event.data1 == 25:
        if event.data2 != 0:
            device.midiOutMsg(176, 0, event.data1, 127)
            if event.data1 == 25 and controller.program <= 126:
                controller.program += 1
                ui.setHintMsg("PROGRAM = " + str(controller.program))
            elif event.data1 == 24 and controller.program != 0:
                controller.program -= 1
                ui.setHintMsg("PROGRAM = " + str(controller.program))
            message = 192 + (controller.program << 8) + (0 << 16) + (MIDI_PORT << 24)
            device.forwardMIDICC(message)
            event.handled = True
            return
        device.midiOutMsg(176, 0, event.data1, 0)
        event.handled = True
        return
    if event.data1 == 36: #PLAYLIST
        if ui.getVisible(widPlaylist):
            ui.hideWindow(midi.widPlaylist)
            event.handled = True
            return
        ui.showWindow(midi.widPlaylist)
        event.handled = True
        return
    if event.data1 == 35: # SHOW/HIDE PLUGIN/SAMPLE FORM CURRENTLY SELECTED
        if event.data2 == 0:
            device.midiOutMsg(176, 0, 35, 0)
            event.handled = True
            return
        device.midiOutMsg(176, 0, 35, 127)
        channels.showCSForm(channels.selectedChannel(), -1)
        event.handled = True
        return
    if event.data1 == 38:# PLUGIN PICKER
        if event.data2 == 0:
            event.handled = True
            return
        if controller.plugin_picker_active == 0:
            transport.globalTransport(midi.FPT_F8, 1)
            controller.plugin_picker_active = 1
            device.midiOutMsg(176, 0, 38, 127)
        else:
            transport.globalTransport(midi.FPT_F8, 1)
            controller.plugin_picker_active = 0
            device.midiOutMsg(176, 0, 38, 0)
        #print(controller.plugin_picker_active)
        event.handled = True
        return
    if event.data1 == 37: # MIXER
        if ui.getVisible(midi.widMixer):
            ui.hideWindow(midi.widMixer)
            device.midiOutMsg(176, 0, event.data1, 0)
            event.handled = True
            return
        ui.showWindow(midi.widMixer)
        device.midiOutMsg(176, 0, event.data1, 127)
        event.handled = True
        return
    if event.data1 == 19: # CHANNEL RACK
        if ui.getVisible(1):
            ui.hideWindow(1)
            device.midiOutMsg(176, 0, 19, 0)
            event.handled = True
            return
        ui.showWindow(midi.widChannelRack)
        device.midiOutMsg(176, 0, 19, 127)
        event.handled = True
        return
    if event.data1 == 41: # MIDI SETTINGS
        transport.globalTransport(midi.FPT_F10, 1)
        event.handled = True
        return
    if event.data1 == 43: # RIGHT CLICK
        if not ui.isInPopupMenu():
            transport.globalTransport(midi.FPT_ItemMenu, 1)
            event.handled = True
            return
        else:
            ui.closeActivePopupMenu()
            event.handled = True
            return
    if event.data1 == 48:
        if event.data2 != 0:
            ui.snapOnOff()
            if ui.getSnapMode() == 3:
                device.midiOutMsg(176, 0, 48, 0)
            else:
                device.midiOutMsg(176, 0, 48, 127)
        #print(ui.getSnapMode())
        event.handled = True
        return
    # --------------------------------------------------------------------------------------------------------
    #   4-D ENCODER
    # --------------------------------------------------------------------------------------------------------
    if event.data1 == 44:
        if controller.encoder == VOLUME:
            controller.encoder = JOG
            event.handled = True
            controller.update_maschine_encoder(44, 0)
            return
        else:
            controller.encoder = VOLUME
            event.handled = True
            controller.update_maschine_encoder(44, 127)
            return
    if event.data1 == 45:
        if controller.encoder == SWING:
            controller.encoder = JOG
            event.handled = True
            controller.update_maschine_encoder(45, 0)
            return
        else:
            controller.encoder = SWING
            event.handled = True
            controller.update_maschine_encoder(45, 127)
            return
    if event.data1 == 46:
        if controller.encoder == TEMPO:
            controller.encoder = JOG
            event.handled = True
            controller.update_maschine_encoder(46, 0)
            return
        else:
            controller.encoder = TEMPO
            event.handled = True
            controller.update_maschine_encoder(46, 127)
            return
    if event.data1 == 7:  # PRESS
        ui.enter()
        event.handled = True
        return
    if event.data1 == 8:  # ROTATION
        if event.data2 == 65:
            if controller.encoder == JOG:
                if ui.getFocused(midi.widMixer):
                    ui.right()
                    event.handled = True
                    return
                ui.down()
                event.handled = True
                return
            elif controller.encoder == VOLUME:
                volume = channels.getChannelVolume(channels.selectedChannel()) + 0.01
                channels.setChannelVolume(channels.selectedChannel(), volume)
                event.handled = True
                return
            elif controller.encoder == SWING:
                ui.setFocused(midi.widPlaylist)
                ui.jog(1)
                event.handled = True
                return
            elif controller.encoder == TEMPO:
                transport.globalTransport(midi.FPT_TempoJog, 10)
                event.handled = True
                return
        if event.data2 == 63:
            if controller.encoder == JOG:
                if ui.getFocused(midi.widMixer):
                    ui.left()
                    event.handled = True
                    return
                ui.up()
                event.handled = True
                return
            elif controller.encoder == VOLUME:
                volume = channels.getChannelVolume(channels.selectedChannel()) - 0.01
                channels.setChannelVolume(channels.selectedChannel(), volume)
                event.handled = True
                return
            elif controller.encoder == SWING:
                ui.setFocused(midi.widPlaylist)
                ui.jog(-1)
                event.handled = True
                return
            elif controller.encoder == TEMPO:
                transport.globalTransport(midi.FPT_TempoJog, -10)
                event.handled = True
                return
    if event.data1 == 30:
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, Green1)
            event.handled = True
            return
        device.midiOutMsg(176, 0, event.data1, Green3)
        ui.up()
        event.handled = True
        return
    if event.data1 == 31:
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, Green1)
            event.handled = True
            return
        ui.right()
        device.midiOutMsg(176, 0, event.data1, Green3)
        event.handled = True
        return
    if event.data1 == 33:
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, Green1)
            event.handled = True
            return
        ui.down()
        device.midiOutMsg(176, 0, event.data1, Green3)
        event.handled = True
        return
    if event.data1 == 34:
        if event.data2 == 0:
            device.midiOutMsg(176, 0, event.data1, Green1)
            event.handled = True
            return
        ui.left()
        device.midiOutMsg(176, 0, event.data1, Green3)
        event.handled = True
        return
    # -----------------------------------------------------------------------------------------------------
    #   GROUPS
    # --------------------------------------------------------------------------------------------------------
    if 100 <= event.data1 <= 107:
        print("Event.data1 Changed: " + str(event.data1))
        for group in range(100, 108):
            device.midiOutMsg(176, 0, group, 0)
        for channel in range(0, 16):
            device.midiOutMsg(144, 0, channel, 0)
        if controller.padmode == OMNI:
            controller.channels = event.data1 - 100
            device.midiOutMsg(176, 0, event.data1, White1)
            controller.note_off()
            refresh_channels()
            event.handled = True
            return
        elif controller.padmode == KEYBOARD:
            print("Event.data1: " + str(event.data1))
            controller.current_group = cs.groups[event.data1 - 100]
            device.midiOutMsg(176, 0, event.data1, 4)
            controller.note_off()
            event.handled = True
            return
        elif controller.padmode == CHORDS:
            controller.active_chordset = event.data1 - 100
            controller.note_off()
            device.midiOutMsg(176, 0, event.data1, 44)
            event.handled = True
            return
        elif controller.padmode == STEP:
            controller.stepchannel = event.data1 - 100
            refresh_grid()
            device.midiOutMsg(176, 0, event.data1, Purple1)
            event.handled = True
            return

# --------------------------------------------------------------------------------------------------------
#   ROTARY WHEELS
# --------------------------------------------------------------------------------------------------------
    # LEFT SECTION
    if event.data1 == 20:
        if event.data2 == 0:
            controller.mixer_snap = 0
            event.handled = True
            return
        controller.mixer_snap = 1
        event.handled = True
        return
    if event.data1 == 70: # MIXER SELECT
        controller.selected_track = event.data2
        mixer.setTrackNumber(controller.selected_track)
        event.handled = True
        return
    if event.data1 == 71: # MIXER VOLUME
        if controller.mixer_snap == 1:
            mixer.setTrackVolume(mixer.trackNumber(), 0.8)
            event.handled = True
            return
        converted_volume = event.data2 / 125
        if 0.78 < converted_volume < 0.82:
            converted_volume = 0.8
        mixer.setTrackVolume(mixer.trackNumber(), converted_volume)
        event.handled = True
        return
    if event.data1 == 72: # MIXER PAN
        if controller.mixer_snap == 1:
            mixer.setTrackPan(mixer.trackNumber(), 0)
            event.handled = True
            return
        converted_pan = (event.data2 / 63) - 1
        if -0.05 < converted_pan < 0.05:
            converted_pan = 0
        mixer.setTrackPan(mixer.trackNumber(), converted_pan)
        event.handled = True
        return
    if event.data1 == 73: # MIXER STEREO SEPARATION
        if controller.mixer_snap == 1:
            ssindex = midi.REC_Mixer_SS + mixer.getTrackPluginId(mixer.trackNumber(), 0)
            general.processRECEvent(ssindex, 0, midi.REC_UpdateValue | midi.REC_UpdateControl | midi.REC_ShowHint)
            event.handled = True
            return
        converted_ss = event.data2 - 63
        if -2 < converted_ss < 2:
            converted_ss = 0
        ssindex = midi.REC_Mixer_SS + mixer.getTrackPluginId(mixer.trackNumber(), 0)
        general.processRECEvent(ssindex, converted_ss, midi.REC_UpdateValue | midi.REC_UpdateControl | midi.REC_ShowHint)
        event.handled = True
        return
    # RIGHT SECTION
    if event.data1 == 74:
        if event.data2 < channels.channelCount():
            channels.selectOneChannel(event.data2)
            ui.setHintMsg("Channel selected: " + str(channels.getChannelName(channels.selectedChannel())))
        else:
            device.midiOutMsg(176, 0, 74, channels.selectedChannel())
        event.handled = True
        return
    if event.data1 == 75:
        id = midi.REC_Chan_OfsVol + channels.getRecEventId(channels.selectedChannel())
        value = (event.data2 / 127) * 25600
        if 12200 < value < 13300:
            value = 12800
        general.processRECEvent(id, round(value), midi.REC_UpdateValue | midi.REC_UpdateControl | midi.REC_ShowHint)
        # value is between 0 and 25600
        event.handled = True
        return
    if event.data1 == 76:
        id = midi.REC_Chan_OfsFCut + channels.getRecEventId(channels.selectedChannel())
        value = ((event.data2 / 127) * 512) - 256
        #value2 = general.processRECEvent(id, round(value), midi.REC_GetValue)
        #print(value)
        if -12 < value < 12:
            value = 0
        general.processRECEvent(id, round(value), midi.REC_UpdateValue | midi.REC_UpdateControl | midi.REC_ShowHint)
        # value is between -256 and 256
        event.handled = True
        return
    if event.data1 == 77:
        controller.fixedvelocityvalue = event.data2
        event.handled = True
        return

# --------------------------------------------------------------------------------------------------------
#   NOTES
# --------------------------------------------------------------------------------------------------------
def OnNoteOn(event): 
    pad_id = event.data1 % 16
    velocity = event.data2

    if controller.overlaymode == OPTION:
        if pad_id in [14, 15] and velocity != 0: #Octave Shifting
            if pad_id == 14 and controller.current_octave >= -2:
                controller.current_octave -= 1
            if pad_id == 15 and controller.current_octave <= 2:
                controller.current_octave += 1     
            refresh_options()
            print("Octave: " + str(controller.current_octave))
            ui.setHintMsg("Current octave: " + str(controller.current_octave))
            controller.note_off() 
            event.handled = True
            return

        if pad_id in [12, 13] and velocity != 0: #Semitone Shifting
            if pad_id == 12 and controller.current_offset > -11:
                controller.current_offset -= 1
            elif pad_id == 12 and controller.current_octave >= -2:
                controller.current_offset = 0
                controller.current_octave -= 1
            if pad_id == 13 and controller.current_offset < 11:
                controller.current_offset += 1
            elif pad_id == 13 and controller.current_octave <= 2:
                controller.current_offset = 0
                controller.current_octave += 1
            refresh_options()
            print("Semitone: " + str(controller.current_offset))
            ui.setHintMsg("Root note: " + controller.scale[controller.current_offset])
            controller.note_off()        
            event.handled = True
            return

        if pad_id in [0, 1] and velocity != 0: #Shortcuts
            if pad_id == 0: #Undo
                general.undoUp()
                print("Undo")
                ui.setHintMsg("Undo")
            elif pad_id == 1: #Redo
                general.undoDown()
                ui.setHintMsg("Redo")
                print("Redo")
            controller.note_off()
            event.handled = True
            return 

    elif controller.overlaymode == PATTERN:
        compare_pattern = patterns.patternCount() - 1
        if pad_id <= compare_pattern:
            patterns.jumpToPattern(pad_id + 1)
            refresh_patterns()
            ui.setHintMsg("Select pattern: " + patterns.getPatternName(pad_id + 1))
        elif pad_id == compare_pattern + 1:
            patterns.selectPattern(1)
            patterns.findFirstNextEmptyPat(midi.FFNEP_DontPromptName)  
            refresh_patterns()   
            ui.setHintMsg("Select pattern: " + patterns.getPatternName(pad_id + 1))  
        controller.note_off() 
        event.handled = True
        return
    
    elif controller.overlaymode == PAGE:
        if controller.padmode == OMNI and pad_id < ((channels.channelCount()-1) // 16) + 1:
            controller.channels = pad_id
            ui.setHintMsg("Select Padpage: " + str(pad_id + 1))
            refresh_selector()
        elif controller.padmode == KEYBOARD and pad_id < len(cs.groups): 
            controller.current_group = cs.groups[pad_id]      
            ui.setHintMsg("Select Keyboardpage: " + str(pad_id + 1)) 
            refresh_selector()  
        elif controller.padmode == CHORDS and pad_id < len(cs.chdSet):
            controller.active_chordset = pad_id
            ui.setHintMsg("Select Chordpage: " + str(pad_id + 1))
            refresh_selector()
        elif controller.padmode == STEP:
            controller.stepchannel = pad_id
            ui.setHintMsg("Select Steppage: " + str(pad_id + 1))
            refresh_selector()
        
        
        event.handled = True
        controller.note_off()
        return

    elif controller.overlaymode == NONE: #regular note mode
        
        if controller.padmode == OMNI:
            lower_channel = controller.channels * 16
            if pad_id < channels.channelCount():
                channels.selectOneChannel(lower_channel + pad_id)
                selectedchannel = channels.selectedChannel()                
                realnote = cs.C6
                realnote += (controller.current_octave * 12) + controller.current_offset if channels.getChannelType(selectedchannel) != 0 else 0
                if velocity != 0:                    
                    for channel in range(lower_channel, channels.channelCount()):
                        color = 'highlight' if channel == selectedchannel else 'color'                       
                        device.midiOutMsg(144, 0, channel - lower_channel, ChannelCoding[channels.getChannelType(channel)][color])
                    velocity = velocity if controller.fixedvelocity == 0 else controller.fixedvelocityvalue
                else:
                    velocity = 0
                channels.midiNoteOn(channels.getChannelIndex(lower_channel + pad_id), realnote, velocity)
            event.handled = True
            return
        
        elif controller.padmode == KEYBOARD:
            realnote = controller.current_group[pad_id] + (controller.current_octave * 12) + controller.current_offset + 12
            realindex = channels.getChannelIndex(channels.selectedChannel())
            if velocity != 0:
                controller.last_triggered.append(realnote)
                if controller.fixedvelocity == 0:                
                    channels.midiNoteOn(realindex, realnote, velocity)
                else:
                    channels.midiNoteOn(realindex, realnote, controller.fixedvelocityvalue)
                device.midiOutMsg(144, 0, pad_id, KEYBOARD_HIGHLIGHTED)
                event.handled = True
                return
            else:
                if realnote in controller.last_triggered:
                    controller.last_triggered.remove(realnote)
                channels.midiNoteOn(realindex, realnote, 0)
                device.midiOutMsg(144, 0, pad_id, KEYBOARD_COLOR)
                event.handled = True
                return
        
        elif controller.padmode == CHORDS:
            realindex = channels.getChannelIndex(channels.selectedChannel())
            if velocity != 0:
                for note in cs.chdSet[controller.active_chordset][pad_id]:
                    
                    realnote = note + (controller.current_octave * 12) + controller.current_offset + 12
                    if realnote not in controller.last_triggered:
                        if controller.fixedvelocity == 0:
                            channels.midiNoteOn(realindex, realnote, velocity)
                        else:
                            channels.midiNoteOn(realindex, realnote, controller.fixedvelocityvalue)
                        controller.last_triggered.append(realnote)
                    else:
                        controller.last_triggered.append(realnote)
                device.midiOutMsg(144, 0, pad_id, CHORDS_HIGHLIGHTED)
                event.handled = True
                return
            else:
                for note in cs.chdSet[controller.active_chordset][pad_id]:
                    realnote = note + (controller.current_octave * 12) + controller.current_offset + 12
                    if realnote in controller.last_triggered:
                        controller.last_triggered.remove(realnote)
                    if realnote not in controller.last_triggered:
                        channels.midiNoteOn(realindex, realnote, 0)
                device.midiOutMsg(144, 0, pad_id, CHORDS_COLOR)
                event.handled = True
                return
        
        elif controller.padmode == STEP:
            if velocity != 0:
                index = pad_id + (controller.stepchannel * 16)
                selectedchannel = channels.selectedChannel()
                isset = (1, 'highlight') if channels.getGridBit(selectedchannel, index) == 0 else (0, 'color')
                channels.setGridBit(selectedchannel, index, isset[0])
                device.midiOutMsg(144, 0, pad_id, ChannelCoding[6][isset[1]])
            event.handled = True
            return

# FOR THIS CONTROLLER NOTE OFF STATUS NEVER APPEARS, INSTEAD DATA2 WITH 0 VALUE TURNS NOTES OFF
def OnNoteOff(event):
    event.handled = True
    return

def OnKeyPressure(event):
    return


def OnChannelPressure(event):
    return