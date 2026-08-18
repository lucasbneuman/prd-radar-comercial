import unittest

from radar_comercial.models import RadarReport
from radar_comercial.presenter import render_radar_report_markdown


class RenderRadarReportMarkdownTest(unittest.TestCase):
    def test_renders_from_report_model(self):
        report = RadarReport(
            summary="Acme necesita ordenar pipeline comercial.",
            priority="alta",
            signals_positive=["pidió demo esta semana"],
            signals_risk=["no tiene proceso consistente"],
            next_steps=["Agendar demo enfocada en prioridades y siguientes pasos."],
        )

        markdown = render_radar_report_markdown(report)

        self.assertIn("# Radar Comercial", markdown)
        self.assertIn("**Prioridad:** alta", markdown)
        self.assertIn("- pidió demo esta semana", markdown)


if __name__ == "__main__":
    unittest.main()
