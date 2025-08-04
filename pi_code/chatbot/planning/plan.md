# Plan as of 20th July

1. [DONE] Face_Tracking and Sentry work fine enough to begin the next stage.
2. [DONE] When thinking must orchestrate what LEDs will do
3. [DONE] Must come up with way to asynchrounsly run face tracking, led blinking and the chatbot. Can only chat when LED green is blinking as milo can 'see' you.
4. [DONE] Play how asynchornous will work with all of these functions
5. Customise little easter eggs like 'disco biscuits' plays andies voice and 'drop a beat' drops mad beat. Or 'Dance' makes servo dance
6. [DONE] Replace tilt sg90 servo with new one
7. Come up with new body design for Milo


# 22nd July Update

1. [DONE] Face_tracking could do with a better PD controller this can be fixed later
2. [DONE] made a script called brain above all modules so it should be able to call from all code created now (yay)
3. [DONE] Brain currently utilises LED functionaility async with asyncio and east _to_thread threading techniques
4. Next step is to make it that milo can't be spoke to unless he has seen someone for the last 20 seconds.
Once this the processing starts it can't be interupted. When this is in. I can then add easter eggs
5. Easter Eggs
- disco biscuits - andy hill audio
- drop a beat 'drops one of 3 beats'
- dance - servos do little dance
5.b Must make shell script to run when pi has power to it so it works without hdmi (starting pigmoid, stopping pigmoid, clearing recordings on turn on) 
6. Create new body for Milo and replace SG90 servo
7. Make trailer. Bam summer project over. Do a summary of what Milo is and what I have learned. 
