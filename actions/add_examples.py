from actions.Action import Action

responses = {
  'de': {
    'MISSING_INTENT_NAME': 'Ich konnte leider den Namen für das neue Vorhaben nicht verstehen.',
    'MISSING_EXAMPLE': 'Ich konnte das neue Beispiel leider nicht aus deinem Satz herauslesen. Du machst es mir einfacher, wenn du doppelte Anführungszeichen für das Beispiel verwendest.?',
    'SUCCESS': 'Ich habe das Beispiel "{}" für das Vorhaben {} gelernt'
  },
  'en': {
    'MISSING_INTENT_NAME': 'Unfortunately I could not understand the name for the new intent.',
    'MISSING_EXAMPLE': 'Unfortunately I could not read the new example from your sentence. If you use quotes for the example, you make it easier for me.',
    'SUCCESS': 'I\'ve successfully learned the example "{}" for intent "{}"'
  }
}

class AddExampleAction(Action):
    name = "Add Example"
    description = """
    Adds a new intent to robert
    """.strip()

    def __init__(self, settings={}):
      self.name = AddExampleAction.name
      self.description = AddExampleAction.description
      super().__init__(settings) 

    def execute(self, query, intent=None, extra={}):
      language = extra['language']

      if 'target_intent' not in extra['data_collection']:
        return responses[language]['MISSING_INTENT_NAME']

      if 'new_example' not in extra['data_collection']:
        return responses[language]['MISSING_EXAMPLE']

      extra['core'].add_intent(extra['data_collection']['new_example'], extra['data_collection']['target_intent'])
      return responses[language]['SUCCESS'].format(extra['data_collection']['new_example'], extra['data_collection']['target_intent'])
