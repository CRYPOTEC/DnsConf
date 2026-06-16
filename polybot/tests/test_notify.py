import os
import unittest

from polybot import notify


class TelegramTests(unittest.TestCase):
    def test_send_builds_payload(self):
        captured = {}

        def fake_sender(url, payload):
            captured["url"] = url
            captured["payload"] = payload

        n = notify.TelegramNotifier("TOK", "42", sender=fake_sender)
        n.send("hello")
        self.assertIn("botTOK/sendMessage", captured["url"])
        self.assertEqual(captured["payload"]["chat_id"], "42")
        self.assertEqual(captured["payload"]["text"], "hello")

    def test_send_swallows_errors(self):
        def boom(url, payload):
            raise RuntimeError("network down")

        # must not raise
        notify.TelegramNotifier("TOK", "42", sender=boom).send("x")


class BuildNotifierTests(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in
                       ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")}
        for k in self._saved:
            os.environ.pop(k, None)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_console_without_env(self):
        self.assertEqual(notify.build_notifier().name, "console")

    def test_telegram_with_env(self):
        os.environ["TELEGRAM_BOT_TOKEN"] = "t"
        os.environ["TELEGRAM_CHAT_ID"] = "c"
        self.assertEqual(notify.build_notifier().name, "telegram")


if __name__ == "__main__":
    unittest.main()
