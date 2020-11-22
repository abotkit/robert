import os
import pickle
import json
import logging

from http import HTTPStatus
from fastapi import FastAPI, Response, Body, Request
from fastapi_utils.tasks import repeat_every
from actions.actions import ACTIONS
from persistence.bot_reader import BotReader
from persistence.bot_writer import BotWriter
from api.models import Message, Language, NewExample, DeleteAction, RemoveExample, Action, Phrase, ListOfPhrases, BotMeta

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

bot = None
core = None
minio_client = None

CACHE_PATH = 'bot.pkl'
CONFIGURATION = 'bot.json'
PHRASES_FILE = os.path.join('actions', 'phrases.json')
HAS_UPDATES = False

USE_MINIO = str(os.environ.get('ABOTKIT_ROBERT_USE_MINIO', 'False')).lower() == 'true'
MINIO_URL = os.environ.get('ABOTKIT_ROBERT_MINIO_URL', 'localhost')
MINIO_PORT = str(os.environ.get('ABOTKIT_ROBERT_MINIO_PORT', '9000'))
MINIO_SECRET_KEY = str(os.environ.get('ABOTKIT_ROBERT_MINIO_SECRET_KEY', 'A_SECRET_KEY'))
MINIO_ACCESS_KEY = str(os.environ.get('ABOTKIT_ROBERT_MINIO_ACCESS_KEY', 'AN_ACCESS_KEY'))

def cache_bot():
  with open(CACHE_PATH, "wb") as handle:
    pickle.dump(bot, handle)

def store_bot():
  global HAS_UPDATES
  HAS_UPDATES = True

def upload_bot():
  if not (minio_client.bucket_exists(bot.id)):
    minioClient.make_bucket(bot.id, location="eu-west-1")

  files = [CONFIGURATION, PHRASES_FILE]

  for filepath in files:
    try:
      file_meta = os.stat(filepath)
      with open(filepath, 'rb') as handle:
        minioClient.put_object(bot.id, os.path.split(filepath)[-1], handle, file_meta.st_size)
    except ResponseError as error:
        logging.warning('MinIO upload failed')
        logging.error(error)

def download_bot():
  files = [CONFIGURATION, PHRASES_FILE]

  if (minio_client.bucket_exists(bot.id)):
    try:
      for filepath in files:
        filename = os.path.split(filepath)[-1]
        data = minioClient.get_object(bot.id, os.path.split(filepath)[-1])
        with open(filepath, 'wb') as handle:
          for block in data.stream(32*1024):
              handle.write(block)
    except ResponseError as error:
        logging.warning('MinIO download of {} failed'.format(filename))
        logging.error(error)
  else:
    logging.info('Failed to download bot from S3. Bot does not exist.')

@app.on_event("startup")
@repeat_every(seconds=5*60)
def store_files() -> None:
  global HAS_UPDATES
  global bot

  if HAS_UPDATES:
    BotWriter(bot).write(CONFIGURATION)
    HAS_UPDATES = False
    cache_bot()
    if USE_MINIO:
      upload_bot()

@app.on_event("startup")
def startup_event():
  global bot
  global core

  if USE_MINIO:
    from minio import Minio
    from minio.error import ResponseError
    global minio_client

    minio_client = Minio('{}:{}'.format(MINIO_URL, MINIO_PORT), access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY)
    download_bot()

  if os.path.exists(CACHE_PATH):
    try:
      with open(CACHE_PATH, "rb") as handle:
        bot = pickle.load(handle)
        core = bot.core
      return
    except:
      logging.warning('{} is broken. Fallback to json configuration'.format(CACHE_PATH))     

  path = os.path.join(CONFIGURATION)
  bot = BotReader(path).load()
  core = bot.core
  cache_bot()

@app.get("/")
def root():
  return '"When the legend becomes fact, you print the legend." - Robert Ford'

@app.get("/alive")
def alive():
  return Response(status_code=HTTPStatus.OK)

@app.post('/intent')
def intent(message: Message):
  return core.intent_of(message.query)

@app.post('/handle')
def handle_route(message: Message):
  return [{
    "recipient_id": message.identifier,
    "text": bot.handle(message.query)
  }]

@app.post('/explain')
def explain_route(message: Message):
  return bot.explain(message.query)

@app.get('/language')
def get_language():
  return bot.language

@app.post('/language')
def set_language(language: Language):
  if language.country_code == 'de' or language.country_code == 'en':
    bot.language = language.country_code
    store_bot()
    return Response(status_code=HTTPStatus.OK)
  else:
    return Response(status_code=HTTPStatus.BAD_REQUEST, content='language not supported.')

@app.get('/intent/examples')
def intent_examples(intent: str):
    examples = []
    for example in core.intents:
        if intent == core.intents[example]:
            examples.append(example)
    return examples

@app.get('/example')
def get_examples():
  intents = [{
    'name': intent,
    'action': bot.find_action_by_intent(intent)['action'].name
    } for intent in set(core.intents.values())]

  return intents

@app.post('/example')
def get_examples(example: NewExample):
  core.add_intent(example.example, example.intent)
  store_bot()
  return Response(status_code=HTTPStatus.OK)

@app.delete('/example')
def get_examples(example: RemoveExample):
  core.remove_intent(example.example)
  store_bot()
  return Response(status_code=HTTPStatus.OK) 

@app.get('/actions')
def get_actions():  
  return [{
      'name': a['action'].name,
      'description': a['action'].description,
      'settings': a['action'].settings,
      'active': a['active'],
  } for a in bot.actions]

@app.post('/actions')
def add_action(action: Action):  
  result = next(a for a in ACTIONS if a.name.lower() == action.name.lower())
  bot.add_action(action.intent, result(settings=action.settings))
  store_bot()
  return Response(status_code=HTTPStatus.OK)

@app.delete('/actions')
def delete_action(action: DeleteAction):
  bot.delete_action(action.intent)
  store_bot()
  return Response(status_code=HTTPStatus.OK)

@app.get('/name')
def get_name():
  return bot.name

@app.get('/available/actions')
def available_actions():
  return [{
      'name': action.name,
      'description': action.description
  } for action in ACTIONS]

def read_phrases():
  phrases_file = PHRASES_FILE
  phrases = {}
  if os.path.exists(phrases_file):
    with open(phrases_file) as handle:
      phrases = json.load(handle)
  return phrases

def update_phrases(phrases):
  phrases_file = PHRASES_FILE
  with open(phrases_file, 'w') as handle:
      json.dump(phrases, handle, indent=2, sort_keys=True)
  bot.update_actions()  

@app.get('/phrases')
def get_phrases():
  phrases = read_phrases()
  return phrases[bot.language]

@app.post('/phrases')
def add_phrases(list_of_phrases: ListOfPhrases):
  phrases = read_phrases()
  for phrase in list_of_phrases.phrases:
    if phrase.intent in phrases[bot.language]:
      phrases[bot.language][phrase.intent].append(phrase.text)
    else:
      phrases[bot.language][phrase.intent] = [phrase.text]
  update_phrases(phrases)
  return Response(status_code=HTTPStatus.OK)

@app.delete('/phrases')
def delete_phrases(list_of_phrases: ListOfPhrases):
  phrases = read_phrases()
  for phrase in list_of_phrases.phrases:
    if phrase.intent in phrases[bot.language]:
      phrases[bot.language][phrase.intent] = [text for text in phrases[bot.language][phrase.intent] if text != phrase.text]
  update_phrases(phrases)
  return Response(status_code=HTTPStatus.OK)
