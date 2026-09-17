import unittest
from datetime import datetime, timezone

from opspulse.analyzer import analyze, normalize_signature
from opspulse.models import LogEvent


def event(minute: int, level: str, message: str = "timeout id=123456") -> LogEvent:
    return LogEvent(datetime(2026, 9, 17, 2, minute, tzinfo=timezone.utc), level, "api", message, message)


class AnalyzerTests(unittest.TestCase):
    def test_masks_identifiers_and_ips(self):
        result = normalize_signature("failure transaction_id=987654 upstream=10.2.4.18")
        self.assertIn("transaction_id=<id>", result)
        self.assertIn("<ip>", result)

    def test_detects_spike_and_degraded_health(self):
        events = [event(0, "INFO")] + [event(index, "ERROR") for index in range(1, 6)]
        result = analyze(events, window_minutes=5, spike_threshold=4)
        self.assertTrue(result.spike_detected)
        self.assertGreaterEqual(result.peak_window_errors, 4)
        self.assertLess(result.health_score, 80)

    def test_empty_input_is_healthy(self):
        result = analyze([])
        self.assertEqual(result.health_score, 100)
        self.assertEqual(result.status, "HEALTHY")


if __name__ == "__main__":
    unittest.main()

