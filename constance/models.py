from json.decoder import WHITESPACE
from json.decoder import JSONDecoder

from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from picklefield import PickledObjectField
except ImportError:
    raise ImproperlyConfigured(
        "Couldn't find the the 3rd party app "
        'django-picklefield which is required for '
        'the constance database backend.'
    ) from None


class ConstanceEncoder(DjangoJSONEncoder):
    def encode(self, o):
        return f'{{"__type__": "{type(o).__name__}", "value": {super().encode(o)}}}'


class ConstanceDecoder(JSONDecoder):
    def decode(self, s, _w=WHITESPACE.match):
        a = super().decode(s, _w)
        if isinstance(a, dict) and '__type__' in a:
            return a['value']
        return a


class Constance(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = PickledObjectField(null=True, blank=True)
    value_json = models.JSONField(
        default=None, blank=True, null=True, encoder=ConstanceEncoder, decoder=ConstanceDecoder
    )

    class Meta:
        verbose_name = _('constance')
        verbose_name_plural = _('constances')
        permissions = [
            ('change_config', 'Can change config'),
            ('view_config', 'Can view config'),
        ]

    def __str__(self):
        return self.key
