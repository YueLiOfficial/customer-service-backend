from dataclasses import dataclass


@dataclass(slots=True)
class FLowLink:
    target: str

@dataclass(slots=True)
class StaticFlowLink(FLowLink):
    ...

@dataclass(slots=True)
class ConditionalFlowLink(FLowLink):
    condition: str

@dataclass(slots=True)
class FallbackFlowLink(FLowLink):
    ...