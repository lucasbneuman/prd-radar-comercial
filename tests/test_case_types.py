import unittest

from radar_comercial.analysis import analyze_commercial_case
from radar_comercial.models import CommercialCase


class CommercialCaseTypesTest(unittest.TestCase):
    def test_prioritizes_hot_inbound_case(self):
        case = CommercialCase(
            company="Acme",
            objective="ordenar pipeline comercial",
            pain_points=["seguimiento manual", "oportunidades sin prioridad clara"],
            signals=["pidió demo esta semana", "equipo comercial activo"],
            risks=["no tiene proceso consistente"],
            case_type="inbound_hot",
        )

        report = analyze_commercial_case(case)

        self.assertEqual(report.case_type, "inbound_hot")
        self.assertEqual(report.priority, "alta")
        self.assertIn("tipo de caso: inbound_hot", report.score_breakdown)

    def test_keeps_outbound_cold_case_in_lower_band(self):
        case = CommercialCase(
            company="Beta",
            objective="mejorar seguimiento",
            pain_points=["seguimiento manual"],
            signals=["interés inicial"],
            risks=[],
            case_type="outbound_cold",
        )

        report = analyze_commercial_case(case)

        self.assertEqual(report.case_type, "outbound_cold")
        self.assertEqual(report.priority, "media")
        self.assertEqual(report.confidence, "media")
        self.assertIn("tipo de caso: outbound_cold", report.score_breakdown)


if __name__ == "__main__":
    unittest.main()
