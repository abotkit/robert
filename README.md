# robert
robert is a BERT-based bot using a fastapi server as interface to modify and update phrases, intents and actions.

# quickstart

```zsh
pip install -r requirements.txt
export ABOTKIT_ROBERT_PORT=5000 # or any port you want to use

pip install gunicorn
# use hot reload in development and during testing
uvicorn robert:app --reload

# remove --reload for production usage
uvicorn robert:app --port $ABOTKIT_ROBERT_PORT 
```

# environment variables

|         name        |        description             |    default           |
|---------------------|--------------------------------|----------------------|
| ABOTKIT_ROBERT_PORT | port for starting robert       |   5000               |