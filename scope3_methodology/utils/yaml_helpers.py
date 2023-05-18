""" Yaml dump helper to represent decimals """

# pylint: disable=consider-using-f-string
import re
from decimal import Decimal

import yaml
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import BaseResolver
from yaml.resolver import Resolver as DefaultResolver
from yaml.scanner import Scanner


class Resolver(BaseResolver):
    """Resolver is identical to the base resolver"""


Resolver.add_implicit_resolver(  # regex copied from yaml source
    "!decimal",
    re.compile(
        r"""^(?:
        [-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?
        |\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-9]?[0-9])+\.[0-9_]*
        |[-+]?\.(?:inf|Inf|INF)
        |\.(?:nan|NaN|NAN)
    )$""",
        re.VERBOSE,
    ),
    list("-+0123456789."),
)

for ch, vs in DefaultResolver.yaml_implicit_resolvers.items():
    Resolver.yaml_implicit_resolvers.setdefault(ch, []).extend(
        (tag, regexp) for tag, regexp in vs if not tag.endswith("float")
    )


class Loader(Reader, Scanner, Parser, Composer, SafeConstructor, Resolver):
    """Yaml Loader"""

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)
        Resolver.__init__(self)


def decimal_constructor(loader, node):
    """
    Custom constuctore for reading Decimal values
    """
    value = loader.construct_scalar(node)
    return Decimal(value)


def represent_decimal(self, data: Decimal):
    """
    Custom representer for dumping Decimal values
    """
    value = "{:.9f}".format(data)
    return self.represent_scalar("tag:yaml.org,2002:float", value)


yaml.add_constructor("!decimal", decimal_constructor, Loader)
yaml.add_representer(Decimal, represent_decimal)


def yaml_load(stream, **kwargs):
    """Custom yaml load to correctly read Decimal fields"""
    return yaml.load(stream, Loader, **kwargs)  # type: ignore


def yaml_dump(obj: object):
    """Custom yaml dump to correctly write Decimal fields"""
    # Do not print tags, produces invalid yaml
    yaml.emitter.Emitter.process_tag = lambda *args: False  # type: ignore
    # Print all values without pointers and aliases
    yaml.Dumper.ignore_aliases = lambda *args: True  # type: ignore
    return yaml.dump(obj, default_flow_style=False, Dumper=yaml.Dumper)
