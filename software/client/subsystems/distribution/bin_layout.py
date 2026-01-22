from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


class BinSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    BIG = "big"


@dataclass
class Bin:
    size: BinSize
    category_id: Optional[str] = None


@dataclass
class BinSection:
    bins: List[Bin] = field(default_factory=list)


@dataclass
class Layer:
    sections: List[BinSection] = field(default_factory=list)


@dataclass
class DistributionLayout:
    layers: List[Layer] = field(default_factory=list)


def mkDefaultLayout() -> DistributionLayout:
    sections = []
    for _ in range(6):
        bins = [Bin(size=BinSize.SMALL) for _ in range(3)]
        sections.append(BinSection(bins=bins))
    layer = Layer(sections=sections)
    return DistributionLayout(layers=[layer])
