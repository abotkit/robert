# robert
robert is a BERT-based bot using a flask server as interface to modify and update phrases, intents and actions.

# quickstart

```zsh
pip install -r requirements.txt
export ABOTKIT_ROBERT_PORT=5000 # or any port you want to use

# in development mode
python robert.py

# for production usage
pip install gunicorn
gunicorn --bind 0.0.0.0:$ABOTKIT_ROBERT_PORT robert:app
```

# environment variables

|         name        |        description             |    default           |
|---------------------|--------------------------------|----------------------|
| ABOTKIT_ROBERT_PORT | port for starting robert       |   5000               |