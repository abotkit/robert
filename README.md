# robert
robert is a BERT-based bot using a fastapi server as interface to modify and update phrases, intents and actions.

# Quickstart

```zsh
pip install -r requirements.txt
export ABOTKIT_ROBERT_PORT=5000 # or any port you want to use

# use hot reload in development and during testing
uvicorn robert:app --reload --port ${ABOTKIT_ROBERT_PORT}

# use uvicorn wrapped by gunicorn in production
gunicorn robert:app -b 0.0.0.0:${ABOTKIT_ROBERT_PORT} -p robert.pid -k uvicorn.workers.UvicornWorker --timeout 120 --workers=1 --access-logfile access.log --log-level DEBUG --log-file app.log

# for testing
curl -X POST -H "Content-Type: application/json" -d "{\"query\":\"hi\", \"identifier\":\"unique-char-id\"}" localhost:${ABOTKIT_ROBERT_PORT}/handle       

# should give you something like
# [{"recipient_id":"unique-char-id","text":"Hey"}]
```

# Environment variables

|         name        |        description             |    default           |
|---------------------|--------------------------------|----------------------|
| ABOTKIT_ROBERT_PORT | port for starting robert       |   5000               |
| ABOTKIT_ROBERT_USE_MINIO | use MinIO flag ('True' or 'False')  | 'False' |
| ABOTKIT_ROBERT_MINIO_URL | MinIO host name or url | 'localhost' |
| ABOTKIT_ROBERT_MINIO_PORT | MinIO port | 9000 |
| ABOTKIT_ROBERT_MINIO_SECRET_KEY | MinIO secret key | 'A_SECRET_KEY' |
| ABOTKIT_ROBERT_MINIO_ACCESS_KEY | MinIO access key | 'AN_ACCESS_KEY' |

# Issues

We use our [main repository](https://github.com/abotkit/abotkit) to track our issues. Please use [this site](https://github.com/abotkit/abotkit/issues) to report an issue. Thanks! :blush:
