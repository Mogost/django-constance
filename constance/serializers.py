"""JSON Serialization Utilities."""

from __future__ import annotations

import json
import logging
import pickle
import uuid
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from typing import Any
from typing import Protocol
from typing import TypeVar

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Django-constance custom json encoder."""

    def default(self, o):
        for t, (marker, encoder) in _encoders.items():
            if isinstance(o, t):
                if marker is None:
                    raise ValueError('Type registered without marker')
                return _as(marker, encoder(o))
        raise TypeError(f'Object of type {o.__class__.__name__} is not JSON serializable')


def _as(t: str, v: Any):
    return {'__type__': t, '__value__': v}


def dumps(s, _dumps=json.dumps, cls=JSONEncoder, default_kwargs=None, **kwargs):
    """Serialize object to json string."""
    default_kwargs = default_kwargs or {}
    if isinstance(s, (str, int, bool, float, type(None))):
        s = {'__type__': 'default', '__value__': s}
    return _dumps(s, cls=cls, **dict(default_kwargs, **kwargs))


def loads(s, _loads=json.loads, **kwargs):
    """Deserialize json string to object."""
    return _loads(s, object_hook=object_hook, **kwargs)


def object_hook(o: dict) -> Any:
    """Hook function to perform custom deserialization."""
    if o.keys() == {'__type__', '__value__'}:
        if o['__type__'] == 'default':
            return o['__value__']
        decoder = _decoders.get(o['__type__'])
        if not decoder:
            raise ValueError('Unsupported type', type, o)
        return decoder(o['__value__'])
    try:
        return pickle.loads(o)
    except TypeError:
        logger.error('Unknown object %r', o)
        raise


T = TypeVar('T')


class Encoder(Protocol[T]):
    def __call__(self, value: T, /) -> str: ...


class Decoder(Protocol[T]):
    def __call__(self, value: str, /) -> T: ...


def register_type(
    t: type[T],
    marker: str,
    encoder: Encoder[T],
    decoder: Decoder[T],
):
    if not marker:
        raise ValueError('Marker must be specified')
    if _decoders.get(marker) or marker == 'default':
        raise ValueError('Type already registered')
    _encoders[t] = (marker, encoder)
    _decoders[marker] = decoder


_encoders: dict[type, tuple[str, Encoder]] = {}
_decoders: dict[str, Decoder] = {}


def _register_default_types():
    # NOTE: datetime should be registered before date, because datetime is also instance of date.
    register_type(datetime, 'datetime', datetime.isoformat, datetime.fromisoformat)
    register_type(date, 'date', lambda o: o.isoformat(), lambda o: datetime.fromisoformat(o).date())
    register_type(time, 'time', lambda o: o.isoformat(), time.fromisoformat)
    register_type(Decimal, 'decimal', str, Decimal)
    register_type(uuid.UUID, 'uuid', lambda o: o.hex, lambda o: uuid.UUID(o))
    register_type(timedelta, 'timedelta', lambda o: o.total_seconds(), lambda o: timedelta(seconds=o))


_register_default_types()
