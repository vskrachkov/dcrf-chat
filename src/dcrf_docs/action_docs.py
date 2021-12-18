import dataclasses
from typing import Iterable, Optional

from rest_framework.serializers import Serializer


@dataclasses.dataclass
class ActionDocs:
    publish: Serializer
    subscribe: Optional[Iterable[Serializer]] = None
    description: str = ""
