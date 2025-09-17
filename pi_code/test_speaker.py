from brainV2 import listen_for_prompt

import asyncio

async def main():
        file = asyncio.run(listen_for_prompt())
        print(f'file: {file}')
        
if __name__ == "__main__":
    
    try:

        # Listening but not recording - change default in .conf? from logitect to usb speaker
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Main loop cancelled.")
    finally:
        print('Cleaning Up life')
      