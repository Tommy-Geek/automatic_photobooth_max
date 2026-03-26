from pycaw.pycaw import AudioUtilities
import time
import keyboard
import pythoncom

def make_photo():

    pythoncom.CoInitialize()

    try:
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        volume.SetMasterVolumeLevel(-96.0, None) #скидываем в 0 громкость
        initial_volume = volume.GetMasterVolumeLevel()

        while True:
            current_volume = volume.GetMasterVolumeLevel()
            if initial_volume != current_volume:
                keyboard.send('ctrl+alt+space')
                print(f"сделал кадр, текущая громкость = {initial_volume}")
                volume.SetMasterVolumeLevel(-96.0, None) #скидываем в 0 громкость
                time.sleep(0.5)
            time.sleep(0.1)
    finally:
        pythoncom.CoUninitialize()

        
# volume.GetMasterVolumeLevel() # = громкость в дцб
