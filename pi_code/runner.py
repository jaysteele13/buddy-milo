import time
import pigpio
import dbus
import asyncio
from control_button.button import BUTTON_PIN
from control_audio.control_audio import play_output_blocking
from control_led.blink_led import LED_RED_PIN, LED_GREEN_PIN

# --- GPIO Setup with pigpio ---
pi = pigpio.pi()  # Connect to local pigpiod
pi.set_pull_up_down(BUTTON_PIN, pigpio.PUD_UP)
if not pi.connected:
    raise RuntimeError("Cannot connect to pigpiod. Make sure pigpiod is running.")

def turn_off_leds():
    pi.write(LED_RED_PIN, 0)
    pi.write(LED_GREEN_PIN, 0)

async def wait_for_press():
    while pi.read(BUTTON_PIN) == 0:
 
        await asyncio.sleep(0.05)
    while pi.read(BUTTON_PIN) == 1:
        await asyncio.sleep(0.05)
        
        



# --- D-Bus Setup ---
bus = dbus.SystemBus()
systemd1 = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')

def get_service_state(service_name):
    unit_path = manager.GetUnit(service_name)
    unit = bus.get_object('org.freedesktop.systemd1', str(unit_path))
    unit_props = dbus.Interface(unit, dbus.PROPERTIES_IFACE)
    return unit_props.Get('org.freedesktop.systemd1.Unit', 'ActiveState')

def start_service(service_name):
    manager.StartUnit(service_name, 'replace')
    

def stop_service(service_name):
    manager.StopUnit(service_name, 'replace')
    


async def main():
    

    PIGPIOD = 'pigpiod.service'
    MILO = 'milo_brain.service'
    
    music_prefix = '/home/jay/Documents/projects/buddy-milo/pi_code/presets/power/'
    on_music = f'{music_prefix}on.wav'
    off_music = f'{music_prefix}off.wav'
    await play_output_blocking(on_music)

    try:
        while True:
            print("Waiting for button press...")
            await wait_for_press()

#             # Ensure pigpiod is running before Milo
#             pigpio_state = get_service_state(PIGPIOD)
#             if pigpio_state != 'active':
#                 print("Starting pigpiod service...")
#                 await start_service(PIGPIOD)
#                 # Give pigpiod a moment to start
#                 time.sleep(0.5)

            # Toggle Milo service
            milo_state = get_service_state(MILO)
            if milo_state == 'active':
                print("Stopping Milo service...")
                
                stop_service(MILO)
                await play_output_blocking(off_music)
                turn_off_leds()
                
            else:
                print("Starting Milo service...")
                start_service(MILO)
                await play_output_blocking(on_music)

    finally:
        pi.stop()
        # Optionally stop Milo when script exits
        try:
            stop_service(MILO)
        except Exception:
            pass
        
        

if __name__ == "__main__":
    
    try:

        
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Main loop cancelled.")
    finally:
        print('Finish Milo')
   
