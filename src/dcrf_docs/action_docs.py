import dataclasses
from typing import Iterable, Optional

from rest_framework.serializers import Serializer


@dataclasses.dataclass
class ActionDocs:
    sub: Serializer
    pub: Optional[Iterable[Serializer]] = None
    name: Optional[str] = None
    description: str = ""
