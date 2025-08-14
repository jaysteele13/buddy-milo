import os
import random
import asyncio
import signal


def pick_random_file(dir_path):
    # List all file names in the given directory
    files_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    if not files_list:
        return None  # or raise an error if preferred
    
    # Randomly pick one file name
    return f'{dir_path}/{random.choice(files_list)}'
    
async def play_output(file_path, stop_event, kill_event):
    print("🎧 Playing response...")

    process = await asyncio.create_subprocess_exec("aplay", file_path)

    while True:
        # Polling loop to check if audio finished or stop_event is set
        if stop_event.is_set() or (kill_event.is_set()):
            process.kill()
            await process.wait()
            print("🎧 Playback interrupted.")
            return

        if process.returncode is not None:
            # Process already completed
            break

        await asyncio.sleep(0.1)  # Yield control, check again soon

    print("🎧 Playback finished.")
    
    
async def play_output_blocking(file_path,):
    print("🎧 Playing response...")

    process = await asyncio.create_subprocess_exec("aplay", file_path)
    await process.wait()
    print("🎧 Playback finished.")
    
async def play_audio( # this isn't working making sure params are correct and add logs
    file_path,
    stop_event=None,
    kill_event=None,
    playing_output: asyncio.Event = None,
    stop_face_tracking: asyncio.Event = None
):
    """
    Plays audio via 'aplay', with optional stop events and control flags.
    """
    print(f"🎧 Playing {file_path}...")

    if playing_output:
        playing_output.set()  # mark playback started

    process = await asyncio.create_subprocess_exec("aplay", file_path)

    while True:
        # Stop conditions
        if (stop_event and stop_event.is_set()) or (kill_event and kill_event.is_set()):
            print('TRY  TO KILL AUDIO')
            process.kill()
            await process.wait()
            print("🎧 Playback interrupted.")
            break

        if process.returncode is not None:
            print('finish naturally')
            # Finished naturally
            break

        await asyncio.sleep(0.1)

    # Cleanup flags
    if stop_face_tracking:
        stop_face_tracking.set()
    if playing_output:
        playing_output.clear()

    print("🎧 Playback finished.")



    
async def find_and_think(dir_path, stop_event, kill_event):
    file_path = pick_random_file(dir_path)
    
    if file_path is None:
        print('Invalid File Path / Dir is Empty!')
        return
    await play_output(file_path, stop_event, kill_event)
    
