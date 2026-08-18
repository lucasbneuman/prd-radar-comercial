import unittest

from radar_comercial.presenter import render_report_markdown


class RenderReportMarkdownTest(unittest.TestCase):
    def test_renders_visible_report_for_demo(self):
        markdown = render_report_markdown(
            {
                "summary": "Acme necesita ordenar pipeline comercial.",
                "priority": "alta",
                "signals_positive": ["pidió demo esta semana", "equipo comercial activo"],
                "signals_risk": ["no tiene proceso consistente"],
                "next_steps": ["Agendar demo enfocada en prioridades y siguientes pasos."],
            }
        )

        self.assertIn("# Radar Comercial", markdown)
        self.assertIn("**Prioridad:** alta", markdown)
        self.assertIn("## Señales positivas", markdown)
        self.assertIn("- pidió demo esta semana", markdown)
        self.assertIn("## Riesgos", markdown)
        self.assertIn("- no tiene proceso consistente", markdown)
        self.assertIn("## Próximos pasos", markdown)
        self.assertIn("- Agendar demo enfocada en prioridades y siguientes pasos.", markdown)


if __name__ == "__main__":
    unittest.main()
