from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Union

from dataclasses_json import dataclass_json

@dataclass
class FrameConfig:
    # Frame duration in ms
    duration: int = 1000
    # List of either:
    # [begin, end, R, G, B], begin/end: [0.0, 1.0], RGB: [0, 255]
    # [begin, end, SPEC], where SPEC is an str specification
    colors: List[Union[Tuple[float, float, int, int, int], Tuple[float, float, str]]] = field(default_factory=list)

@dataclass_json
@dataclass
class ColorConfig:
    inner: List[FrameConfig] = field(default_factory=list)
    outer: List[FrameConfig] = field(default_factory=list)

@dataclass
class LoopConfig:
    count: int = 30
    offset: float = 0
    spacing: float = 16

@dataclass
class SerialConfig:
    port: Optional[str] = None
    baudrate: int = 115200
    reconn_wait: int = 2000
    update_wait: int = 10

@dataclass_json
@dataclass
class Config:
    serial: SerialConfig = field(default_factory=SerialConfig)
    diameter: float = 150
    inner_loop: LoopConfig = field(default_factory=LoopConfig)
    outer_loop: LoopConfig = field(default_factory=LoopConfig)
