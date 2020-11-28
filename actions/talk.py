import json
from random import choice
import os
from actions.Action import Action

class TalkAction(Action):
    name = "Talk"
    description = """
    Just answers predefined phrases
    """.strip()

    def __read_phrases(self):
        phrases = os.path.join(os.path.dirname(os.path.abspath( __file__ )), 'phrases.json')
        with open(phrases) as handle:
            self.answers = json.load(handle)

    def __init__(self, settings={}):
        self.name = TalkAction.name
        self.description = TalkAction.description
        super().__init__(settings)
        self.__read_phrases()

    def update(self):
        self.__read_phrases()

    def execute(self, query, intent=None, extra={}):
        if extra['language'] == 'de':
            if intent in self.answers['de']:
                answer = choice(self.answers['de'][intent])
                return answer.replace('${name}', self.settings['bot_name'])
            else:
                return 'Das sieht nach gar nichts aus für mich'
        else:
            if intent in self.answers['en']:
                answer = choice(self.answers['en'][intent])
                return answer.replace('${name}', self.settings['bot_name'])
            else:
                return 'Doesn\'t look like anything to me'


def main():
    action = TalkAction()
    print(action.execute('hello, world', 'hello'))


if __name__ == '__main__':
    main()
