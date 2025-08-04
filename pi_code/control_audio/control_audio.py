import os
import random
import asyncio



def pick_random_file(dir_path):
    # List all file names in the given directory
    files_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    if not files_list:
        return None  # or raise an error if preferred
    
    # Randomly pick one file name
    return f'{dir_path}/{random.choice(files_list)}'
    
async def play_output(file_path, stop_event):
    print("🎧 Playing response...")

    process = await asyncio.create_subprocess_exec("aplay", file_path)

    while True:
        # Polling loop to check if audio finished or stop_event is set
        if stop_event.is_set():
            process.kill()
            await process.wait()
            print("🎧 Playback interrupted.")
            return

        if process.returncode is not None:
            # Process already completed
            break

        await asyncio.sleep(0.1)  # Yield control, check again soon

    print("🎧 Playback finished.")
    
async def find_and_think(dir_path, stop_event):
    file_path = pick_random_file(dir_path)
    
    if file_path is None:
        print('Invalid File Path / Dir is Empty!')
        return
    await play_output(file_path, stop_event)
    
