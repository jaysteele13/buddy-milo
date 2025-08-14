# conclusion

### What bot does well
- Milo, even though using hardware more than a decade old (excluding Rasberry Pi 4B). Performs Text To Speech and Speech to Text capabilities fairly accurately.
- Given the LLM is trained on tiny llama to be sarcastic. Has good reasoning skills and knowledgable to decent degrees on outsanding topics. E.g. (give Example)
- Face_tracking reliably can find face and reduce error enough to be within Deadzone (camera is close enough to face so it doesn't need to constantly jitter if face is stationary)
- Variety in hardcoded as well as model llm responses makes the bot as an ok office assistant to chat to when bored.  


### Downfalls
- Microphone isn't as clear, as such sometimes STT model mistranslates words
- SG90 Servos are cheap and sometimes exceed angular limit due to voltage flucuations. The only way to fix this is to get better quality servos.
- Due to restricted hardware (Home Server is using a Inspiron 13 7000 2-in-1 (2014)) models I am using are only around 1B params. Had this been a server with an average sized GPU. I would have pushed it to try use Ollama 2. A 7B model.

Last things to do
- Shell script to activate milo when button pressed.
- Once this is done begin designing body.
