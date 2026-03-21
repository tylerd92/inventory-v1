"""Tests for Chat API endpoint."""
from unittest.mock import patch


class TestChatEndpoint:
    """Test cases for Chat API endpoint."""

    def test_chat_success(self, client):
        """Test successful chat request returns bot response."""
        with patch("app.api.v1.endpoints.chat.process_chat", return_value="You have 42 units in stock."):
            response = client.post("/api/v1/chat/", json={"message": "How many units do I have?"})

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "You have 42 units in stock."

    def test_chat_missing_message_field(self, client):
        """Test that omitting the required message field returns 422."""
        response = client.post("/api/v1/chat/", json={})
        assert response.status_code == 422

    def test_chat_invalid_body(self, client):
        """Test that sending a non-object body returns 422."""
        response = client.post("/api/v1/chat/", json="not an object")
        assert response.status_code == 422

    def test_chat_service_exception_returns_500(self, client):
        """Test that an unhandled exception in process_chat returns 500."""
        with patch("app.api.v1.endpoints.chat.process_chat", side_effect=Exception("OpenAI unavailable")):
            response = client.post("/api/v1/chat/", json={"message": "Hello"})

        assert response.status_code == 500
        assert "OpenAI unavailable" in response.json()["detail"]

    def test_chat_empty_message(self, client):
        """Test that an empty string message is accepted and forwarded to the service."""
        with patch("app.api.v1.endpoints.chat.process_chat", return_value="Please ask me something.") as mock_chat:
            response = client.post("/api/v1/chat/", json={"message": ""})

        assert response.status_code == 200
        mock_chat.assert_called_once_with("")

    def test_chat_calls_process_chat_with_message(self, client):
        """Test that process_chat is called with the exact message from the request."""
        with patch("app.api.v1.endpoints.chat.process_chat", return_value="Got it.") as mock_chat:
            client.post("/api/v1/chat/", json={"message": "What is the stock for Widget A?"})

        mock_chat.assert_called_once_with("What is the stock for Widget A?")
