from pydantic import BaseModel
from typing import Optional, List

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