# buddy-milo
Stationary desk buddy. Programmed to look at people when speaking to them. Using face detection, face recognition, speech recognition, text-to-speech technology and complex LLM's with the goal to experience a fun sarcastic friendly attidude with my robot.

**Additional Features:**
- NI North Coast surf and weather forecasting
- Drops Beats on Command
- Other fun easter eggs
- Silly nonesence sarcastic personaility
- Randomly insults you
- Recognises me. Anyone else is an enemy



# Other Steps
**Step Two** (Done)
Design and 3D print and pan and tilt system for raspberry pi in fusion 360 ->
1. Is it possible to make a case for raspberry pi as well as pan and tilt system so CPU gets adequate cooling
2. Looks ok and pan and tilt isn’t top heavy
3. Have additional power source to power Servos

**Step Three** (Done)
- Begin looking up how LLM and Speech recognition work on a raspberry pi
- Start by talking to raspberry pi through microphone and getting input
- From their start playing with speakers and output

**Step 4** (Done)
- Either train and use another llm or attempt to make one then host it on free tier amazon cloud service. 
- This must be done through API as it is too powerful for raspberry PI. 
- Wait times may be weird but worth it?

**Step 5** (Now not out of scope but - focusing on core logic and getting to work)
- Experiment with Raspberry PI connecting to internet without direct ethernet
- Has rechargeable battery for device

**Step 6** (Done)
- Connect Server in network to milo (done)
- properly configure how milo will interact with recognised and non recognised people (done)
- configure LEDs green when talking red when on standby, blue when listening (done)
- should he be triggered by a wake word. If person in frame grab audio and look for wake word using endpoint and regex? (done)
- listen to voice based on sensitvity or just record for listen for voice every 3 seconds. per sentry erase recordings. (done)
- tests and fail checks if API doesn't connect? (eh kinda - done with salt)
- add easter egg if you ask milo to 'drop a beat' (done)
- add easter egg to dance (done)
  
**Step 7** (Currently Doing)
- make 3D printed design for milo on Fusion360
- Make trailer using kdenlive
- Conceal Wires and make it look more ‘buddy’ like
