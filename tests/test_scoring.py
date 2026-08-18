import unittest

from radar_comercial.analysis import analyze_commercial_case
from radar_comercial.models import CommercialCase


class AnalyzeCommercialCaseScoringTest(unittest.TestCase):
    def test_builds_explainable_score_breakdown_and_high_confidence(self):
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

        self.assertEqual(report.priority, "alta")
        self.assertEqual(report.confidence, "alta")
        self.assertGreaterEqual(report.score_total, 6)
        self.assertIn("interés activo", report.score_breakdown)
        self.assertIn("dolor operativo", report.score_breakdown)
        self.assertIn("riesgo declarado", report.score_breakdown)
        self.assertIn("Caso con señales suficientes para una demo orientada a cierre.", report.rationale)

    def test_returns_medium_confidence_when_signal_is_still_partial(self):
        case = CommercialCase(
            company="Beta",
            objective="mejorar seguimiento",
            pain_points=["seguimiento manual"],
            signals=["interés inicial"],
            risks=[],
        )

        report = analyze_commercial_case(case)

        self.assertEqual(report.priority, "media")
        self.assertEqual(report.confidence, "media")
        self.assertIn("Falta evidencia suficiente para una urgencia alta.", report.rationale)


if __name__ == "__main__":
    unittest.main()
