import unittest

from radar_comercial.analysis import analyze_case, analyze_commercial_case
from radar_comercial.models import CommercialCase, RadarReport


class AnalyzeCommercialCaseTest(unittest.TestCase):
    def test_returns_report_model_from_domain_case(self):
        case = CommercialCase(
            company="Acme",
            objective="ordenar pipeline comercial",
            pain_points=["seguimiento manual", "oportunidades sin prioridad clara"],
            signals=[
                "pidió demo esta semana",
                "equipo comercial activo",
                "dolor operativo explícito",
            ],
            risks=["no tiene proceso consistente"],
        )

        report = analyze_commercial_case(case)

        self.assertIsInstance(report, RadarReport)
        self.assertEqual(report.priority, "alta")
        self.assertIn("Agendar demo enfocada en prioridades y siguientes pasos.", report.next_steps)

    def test_keeps_legacy_dict_interface(self):
        result = analyze_case(
            {
                "company": "Beta",
                "objective": "mejorar seguimiento",
                "pain_points": ["seguimiento manual"],
                "signals": ["interés inicial"],
                "risks": [],
            }
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["priority"], "media")


if __name__ == "__main__":
    unittest.main()
