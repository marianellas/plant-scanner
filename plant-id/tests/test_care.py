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


class TestGetToxicity(unittest.TestCase):
    def _make_mock_response(self, json_payload: dict) -> MagicMock:
        block = MagicMock()
        block.type = "text"
        block.text = json.dumps(json_payload)
        msg = MagicMock()
        msg.content = [block]
        return msg

    @patch("care.anthropic.Anthropic")
    def test_returns_toxic_and_details(self, MockAnthropic):
        """get_toxicity returns a dict with toxic and details keys."""
        from care import get_toxicity

        payload = {"toxic": True, "details": "Can cause vomiting in cats.", "targets": ["cats"]}
        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response(payload)
        )

        result = get_toxicity("Epipremnum aureum", "cats")

        self.assertIn("toxic", result)
        self.assertIn("details", result)
        self.assertIsInstance(result["toxic"], bool)
        self.assertIsInstance(result["details"], str)

    @patch("care.anthropic.Anthropic")
    def test_all_expands_to_all_targets(self, MockAnthropic):
        """get_toxicity with 'all' includes cats, dogs, and children in the prompt."""
        from care import get_toxicity

        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = self._make_mock_response(
            {"toxic": True, "details": "Toxic to all.", "targets": ["cats", "dogs", "children"]}
        )

        get_toxicity("Rosa canina", "all")

        call_text = str(mock_client.messages.create.call_args)
        self.assertIn("cats", call_text)
        self.assertIn("dogs", call_text)
        self.assertIn("children", call_text)

    @patch("care.anthropic.Anthropic")
    def test_raises_on_missing_keys(self, MockAnthropic):
        """get_toxicity raises ValueError when response is missing required keys."""
        from care import get_toxicity

        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response({"safe": True})
        )

        with self.assertRaises(ValueError):
            get_toxicity("Rosa canina", "dogs")

    @patch("care.anthropic.Anthropic")
    def test_raises_on_invalid_json(self, MockAnthropic):
        """get_toxicity raises ValueError when the API returns non-JSON text."""
        from care import get_toxicity

        block = MagicMock()
        block.type = "text"
        block.text = "This plant is safe."
        msg = MagicMock()
        msg.content = [block]
        MockAnthropic.return_value.messages.create.return_value = msg

        with self.assertRaises(ValueError):
            get_toxicity("Rosa canina", "kids")


class TestGetPlantHelp(unittest.TestCase):
    def _make_mock_response(self, json_payload: dict) -> MagicMock:
        block = MagicMock()
        block.type = "text"
        block.text = json.dumps(json_payload)
        msg = MagicMock()
        msg.content = [block]
        return msg

    @patch("care.anthropic.Anthropic")
    def test_returns_diagnosis_and_advice(self, MockAnthropic):
        """get_plant_help returns a dict with diagnosis and advice keys."""
        from care import get_plant_help

        payload = {
            "diagnosis": "Overwatering is causing root rot.",
            "advice": ["Reduce watering to once a week", "Ensure pot has drainage holes"],
        }
        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response(payload)
        )

        result = get_plant_help("Monstera deliciosa", "leaves turning yellow")

        self.assertIn("diagnosis", result)
        self.assertIn("advice", result)
        self.assertIsInstance(result["diagnosis"], str)
        self.assertIsInstance(result["advice"], list)

    @patch("care.anthropic.Anthropic")
    def test_species_and_issue_in_prompt(self, MockAnthropic):
        """get_plant_help includes both species and issue in the API prompt."""
        from care import get_plant_help

        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = self._make_mock_response(
            {"diagnosis": "Too much sun.", "advice": ["Move to shade"]}
        )

        get_plant_help("Ficus lyrata", "brown crispy edges")

        call_text = str(mock_client.messages.create.call_args)
        self.assertIn("Ficus lyrata", call_text)
        self.assertIn("brown crispy edges", call_text)

    @patch("care.anthropic.Anthropic")
    def test_raises_on_missing_keys(self, MockAnthropic):
        """get_plant_help raises ValueError when response is missing required keys."""
        from care import get_plant_help

        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response({"tips": ["water less"]})
        )

        with self.assertRaises(ValueError):
            get_plant_help("Rosa canina", "wilting")

    @patch("care.anthropic.Anthropic")
    def test_raises_on_invalid_json(self, MockAnthropic):
        """get_plant_help raises ValueError when the API returns non-JSON text."""
        from care import get_plant_help

        block = MagicMock()
        block.type = "text"
        block.text = "Looks like it needs more water."
        msg = MagicMock()
        msg.content = [block]
        MockAnthropic.return_value.messages.create.return_value = msg

        with self.assertRaises(ValueError):
            get_plant_help("Rosa canina", "drooping leaves")


if __name__ == "__main__":
    unittest.main()
