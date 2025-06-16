# How to run service
```
uvicorn app:app
```

# How to hit endpoint

Use this curl command in terminal ( I lazy and don't install postman)

```
curl -X POST http://127.0.0.1:8000/personality \
  -H "x-api-key: <api-key>" \
  -H "Content-Type: application/json" \
  -d '{"sentence": "im bored what should i do"}'
```




# Switching to Home Server
Now that I am switching operation to home server, limitations on RAM and memory aren't as much as an issue, in addition to this they may not have to be dockerised. Depending on Setup with libraries, docker may be best but will explore options soon.
