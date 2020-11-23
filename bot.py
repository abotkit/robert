from data_collection.data_collection import COLLECTORS
from actions.actions import ACTIONS


class Bot:
    def __init__(self, core, name='<no name>', language='en', id='00000000-000-0000-0000-000000000000'):
        self.name = name
        self.core = core
        self.id = id
        self.language = language
        self.actions = [{
            'action': a(settings={
                "bot_name": name
            }),
            'active': False,
        } for a in ACTIONS]

    def _find_action_by_name(self, action_name):
        return next(a for a in self.actions if a['action'].name == action_name)

    def find_action_by_intent(self, intent):
        return next((
            a for a in self.actions
            if a['active'] is not False and intent in a['active']['intents']), None)

    def update_actions(self):
        for action in self.actions:
            action['action'].update()

    def add_action(self, intent, action):
        result = self._find_action_by_name(action.name)
        if result['active'] is not False:
            result['active']['intents'].append(intent)
        else:
            result['active'] = {'intents': [intent]}

    def delete_action(self, intent):
        result = self._find_action_by_name(action.name)
        if result['active'] is not False:
            if intent in result['active']['intents']:
                result['active']['intents'].remove(intent)
            if len(result['active']['intents']) == 0:
                result['active'] = False

    def explain(self, query):
        explanation = {'query': query}

        result = self.core.intent_of(query)
        explanation = {**explanation, **result}

        intent = result['intent']
        if intent is None:
            return explanation

        action = self.find_action_by_intent(intent)['action']

        if action is not None:
            explanation['action'] = {
                'name': action.name,
                'description': action.description,
                'settings': action.settings,
                'data_collection': self.__data_collection(query),
            }

        return explanation

    def __data_collection(self, query):
        collected = {}

        for c in COLLECTORS:
            collected.update(c.extract(query))

        return collected

    def handle(self, query):
        result = self.core.intent_of(query)
        intent = result['intent']

        if intent is None:
            raise Exception('No intent detected')

        action = self.find_action_by_intent(intent)['action']

        if action is None:
            raise Exception('No action found')

        data_collection = self.__data_collection(query)
        return action.execute(query, intent=intent, data_collection=data_collection, language=self.language)
