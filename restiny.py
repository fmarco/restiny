from collections import OrderedDict, namedtuple
import simplejson as json
import werkzeug
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from dataclasses import asdict, dataclass

ResponseData = namedtuple('ResponseData', 'status data')


class NotAllowedMethodException(Exception):
    pass


class DataManager:
    def write(self, **data):
        pass

    def read(self, **data):
        pass

    def delete(self, key):
        pass


@dataclass
class RestModelBase:
    id: int

    def to_dict(self):
        _representation = asdict(self)
        _representation['key'] = _representation['id']
        return _representation


class RestModelEndpoint:
    base_path = None

    _methods = {
        'post': {
            'callback': 'create',
            'path': '/create'
        },
        'get': {
            'callback': 'retrieve',
            'path': '/retrieve/<id>'
        },
        'put': {
            'callback': 'modify',
            'path': '/modify/<id>'
        },
        'patch': {
            'callback': 'modify',
            'path': '/modify/<id>'
        },
        'delete': {
            'callback': 'delete',
            'path': '/delete/<id>'
        }
    }

    def __init__(self, manager, model, *args, **kwargs):
        self.methods = self._methods.copy()
        self.manager = manager
        self.model = model

    def resolve(self, request, *args, **kwargs):
        http_method = request.method
        method_info = self.methods.get(http_method.lower())
        if method_info is None:
            raise NotAllowedMethodException
        callback = method_info.get('callback')
        return getattr(self, callback, None)(request, *args, **kwargs)
        result = json.dumps(result)
        return result
    
    def get_urls(self):
        return [
            Rule(
                f'/{self.base_path}{info.get("path")}',
                endpoint=self.base_path
            ) for method, info in self.methods.items()
        ]

    def create(self, request, **kwargs):
        data = self.model(**json.loads(request.data))
        data_dict = data.to_dict()
        self.manager.write(**data_dict)
        return self._process_result(status=201, data=data_dict)

    def modify(self, request, id, **kwargs):
        id = int(id)
        data = self.model(key=id, **json.loads(request.data))
        data_dict = data.to_dict()
        self.manager.write(**data_dict)
        return self._process_result(status=200, data=data_dict)

    def retrieve(self, request, id, **kwargs):
        id = int(id)
        return self._process_result(status=200, data=self.manager.read(key=id))

    def delete(self, request, id):
        id = int(id)
        self.manager.delete(key=id)
        return self._process_result(status=200, data=None)

    def _process_result(self, status, data):
        data = json.dumps(data)
        return ResponseData(status=status, data=data)


class restiny:

    def __init__(self, *args, **kwargs):
        self.endpoints = {}
        self.url_map = Map()

    def run(self, host='127.0.0.1', port=8000, is_debug=False, reloading=False):
        run_simple(host, port, self, use_debugger=is_debug, use_reloader=reloading)
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint_name, values = adapter.match()
        endpoint = self.endpoints.get(endpoint_name)
        result = endpoint.resolve(request, **values)
        return Response(
            response=result.data,
            status=result.status,
            mimetype='application/json'
        )

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    def register(self, endpoint_instance):
        self.endpoints[endpoint_instance.base_path] = endpoint_instance
        for rule in endpoint_instance.get_urls():
            self.url_map.add(rule)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
