import unittest

from radar_comercial.analysis import analyze_case


class AnalyzeCaseTest(unittest.TestCase):
    def test_returns_actionable_reading_for_high_priority_case(self):
        result = analyze_case(
            {
                "company": "Acme",
                "objective": "ordenar pipeline comercial",
                "pain_points": [
                    "seguimiento manual",
                    "oportunidades sin prioridad clara",
                ],
                "signals": [
                    "pidió demo esta semana",
                    "equipo comercial activo",
                    "dolor operativo explícito",
                ],
                "risks": ["no tiene proceso consistente"],
            }
        )

        self.assertEqual(result["summary"], "Acme necesita ordenar pipeline comercial.")
        self.assertEqual(result["priority"], "alta")
        self.assertIn("pidió demo esta semana", result["signals_positive"])
        self.assertIn("no tiene proceso consistente", result["signals_risk"])
        self.assertIn("Agendar demo enfocada en prioridades y siguientes pasos.", result["next_steps"])

    def test_returns_medium_priority_when_case_has_interest_but_weak_urgency(self):
        result = analyze_case(
            {
                "company": "Beta",
                "objective": "mejorar seguimiento",
                "pain_points": ["seguimiento manual"],
                "signals": ["interés inicial"],
                "risks": [],
            }
        )

        self.assertEqual(result["priority"], "media")
        self.assertIn("Validar urgencia real y criterio de compra.", result["next_steps"])

    def test_requires_minimum_context_to_analyze_case(self):
        with self.assertRaises(ValueError):
            analyze_case({"company": "Gamma"})


if __name__ == "__main__":
    unittest.main()
