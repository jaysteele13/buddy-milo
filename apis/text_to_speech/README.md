# How to run service
```
uvicorn app:app
```

# How to hit endpoint

Use this curl command in terminal ( I lazy and don't install postman)

```
curl -X POST http://127.0.0.1:8080/transcribe   -H "x-api-key: pi_is_awesome"   -F "file=@test1.wav"

```

# How to build with docker
ocker 
Using OpenAI built speech-text model Whisper Tiny. May go toward Whisper Base depending on RAM usage allowance in Google cloud. As of yet the comparison for ram usage is:
Tiny: 600mb
Base: 800mb