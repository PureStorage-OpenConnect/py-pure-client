class __LazyLoader:
    'thin shell class to wrap modules.  load real module on first access and pass thru'

    def __init__ (self, modname) :
        self._modname  = modname
        self._mod      = None

    def __getattr__ (self, attr) :
        'import module on first attribute access'
        import importlib
        if self._mod is None :
            self._mod = importlib.import_module(self._modname)
        return getattr(self._mod, attr)

flasharray = __LazyLoader("pypureclient.flasharray")
flashblade = __LazyLoader("pypureclient.flashblade")
pure1      = __LazyLoader("pypureclient.pure1")

from .exceptions import PureError
from .properties import Property, Filter
from .responses import ValidResponse, ErrorResponse, ApiError, ResponseHeaders
from ._version import __version__
