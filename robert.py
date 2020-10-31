from http import HTTPStatus
from typing import Optional, List
from fastapi import FastAPI, Response, Body, Request
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel

import os
import pickle
import json

from actions.actions import ACTIONS
from persistence.bot_reader import BotReader
from persistence.bot_writer import BotWriter

app = FastAPI()

bot = None
core = None

CACHE_PATH = 'bot.pkl'
CONFIGURATION = 'bot.json'
PHRASES_FILE = os.path.join('actions', 'phrases.json')
HAS_UPDATES = False

class Message(BaseModel):
  query: str
  identifier: Optional[str] = None

class Language(BaseModel):
  country_code: str

class NewExample(BaseModel):
  example: str
  intent: str

class RemoveExample(BaseModel):
  example: str

class Action(BaseModel):
  name: str
  settings: str
  intent: str

class DeleteAction(BaseModel):
  intent: str

class Phrase(BaseModel):
  intent: str
  text: str

class ListOfPhrases(BaseModel):
  phrases: List[Phrase]

class BotMeta(BaseModel):
  name: str

def cache_bot():
  with open(CACHE_PATH, "wb") as handle:
    pickle.dump(bot, handle)

def store_bot():
  global HAS_UPDATES
  HAS_UPDATES = True

@app.on_event("startup")
@repeat_every(seconds=60*5)
def store_files() -> None:
  global HAS_UPDATES
  if HAS_UPDATES:
    BotWriter(bot).write(CONFIGURATION)
    HAS_UPDATES = False
    cache_bot()
    # TODO: Push files to MinIO

@app.on_event("startup")
def startup_event():
  global bot
  global core

  if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "rb") as handle:
      bot = pickle.load(handle)
      core = bot.core
  else:
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
  return {
    "recipient_id": message.identifier,
    "text": bot.handle(message.query)
  }

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

@app.get('/example/{intent}')
def intent_examples(intent: str):
    examples = []
    for example in core.intents:
        if intent == core.intents[example]:
            examples.append(example)
    return examples

@app.get('/example')
def get_examples():
  return core.intents

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
  result = next(a for a in ACTIONS if a.name == action.name)
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

@app.post('/name')
def set_name(meta: BotMeta):
  bot.name = meta.name
  store_bot()
  return Response(status_code=HTTPStatus.OK)

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
