from __future__ import annotations

import math
import unittest

from ome.analysis import (
    PacejkaMagicFormula,
    PacejkaParameters,
    SlipCoordinate,
    TireForceAxis,
    TireModelRequest,
)


class PureSlipTireModelTests(unittest.TestCase):
    def test_classic_magic_formula_matches_known_analytic_value(self) -> None:
        model = PacejkaMagicFormula()
        parameters = PacejkaParameters(
            force_axis=TireForceAxis.LATERAL,
            slip_coordinate=SlipCoordinate.LATERAL_SLIP_ANGLE_RAD,
            b=1.0,
            c=1.0,
            d_n=1000.0,
            e=0.0,
        )

        result = model.evaluate(
            TireModelRequest(
                force_axis=TireForceAxis.LATERAL,
                slip_coordinate=SlipCoordinate.LATERAL_SLIP_ANGLE_RAD,
                slip_value=1.0,
            ),
            parameters,
        )

        self.assertAlmostEqual(result.force_n, 1000.0 / math.sqrt(2.0), places=12)
        self.assertEqual(result.model_id, "pacejka.magic_formula.classic")
        self.assertEqual(result.model_version, "0.1.0")
        self.assertEqual(result.force_axis, TireForceAxis.LATERAL)
        self.assertEqual(result.slip_coordinate, SlipCoordinate.LATERAL_SLIP_ANGLE_RAD)
        self.assertEqual(result.input_slip_value, 1.0)
        self.assertEqual(result.effective_slip_value, 1.0)

    def test_horizontal_and_vertical_shifts_are_explicit_in_result(self) -> None:
        model = PacejkaMagicFormula()
        parameters = PacejkaParameters(
            force_axis=TireForceAxis.LONGITUDINAL,
            slip_coordinate=SlipCoordinate.LONGITUDINAL_SLIP_RATIO,
            b=2.0,
            c=1.0,
            d_n=500.0,
            e=0.0,
            horizontal_shift=0.1,
            vertical_shift_n=25.0,
        )

        result = model.evaluate(
            TireModelRequest(
                force_axis=TireForceAxis.LONGITUDINAL,
                slip_coordinate=SlipCoordinate.LONGITUDINAL_SLIP_RATIO,
                slip_value=0.4,
            ),
            parameters,
        )

        expected = 500.0 * math.sin(math.atan(2.0 * 0.5)) + 25.0
        self.assertAlmostEqual(result.force_n, expected, places=12)
        self.assertEqual(result.input_slip_value, 0.4)
        self.assertEqual(result.effective_slip_value, 0.5)

    def test_longitudinal_and_lateral_parameter_semantics_cannot_be_mixed(self) -> None:
        model = PacejkaMagicFormula()
        parameters = PacejkaParameters(
            force_axis=TireForceAxis.LATERAL,
            slip_coordinate=SlipCoordinate.LATERAL_TAN_SLIP_ANGLE,
            b=8.0,
            c=1.3,
            d_n=3200.0,
            e=-0.2,
        )

        with self.assertRaisesRegex(ValueError, "force axis"):
            model.evaluate(
                TireModelRequest(
                    force_axis=TireForceAxis.LONGITUDINAL,
                    slip_coordinate=SlipCoordinate.LATERAL_TAN_SLIP_ANGLE,
                    slip_value=0.05,
                ),
                parameters,
            )

    def test_slip_coordinate_convention_must_match_calibration(self) -> None:
        model = PacejkaMagicFormula()
        parameters = PacejkaParameters(
            force_axis=TireForceAxis.LATERAL,
            slip_coordinate=SlipCoordinate.LATERAL_SLIP_ANGLE_RAD,
            b=8.0,
            c=1.3,
            d_n=3200.0,
            e=-0.2,
        )

        with self.assertRaisesRegex(ValueError, "slip-coordinate"):
            model.evaluate(
                TireModelRequest(
                    force_axis=TireForceAxis.LATERAL,
                    slip_coordinate=SlipCoordinate.LATERAL_TAN_SLIP_ANGLE,
                    slip_value=math.tan(0.05),
                ),
                parameters,
            )

    def test_non_finite_parameter_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite"):
            PacejkaParameters(
                force_axis=TireForceAxis.LATERAL,
                slip_coordinate=SlipCoordinate.LATERAL_SLIP_ANGLE_RAD,
                b=math.inf,
                c=1.3,
                d_n=3200.0,
                e=-0.2,
            )

    def test_non_finite_request_slip_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite"):
            TireModelRequest(
                force_axis=TireForceAxis.LONGITUDINAL,
                slip_coordinate=SlipCoordinate.LONGITUDINAL_SLIP_RATIO,
                slip_value=math.nan,
            )

    def test_equivalent_inputs_produce_equivalent_results(self) -> None:
        model = PacejkaMagicFormula()
        parameters = PacejkaParameters(
            force_axis=TireForceAxis.LONGITUDINAL,
            slip_coordinate=SlipCoordinate.LONGITUDINAL_SLIP_RATIO,
            b=10.0,
            c=1.7,
            d_n=4500.0,
            e=0.15,
        )
        request = TireModelRequest(
            force_axis=TireForceAxis.LONGITUDINAL,
            slip_coordinate=SlipCoordinate.LONGITUDINAL_SLIP_RATIO,
            slip_value=0.08,
        )

        first = model.evaluate(request, parameters)
        second = model.evaluate(request, parameters)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
