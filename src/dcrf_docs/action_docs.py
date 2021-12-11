import dataclasses
from typing import Optional

from rest_framework.serializers import Serializer


@dataclasses.dataclass
class ActionDocs:
    serializer: Serializer
    name: Optional[str] = None
    description: Optional[str] = None
