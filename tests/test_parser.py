import unittest

from opspulse.parser import parse_line


class ParserTests(unittest.TestCase):
    def test_plain_log(self):
        event = parse_line("2026-09-17T02:01:08Z ERROR payment-api gateway timeout")
        self.assertEqual(event.level, "ERROR")
        self.assertEqual(event.service, "payment-api")
        self.assertEqual(event.message, "gateway timeout")
        self.assertIsNotNone(event.timestamp)

    def test_json_log(self):
        event = parse_line('{"timestamp":"2026-09-17T02:01:08Z","severity":"WARN","application":"web","msg":"slow"}')
        self.assertEqual(event.level, "WARNING")
        self.assertEqual(event.service, "web")
        self.assertEqual(event.message, "slow")

    def test_unknown_format_is_retained(self):
        event = parse_line("legacy service is alive")
        self.assertEqual(event.level, "INFO")
        self.assertEqual(event.message, "legacy service is alive")


if __name__ == "__main__":
    unittest.main()

