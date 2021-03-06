from actions.Action import Action

class ShoutAction(Action):
    name = "Shout"
    description = """
    A simple shout action. Used as an example
    """.strip()

    def __init__(self, settings={}):
        self.name = ShoutAction.name
        self.description = ShoutAction.description
        super().__init__(settings) 

    def execute(self, query, intent=None, extra={}):
        return query.upper()


def main():
    action = ShoutAction()
    print(action.execute('hello, world'))


if __name__ == '__main__':
    main()
