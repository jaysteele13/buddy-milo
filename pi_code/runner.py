import asyncio
import pigpio
import time
import os
import dbus
from control_button.button import BUTTON_PIN
from control_audio.control_audio import play_output_blocking
from control_led.blink_led import LED_RED_PIN, LED_GREEN_PIN


PRESSED = 0
RELEASED = 1

# thresholds (seconds)
SHORT_MAX = 1.0
LONG_MIN  = 3.0

# debounce & cooldown (seconds)
DEBOUNCE_S = 0.26
COOLDOWN_S = 0.90

pi = pigpio.pi()
pi.set_mode(BUTTON_PIN, pigpio.INPUT)
pi.set_pull_up_down(BUTTON_PIN, pigpio.PUD_UP)  # matches PRESSED==1 logic

def turn_off_leds():
    pi.write(LED_RED_PIN, 0)
    pi.write(LED_GREEN_PIN, 0)

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

async def wait_for_press():
    while True:
        # Wait for button press (PRESSED)
        if pi.read(BUTTON_PIN) == PRESSED:
            # Press debounce
            await asyncio.sleep(0.05)  # 50ms debounce
            if pi.read(BUTTON_PIN) != PRESSED:
                continue  # false trigger

            press_t = time.monotonic()

            # Wait for release or long threshold
            while True:
                held = time.monotonic() - press_t
                if held >= LONG_MIN:
                    # Long press detected
                    await asyncio.sleep(COOLDOWN_S)
                    return ("long", held)

                if pi.read(BUTTON_PIN) == RELEASED:
                    # Release debounce
                    await asyncio.sleep(0.05)
                    if pi.read(BUTTON_PIN) != RELEASED:
                        continue  # false release

                    duration = time.monotonic() - press_t
                    if duration < SHORT_MAX:
                        await asyncio.sleep(COOLDOWN_S)
                        return ("short", duration)
                    else:
                        await asyncio.sleep(COOLDOWN_S)
                        return ("long", duration)

                await asyncio.sleep(0.01)

        await asyncio.sleep(0.01)


async def main():
    PIGPIOD = 'pigpiod.service'
    MILO = 'milo_brain.service'

    music_prefix = '/home/jay/Documents/projects/buddy-milo/pi_code/presets/power/'
    on_music = f'{music_prefix}on.wav'
    off_music = f'{music_prefix}off.wav'
    shutdown_music = f'{music_prefix}shutdown.wav'
    await play_output_blocking(on_music)

    try:
        while True:
            print("Waiting for button press...")
            kind, dur = await wait_for_press()
            print(f'kind {kind} dur: ')
            if kind == "short":
                milo_state = get_service_state(MILO).lower()
                if milo_state.startswith('active'):
                    print("Stopping Milo service...")
                    stop_service(MILO)
                    await play_output_blocking(off_music)
                    turn_off_leds()
                elif milo_state.startswith('inactive'):
                    print("Starting Milo service...")
                    start_service(MILO)
                    await play_output_blocking(on_music)

                await asyncio.sleep(0.05)  # let service state settle

            elif kind == "long":
                # Standby-ish: turn off display + LEDs
                turn_off_leds()
                pi.stop()
                await play_output_blocking(shutdown_music)
                print("Powering off completely")
                os.system("sudo shutdown now")
                

            

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
    except KeyboardInterrupt:
        pass


