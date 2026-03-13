"""Tests for care.py — text call that returns care tips for a species."""

import json
import unittest
from unittest.mock import MagicMock, patch


class TestGetCareTips(unittest.TestCase):
    def _make_mock_response(self, json_payload: dict) -> MagicMock:
        block = MagicMock()
        block.type = "text"
        block.text = json.dumps(json_payload)
        msg = MagicMock()
        msg.content = [block]
        return msg

    @patch("care.anthropic.Anthropic")
    def test_returns_care_tips_list(self, MockAnthropic):
        """get_care_tips returns a dict with a non-empty care_tips list."""
        from care import get_care_tips

        payload = {
            "care_tips": [
                "Water twice a week",
                "Full sun preferred",
                "Prune in early spring",
            ]
        }
        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response(payload)
        )

        result = get_care_tips("Rosa canina")

        self.assertIn("care_tips", result)
        self.assertIsInstance(result["care_tips"], list)
        self.assertGreater(len(result["care_tips"]), 0)

    @patch("care.anthropic.Anthropic")
    def test_species_name_in_prompt(self, MockAnthropic):
        """get_care_tips includes the species name in the API prompt."""
        from care import get_care_tips

        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = self._make_mock_response(
            {"care_tips": ["Keep moist"]}
        )

        get_care_tips("Monstera deliciosa")

        call_kwargs = mock_client.messages.create.call_args
        # Reconstruct kwargs regardless of positional/keyword calling style
        all_kwargs = call_kwargs.kwargs if call_kwargs.kwargs else {}
        all_args = call_kwargs.args if call_kwargs.args else ()

        # Flatten everything to a single string for the assertion
        call_text = str(all_kwargs) + str(all_args)
        self.assertIn("Monstera deliciosa", call_text)

    @patch("care.anthropic.Anthropic")
    def test_raises_on_missing_care_tips(self, MockAnthropic):
        """get_care_tips raises ValueError when response lacks 'care_tips'."""
        from care import get_care_tips

        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response({"watering": "twice a week"})
        )

        with self.assertRaises(ValueError):
            get_care_tips("Rosa canina")

    @patch("care.anthropic.Anthropic")
    def test_raises_on_invalid_json(self, MockAnthropic):
        """get_care_tips raises ValueError when the API returns non-JSON text."""
        from care import get_care_tips

        block = MagicMock()
        block.type = "text"
        block.text = "Water it sometimes."
        msg = MagicMock()
        msg.content = [block]
        MockAnthropic.return_value.messages.create.return_value = msg

        with self.assertRaises(ValueError):
            get_care_tips("Rosa canina")

    @patch("care.anthropic.Anthropic")
    def test_care_tips_are_strings(self, MockAnthropic):
        """Each item in care_tips must be a string."""
        from care import get_care_tips

        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response({"care_tips": ["Tip one", "Tip two"]})
        )

        result = get_care_tips("Ficus lyrata")
        for tip in result["care_tips"]:
            self.assertIsInstance(tip, str)


if __name__ == "__main__":
    unittest.main()
