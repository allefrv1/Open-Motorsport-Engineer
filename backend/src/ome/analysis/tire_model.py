from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TypeVar


class TireForceAxis(StrEnum):
    LONGITUDINAL = "longitudinal"
    LATERAL = "lateral"


class SlipCoordinate(StrEnum):
    LONGITUDINAL_SLIP_RATIO = "longitudinal_slip_ratio"
    LATERAL_SLIP_ANGLE_RAD = "lateral_slip_angle_rad"
    LATERAL_TAN_SLIP_ANGLE = "lateral_tan_slip_angle"


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class TireModelRequest:
    force_axis: TireForceAxis
    slip_coordinate: SlipCoordinate
    slip_value: float

    def __post_init__(self) -> None:
        _require_finite("slip_value", self.slip_value)


@dataclass(frozen=True, slots=True)
class TireModelResult:
    force_axis: TireForceAxis
    slip_coordinate: SlipCoordinate
    input_slip_value: float
    effective_slip_value: float
    force_n: float
    model_id: str
    model_version: str


@dataclass(frozen=True, slots=True)
class PacejkaParameters:
    force_axis: TireForceAxis
    slip_coordinate: SlipCoordinate
    b: float
    c: float
    d_n: float
    e: float
    horizontal_shift: float = 0.0
    vertical_shift_n: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("b", self.b),
            ("c", self.c),
            ("d_n", self.d_n),
            ("e", self.e),
            ("horizontal_shift", self.horizontal_shift),
            ("vertical_shift_n", self.vertical_shift_n),
        ):
            _require_finite(name, value)


ParametersT = TypeVar("ParametersT", contravariant=True)


class TireModel(Protocol[ParametersT]):
    def evaluate(
        self,
        request: TireModelRequest,
        parameters: ParametersT,
    ) -> TireModelResult: ...


class PacejkaMagicFormula:
    MODEL_ID = "pacejka.magic_formula.classic"
    MODEL_VERSION = "0.1.0"

    def evaluate(
        self,
        request: TireModelRequest,
        parameters: PacejkaParameters,
    ) -> TireModelResult:
        if request.force_axis != parameters.force_axis:
            raise ValueError(
                "request force axis does not match the Pacejka parameter-set force axis"
            )
        if request.slip_coordinate != parameters.slip_coordinate:
            raise ValueError(
                "request slip-coordinate convention does not match the Pacejka parameter set"
            )

        x = request.slip_value + parameters.horizontal_shift
        bx = parameters.b * x
        force_n = (
            parameters.d_n
            * math.sin(parameters.c * math.atan(bx - parameters.e * (bx - math.atan(bx))))
            + parameters.vertical_shift_n
        )

        return TireModelResult(
            force_axis=request.force_axis,
            slip_coordinate=request.slip_coordinate,
            input_slip_value=request.slip_value,
            effective_slip_value=x,
            force_n=force_n,
            model_id=self.MODEL_ID,
            model_version=self.MODEL_VERSION,
        )
