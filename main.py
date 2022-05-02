from midiutil import MIDIFile
from os import environ
import re
from pathlib import Path
from mido import MidiFile as midi
import mido.messages.messages

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# Variables
goodbye_msg = "\nHave a nice day bye-"
menu_msg = "\n=============== MENU ===============\n1 -> Encrypt\n2 -> Decrypt\n3 -> Exit\n"
midi_max, midi_min = 119, 21


# Functions
def return_message(filename="cifer.mid"):
    mid = midi(filename)
    for __i, track in enumerate(mid.tracks):
        for msg in track:
            if type(msg) == mido.messages.messages.Message:
                _message = str(msg)
                try:
                    note__ = re.search(
                        'note_on.*note=(.+?) velocity.*',
                        _message
                    ).group(1)
                    ascii_number = int(note__) + 11
                    if ascii_number != 11:
                        print(chr(ascii_number), end="")
                    else:
                        print(" ", end="")

                except AttributeError:
                    pass


def play_midi(midi_filename):
    # mixer config
    freq = 44100  # audio CD quality
    bitsize = -16  # unsigned 16 bit
    channels = 2  # 1 is mono, 2 is stereo
    buffer = 1024  # number of samples
    pygame.mixer.init(freq, bitsize, channels, buffer)

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(0.6)

    # Playing the file
    clock = pygame.time.Clock()
    pygame.mixer.music.load(midi_filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(30)  # check if playback has finished


def listen_midi_events(midi_filename):
    try:
        play_midi(midi_filename)
    except KeyboardInterrupt:
        # if user hits Ctrl/C then exit (works only in console mode)
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.stop()
        raise SystemExit


def checkAscii(_list, _max, _min, allowed_exceptions):
    for item in _list:
        if item in allowed_exceptions:
            pass
        elif item > _max or item < _min:
            return False
    return True


def write_midi(degrees, track=0, channel=0, time=0, duration=1, tempo=160, volume=100, file_name="cifer.mid"):
    mid = MIDIFile()  # One track, defaults to format 1 (tempo track automatically created)
    mid.addTempo(track, time, tempo)

    for note in degrees:
        mid.addNote(track, channel, note, time, duration, volume)
        time = time + 1

    with open(file_name, "wb") as output_file:
        mid.writeFile(output_file)
        print("Playing cifer midi created")
    listen_midi_events(file_name)


def selection(_validated=0, err_msg="Your input is wrong", inp_msg="Your input: ", accepted_input=None, is_file=False):
    if accepted_input is None:
        accepted_input = []

    check = False

    while not check:
        try:
            _input = input("\n" + inp_msg).strip()

            if is_file:
                path_exist = Path(_input).is_file()
                if path_exist:
                    return _input
                print(err_msg)
            elif (_validated == 0 and accepted_input == []) or (_input in accepted_input) or (int(_input) in range(_validated)):
                return _input
            else:
                print(err_msg)

        except ValueError:
            print(err_msg)


def menu():
    err_msg = "Wrong selection. Please choose from 0 to 3"
    print("\n" + menu_msg)
    return selection(_validated=4, err_msg=err_msg, inp_msg="Your menu selection: ")


try:
    while True:
        inp = menu()
        if inp == "1":
            messageToBeEncrypted = selection(err_msg="", inp_msg="Your message to be encrypted: ")
            ascii_list = list()

            for char in messageToBeEncrypted:
                if char == " ":
                    ascii_list.append(0)
                else:
                    ascii_list.append(ord(char) - 11)

            if not checkAscii(ascii_list, midi_max, midi_min, [0]):
                print("Some of your characters are not supported currently")
            else:
                write_midi(ascii_list)
        elif inp == "2":
            path_exist = Path("cifer.mid").is_file()
            if path_exist:
                return_message()
            else:
                print("Oof nothing is encrypted right now")
        elif inp == "3":
            print(goodbye_msg)
            exit()
except (KeyboardInterrupt, EOFError):
    print(goodbye_msg)
