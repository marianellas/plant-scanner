"""Tests for identifier.py — vision call that returns species + confidence."""

import json
import unittest
from unittest.mock import MagicMock, patch


class TestIdentifyPlant(unittest.TestCase):
    def _make_mock_response(self, json_payload: dict) -> MagicMock:
        """Build a fake anthropic Message whose first content block is text."""
        block = MagicMock()
        block.type = "text"
        block.text = json.dumps(json_payload)
        msg = MagicMock()
        msg.content = [block]
        return msg

    @patch("identifier.anthropic.Anthropic")
    def test_returns_species_and_confidence(self, MockAnthropic):
        """identify_plant returns a dict with species and confidence keys."""
        from identifier import identify_plant

        payload = {
            "species": "Rosa canina",
            "common_name": "Dog Rose",
            "confidence": 0.92,
        }
        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response(payload)
        )

        result = identify_plant("fake_base64_data", "image/jpeg")

        self.assertEqual(result["species"], "Rosa canina")
        self.assertEqual(result["common_name"], "Dog Rose")
        self.assertAlmostEqual(result["confidence"], 0.92)

    @patch("identifier.anthropic.Anthropic")
    def test_sends_image_and_prompt(self, MockAnthropic):
        """identify_plant passes the image and a JSON-requesting prompt to the API."""
        from identifier import identify_plant

        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = self._make_mock_response(
            {
                "species": "Quercus robur",
                "common_name": "English Oak",
                "confidence": 0.85,
            }
        )

        identify_plant("abc123", "image/png")

        call_kwargs = mock_client.messages.create.call_args
        messages = (
            call_kwargs.kwargs.get("messages")
            or call_kwargs.args[0]
            if call_kwargs.args
            else call_kwargs.kwargs["messages"]
        )

        # Find the user message
        user_msg = next(m for m in messages if m["role"] == "user")
        content = user_msg["content"]

        # Must contain an image block
        image_blocks = [b for b in content if b.get("type") == "image"]
        self.assertEqual(len(image_blocks), 1)
        self.assertEqual(image_blocks[0]["source"]["data"], "abc123")
        self.assertEqual(image_blocks[0]["source"]["media_type"], "image/png")

        # Must contain a text/prompt block
        text_blocks = [b for b in content if b.get("type") == "text"]
        self.assertGreater(len(text_blocks), 0)

    @patch("identifier.anthropic.Anthropic")
    def test_raises_on_missing_species(self, MockAnthropic):
        """identify_plant raises ValueError when the API response omits 'species'."""
        from identifier import identify_plant

        MockAnthropic.return_value.messages.create.return_value = (
            self._make_mock_response({"confidence": 0.5})  # no species key
        )

        with self.assertRaises(ValueError):
            identify_plant("fake_base64", "image/jpeg")

    @patch("identifier.anthropic.Anthropic")
    def test_raises_on_invalid_json(self, MockAnthropic):
        """identify_plant raises ValueError when the API returns non-JSON text."""
        from identifier import identify_plant

        block = MagicMock()
        block.type = "text"
        block.text = "I see a flower."
        msg = MagicMock()
        msg.content = [block]
        MockAnthropic.return_value.messages.create.return_value = msg

        with self.assertRaises(ValueError):
            identify_plant("fake_base64", "image/jpeg")


if __name__ == "__main__":
    unittest.main()
