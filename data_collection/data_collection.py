from data_collection.locations import LocationDataCollection
from data_collection.files import FileDataCollection
from data_collection.add_intent import AddIntentDataCollection

COLLECTORS = [
    LocationDataCollection(),
    FileDataCollection(),
    AddIntentDataCollection()
]
