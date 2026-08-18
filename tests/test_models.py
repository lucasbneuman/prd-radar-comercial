import unittest

from radar_comercial.models import CommercialCase, RadarReport


class CommercialCaseTest(unittest.TestCase):
    def test_builds_case_from_dict(self):
        case = CommercialCase.from_dict(
            {
                "company": "Acme",
                "objective": "ordenar pipeline comercial",
                "pain_points": ["seguimiento manual"],
                "signals": ["pidió demo esta semana"],
                "risks": ["no tiene proceso consistente"],
            }
        )

        self.assertEqual(case.company, "Acme")
        self.assertEqual(case.objective, "ordenar pipeline comercial")
        self.assertEqual(case.pain_points, ["seguimiento manual"])
        self.assertEqual(case.signals, ["pidió demo esta semana"])
        self.assertEqual(case.risks, ["no tiene proceso consistente"])
        self.assertEqual(case.case_type, "generic")

    def test_rejects_missing_required_fields(self):
        with self.assertRaises(ValueError):
            CommercialCase.from_dict({"company": "Acme"})


class RadarReportTest(unittest.TestCase):
    def test_converts_report_to_dict(self):
        report = RadarReport(
            summary="Acme necesita ordenar pipeline comercial.",
            priority="alta",
            confidence="media",
            score_total=0,
            score_breakdown=[],
            rationale="",
            signals_positive=["pidió demo esta semana"],
            signals_risk=["no tiene proceso consistente"],
            next_steps=["Agendar demo enfocada en prioridades y siguientes pasos."],
            case_type="generic",
        )

        self.assertEqual(
            report.to_dict(),
            {
                "summary": "Acme necesita ordenar pipeline comercial.",
                "priority": "alta",
                "confidence": "media",
                "score_total": 0,
                "score_breakdown": [],
                "rationale": "",
                "signals_positive": ["pidió demo esta semana"],
                "signals_risk": ["no tiene proceso consistente"],
                "next_steps": ["Agendar demo enfocada en prioridades y siguientes pasos."],
                "case_type": "generic",
            },
        )


if __name__ == "__main__":
    unittest.main()
