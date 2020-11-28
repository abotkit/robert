import re

class AddIntentDataCollection:
    def extract(self, query):
        example = re.findall(r'"(.*?)"', query)
        query = query.replace('"', '')
        
        if example:
          query = query.replace(example[0], '')

        intent = re.search(r'{} (\S+)'.format('intent'), query.lower())
        if not intent:
          intent = re.search(r'{} (\S+)'.format('vorhaben'), query.lower())

        return {
          'new_example': example[0] if example else '',
          'target_intent': intent.group(1) if intent else ''
        }


def main():
    dataCollection = AddIntentDataCollection()
    sentence_1 = '"Hello boy" is also an example for Intent hello'
    sentence_2 = '"Moin Moin!" kann man auch sagen für das Vorhaben "hello"'
    sentence_3 = 'Moin Moin! kann man auch sagen für das Vorhaben hello'

    matches_1 = dataCollection.extract(sentence_1)
    matches_2 = dataCollection.extract(sentence_2)
    matches_3 = dataCollection.extract(sentence_3)
    print("MATCH: {}".format(matches_1))
    print("MATCH: {}".format(matches_2))
    print("MATCH: {}".format(matches_3))

    if not matches_2['new_example']:
      print('no example found for sentence 2')

    if not matches_3['new_example']:
      print('no example found for sentence 3')

if __name__ == '__main__':
    main()