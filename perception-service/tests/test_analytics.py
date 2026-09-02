"""
Automated API Test Suite for Perception Analytics & Dashboard Endpoints
==============================================================================
Tests /svi-trend, /risk-distribution, /flag-frequency, /channel-language-volume,
district, state, risk tier, language, and channel filters.
==============================================================================
"""

import unittest
from fastapi.testclient import TestClient

from api.main import app

class TestAnalyticsEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_svi_trend_endpoint(self):
        response = self.client.get("/api/v1/perception/analytics/svi-trend?period=weekly")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["period_type"], "weekly")
        self.assertGreater(data["total_cases_analyzed"], 0)
        self.assertGreater(len(data["trends"]), 0)

        item = data["trends"][0]
        self.assertIn("time_period", item)
        self.assertIn("average_svi", item)
        self.assertIn("case_count", item)

    def test_svi_trend_district_filter(self):
        response = self.client.get("/api/v1/perception/analytics/svi-trend?district=Central%20Delhi")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertGreater(len(data["trends"]), 0)
        self.assertEqual(data["trends"][0]["district"], "Central Delhi")

    def test_risk_distribution_endpoint(self):
        response = self.client.get("/api/v1/perception/analytics/risk-distribution")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertGreater(data["total_cases"], 0)
        self.assertEqual(len(data["distribution"]), 4)

        tiers = [d["risk_tier"] for d in data["distribution"]]
        self.assertIn("Low", tiers)
        self.assertIn("Moderate", tiers)
        self.assertIn("High", tiers)
        self.assertIn("Critical", tiers)

    def test_flag_frequency_endpoint(self):
        response = self.client.get("/api/v1/perception/analytics/flag-frequency")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertGreater(data["total_flags_count"], 0)
        self.assertGreater(len(data["flags"]), 0)

        first_flag = data["flags"][0]
        self.assertIn("flag_name", first_flag)
        self.assertIn("count", first_flag)
        self.assertIn("percentage", first_flag)

    def test_channel_language_volume_endpoint(self):
        response = self.client.get("/api/v1/perception/analytics/channel-language-volume")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertGreater(data["total_cases"], 0)
        self.assertGreater(len(data["volumes"]), 0)

        item = data["volumes"][0]
        self.assertIn("channel", item)
        self.assertIn("language", item)
        self.assertIn("count", item)

if __name__ == "__main__":
    unittest.main()
