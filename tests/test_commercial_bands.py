import unittest

from radar_comercial.analysis import analyze_commercial_case
from radar_comercial.models import CommercialCase


class CommercialBandsTest(unittest.TestCase):
    def test_assigns_critical_priority_for_urgent_enterprise_case(self):
        case = CommercialCase(
            company="EnterpriseCo",
            objective="evitar fuga de oportunidades críticas",
            pain_points=["seguimiento manual", "fuga de oportunidades"],
            signals=["pidió demo esta semana", "equipo comercial activo", "urgencia de cierre este mes"],
            risks=["pipeline roto"],
            case_type="inbound_hot",
        )

        report = analyze_commercial_case(case)

        self.assertEqual(report.priority, "critica")
        self.assertEqual(report.confidence, "alta")
        self.assertIn("urgencia de cierre", report.score_breakdown)

    def test_assigns_low_priority_for_weak_cold_case(self):
        case = CommercialCase(
            company="ColdCo",
            objective="explorar seguimiento",
            pain_points=[],
            signals=[],
            risks=[],
            case_type="outbound_cold",
        )

        report = analyze_commercial_case(case)

        self.assertEqual(report.priority, "baja")
        self.assertEqual(report.confidence, "baja")
        self.assertIn("evidencia insuficiente", report.rationale.lower())


if __name__ == "__main__":
    unittest.main()
