import unittest

from fastapi import HTTPException

from services import rate_limit


class AiRateLimitTests(unittest.TestCase):
    def setUp(self):
        rate_limit.AI_RATE_LIMITS.clear()

    def test_user_is_allowed_n_requests_within_window(self):
        for index in range(10):
            # Fixed timestamps make the sliding-window behavior deterministic.
            rate_limit.rate_limit_ai_request(request=None, user_id=42, now=1000 + index)

        self.assertEqual(len(rate_limit.AI_RATE_LIMITS["ai:user:42"]), 10)

    def test_n_plus_one_request_returns_429(self):
        for index in range(10):
            rate_limit.rate_limit_ai_request(request=None, user_id=42, now=1000 + index)

        with self.assertRaises(HTTPException) as exc:
            rate_limit.rate_limit_ai_request(request=None, user_id=42, now=1010)

        self.assertEqual(exc.exception.status_code, 429)
        self.assertEqual(exc.exception.headers["Retry-After"], "51")

    def test_counter_resets_after_window_expires(self):
        for index in range(10):
            rate_limit._check_sliding_windows("unit", "user:42", ((10, 60),), now=1000 + index)

        rate_limit._check_sliding_windows("unit", "user:42", ((10, 60),), now=1070)

        self.assertEqual(len(rate_limit.AI_RATE_LIMITS["unit:user:42"]), 1)


if __name__ == "__main__":
    unittest.main()
