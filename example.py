from dataclasses import asdict, dataclass
from restiny import restiny, RestModelBase, RestModelEndpoint, DataManager


class InMemoryManager(DataManager):
    def __init__(self):
        self._data = {}

    def write(self, **data):
        if 'key' in data:
            self._data[data.pop('key')] = data

    def read(self, key):
        return self._data.get(key, {})

    def delete(self, key):
        if key in self._data:
            del self._data[key]


@dataclass
class TestRestModel(RestModelBase):
    word: str
    number: int



class TestEndpoint(RestModelEndpoint):
    base_path = 'test'



app = restiny()
app.register(
    TestEndpoint(
        manager=InMemoryManager(),
        model=TestRestModel
    )
)

