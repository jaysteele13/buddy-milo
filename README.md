# buddy-milo
Stationary desk buddy. Programmed to look at people when speaking to them. Using face detection, face recognition, speech recognition, calls to trained complex LLM's with the goal to train the LLM to give it a sarcastic friendly attidude.

# Progress

16/05/2025
Currently I have configured the Rasberry Pi to capture 640 x 480 video and get face recognition and detection using haar cascade model for face detection due to its light wieght capabilities. Also using encoding technique to train this model on certain peoples faces ('buddies') which is through Pickle encodings. Also have a system in place to relay _x, y coordinates_ of where face is in relation to centre ounding box of face in the screen. This is so the servos will know where to look.


18/05/2025
Started Experimenting with USB Cam Microphone. Created a Script to take in and convert audio to 16bit wav file.
Started planning out a cloud architecture for LLM as well as now speech recognition. (Looking at 'whisper' model for speech recognition).
Using pavucontrol library to control gain when someone shouts into mic.

20/05/2025
Have Created a python script that uses whisper 'tiny' to convert .wav files to a string. This is hosted through FastAPI. Currently 'dockerising' this app into an image which I plan to host on Google Cloud Run Free Tier. Have an API key set so my PI will be able to hit this endpoint and move on to the next step which will be manipulating an LLM (Model and experimentation yet to be decided).


# Other Steps
**Step Two**
Design and 3D print and pan and tilt system for raspberry pi in fusion 360 ->
1. Is it possible to make a case for raspberry pi as well as pan and tilt system so CPU gets adequate cooling
2. Looks ok and pan and tilt isn’t top heavy
3. Have additional power source to power Servos

**Step Three**
- Begin looking up how LLM and Speech recognition work on a raspberry pi
- Start by talking to raspberry pi through microphone and getting input
- From their start playing with speakers and output

**Step 4**
- Either train and use another llm or attempt to make one then host it on free tier amazon cloud service. 
- This must be done through API as it is too powerful for raspberry PI. 
- Wait times may be weird but worth it?

**Step 5**
- Experiment with Raspberry PI connecting to internet without direct ethernet
- Has rechargeable battery for device
  
**Step 6**
- Conceal Wires and make it look more ‘buddy’ like
