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

23/05/2025
Due to the size of pytorch, the image created was 10GB. I have instead opted for using a more quantised version of whisper which has been compiled in C++. This avoids the need for pytorch. In doing this I have dockerised the code and create an image.
Using Google Cloud Run Free Tier I have uploaded this image in the artifact repository for google cloud. In addition I have also made this endpoint authorised only to avoid DDoS attacks and traffic. The endpoint is now only accessible by two keys, on api.json and another is string api key.

The endpoint can be hit from any compute device as long as there is wifi and these keys. The main drawback is the time it takes to process this, which is 11 seconds on average. Future work would be potenially spending money on a more powerful compute server to get faster times, or just potentially hosting local servers from my PC. However one of the main goals is to have this robot isolated, so all it needs is to be charged and have WiFi connection.

01/06/2025

So I have created a system where the chatbot takes in a string and currently, outputs surf forecasts of portush's east and west strand for the current day or day after depending on request which is aquired using regex. Done the same but for weather with a weather API. Have a secret function about milk with robot.

I have also begun training the small LLM, I have experimented with tiny models such as tiny-llama and others with arond 100m params, current progress is bleak. I have made a custom dataset with over 500 lines of content I would like the robot to act like. Due to the 1.1b params from tiny-llama I fear it may be to big to coherse with such a small dataset so will look elsewhere.

I have programming this in google colab, and using BitsAndBytes to load it in quantised so it trains better. Have experimented with using axolotl locally and on Collab to no avail, Linux Mint is not the ideal distro to try docker-nvidia relations it seems. I did however sucessfully install cuda and make it compatible with my current GPU. Due to Colab though, I have yet to use this.

The Short Term plan is to continue trying to find smaller models and test them with my common questions, once this is done, then I can experiment with llama.cpp to try and quantise this model to make it run better on the CPU and hopefully deploy this second endpoint as an image to google cloud run.

15/06/2025

After weeks of tinkering I have realised fine-tuning and transfer learning with pre-existing models is the way to go. With help of my own intuition and Big LLM prompting, I have created a small dataset to train my desired model on.

I have experimented with state of the art models from hugging face, training models with my dataset on tiny llms ranging from 50m - 1.8B parameters. Ultimately. My dataset is not big enough to change the tone of a bigger dataset with 1B params, and the smaller llms with around 100-200M don't have enough intelligence to work. I have landed on a fine tuned model based off of Llama's tiny LLM. Link [here](https://huggingface.co/AlexandrosChariton/SarcasMLL-1B). This model utilises a big broad sarcastic, nothing answer which is the kind of vibe I wanted.

I used Llama.cpp to load in this quantised model.

In addition I have now gained access to an old laptop which I am going to convert to a home private server which will now run these endpoints rather than google cloud run. This will increase the speed drastically. Talk about this later...


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
