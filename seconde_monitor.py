import win32api
import win32con


def main_monitor_size()-> list:

    d = win32api.EnumDisplayDevices(None, 0)
    dm = win32api.EnumDisplaySettings(d.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
    
    width = max(dm.PelsWidth, dm.PelsHeight)
    height = min(dm.PelsWidth, dm.PelsHeight)
    
    main_size = [width, height]

    return main_size


def seconde_monitor_size():

    d = win32api.EnumDisplayDevices(None, 1)
    dm = win32api.EnumDisplaySettings(d.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
    
    width = max(dm.PelsWidth, dm.PelsHeight)
    height = min(dm.PelsWidth, dm.PelsHeight)
    
    seconde_size = [width, height]

    return seconde_size


def rotate_and_get_coords():
    """переворачиваем изображение на втором мониторе"""
    d = win32api.EnumDisplayDevices(None, 1)
    dm = win32api.EnumDisplaySettings(d.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
    
    current_orientation = dm.DisplayOrientation if hasattr(dm, 'DisplayOrientation') else dm.Orientation
    
    # Определяем физические размеры (большее значение - это ширина, меньшее - высота)
    width = max(dm.PelsWidth, dm.PelsHeight)
    height = min(dm.PelsWidth, dm.PelsHeight)
    
    if current_orientation != win32con.DMDO_90:
        # Поворачиваем на 90°
        dm.DisplayOrientation = win32con.DMDO_90
        dm.PelsWidth, dm.PelsHeight = dm.PelsHeight, dm.PelsWidth
        dm.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYORIENTATION
        
        win32api.ChangeDisplaySettingsEx(d.DeviceName, dm)
