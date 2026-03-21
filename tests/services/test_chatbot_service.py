"""Tests for Chatbot service."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Set a fake API key to prevent OpenAI client initialization errors
os.environ["OPENAI_API_KEY"] = "fake-test-key"

from app.services.chatbot_service import process_chat, tools


class TestChatbotService:
    """Test cases for chatbot service."""
    
    @patch('app.services.chatbot_service.client')
    def test_process_chat_simple_message_without_tool_calls(self, mock_client):
        """Test chat processing for simple messages that don't require tool calls."""
        # Arrange
        mock_response = Mock()
        mock_message = Mock()
        mock_message.tool_calls = None
        mock_message.content = "Hello! I'm your AI inventory assistant. How can I help you today?"
        mock_response.choices = [Mock(message=mock_message)]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = process_chat("Hello")
        
        # Assert
        assert result == "Hello! I'm your AI inventory assistant. How can I help you today?"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI inventory assistant."},
                {"role": "user", "content": "Hello"}
            ],
            tools=tools,
            tool_choice="auto"
        )
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_with_inventory_tool_call_success(self, mock_client, mock_get_inventory, mock_get_db):
        """Test chat processing with successful inventory lookup tool call."""
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_get_inventory.return_value = 50
        
        # Mock first response with tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_inventory_by_product_name"
        mock_tool_call.function.arguments = json.dumps({"product_name": "Widget"})
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call]
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        # Mock second response with final answer
        mock_second_message = Mock()
        mock_second_message.content = "We currently have 50 units of Widget in stock."
        mock_second_response = Mock()
        mock_second_response.choices = [Mock(message=mock_second_message)]
        
        mock_client.chat.completions.create.side_effect = [mock_first_response, mock_second_response]
        
        # Act
        result = process_chat("How many Widgets do we have?")
        
        # Assert
        assert result == "We currently have 50 units of Widget in stock."
        assert mock_client.chat.completions.create.call_count == 2
        mock_get_inventory.assert_called_once_with(mock_db_session, "Widget")
        mock_db_session.close.assert_called_once()
        
        # Verify the second call includes the tool result
        second_call_args = mock_client.chat.completions.create.call_args_list[1]
        messages = second_call_args[1]['messages']
        assert len(messages) == 4
        assert messages[-1]["role"] == "tool"
        assert messages[-1]["tool_call_id"] == "call_123"
        assert messages[-1]["content"] == "50"
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_with_inventory_tool_call_product_not_found(self, mock_client, mock_get_inventory, mock_get_db):
        """Test chat processing when product is not found."""
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_get_inventory.return_value = 0
        
        # Mock first response with tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_456"
        mock_tool_call.function.name = "get_inventory_by_product_name"
        mock_tool_call.function.arguments = json.dumps({"product_name": "NonExistentProduct"})
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call]
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        # Mock second response
        mock_second_message = Mock()
        mock_second_message.content = "I couldn't find any inventory for NonExistentProduct."
        mock_second_response = Mock()
        mock_second_response.choices = [Mock(message=mock_second_message)]
        
        mock_client.chat.completions.create.side_effect = [mock_first_response, mock_second_response]
        
        # Act
        result = process_chat("How many NonExistentProduct do we have?")
        
        # Assert
        assert result == "I couldn't find any inventory for NonExistentProduct."
        mock_get_inventory.assert_called_once_with(mock_db_session, "NonExistentProduct")
        mock_db_session.close.assert_called_once()
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_database_session_cleanup_on_exception(self, mock_client, mock_get_inventory, mock_get_db):
        """Test that database session is properly closed even when an exception occurs."""
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_get_inventory.side_effect = Exception("Database error")
        
        # Mock first response with tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_789"
        mock_tool_call.function.name = "get_inventory_by_product_name"
        mock_tool_call.function.arguments = json.dumps({"product_name": "TestProduct"})
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call]
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        mock_client.chat.completions.create.return_value = mock_first_response
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            process_chat("How many TestProduct do we have?")
        
        # Verify session cleanup
        mock_db_session.close.assert_called_once()
    
    @patch('app.services.chatbot_service.client')
    def test_process_chat_invalid_json_in_tool_arguments(self, mock_client):
        """Test handling of invalid JSON in tool call arguments."""
        # Arrange
        mock_tool_call = Mock()
        mock_tool_call.id = "call_invalid"
        mock_tool_call.function.name = "get_inventory_by_product_name"
        mock_tool_call.function.arguments = "invalid json"
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call]
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        mock_client.chat.completions.create.return_value = mock_first_response
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            process_chat("How many products do we have?")
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_unknown_function_call(self, mock_client, mock_get_inventory, mock_get_db):
        """Test handling of unknown function calls."""
        # Arrange
        mock_tool_call = Mock()
        mock_tool_call.id = "call_unknown"
        mock_tool_call.function.name = "unknown_function"
        mock_tool_call.function.arguments = json.dumps({"param": "value"})
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call]
        mock_first_message.content = "I don't recognize that function."
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        mock_client.chat.completions.create.return_value = mock_first_response
        
        # Act
        result = process_chat("Test unknown function")
        
        # Assert - should return the original message content since no handling for unknown function
        assert result == "I don't recognize that function."
        mock_get_inventory.assert_not_called()
    
    def test_tools_configuration(self):
        """Test that the tools configuration is properly defined."""
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        
        function_def = tools[0]["function"]
        assert function_def["name"] == "get_inventory_by_product_name"
        assert function_def["description"] == "Get inventory count for a product by its name"
        
        # Check parameters structure
        params = function_def["parameters"]
        assert params["type"] == "object"
        assert "product_name" in params["properties"]
        assert params["properties"]["product_name"]["type"] == "string"
        assert params["required"] == ["product_name"]
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_with_multiple_tool_calls(self, mock_client, mock_get_inventory, mock_get_db):
        """Test that only the first tool call is processed."""
        # Arrange
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_get_inventory.return_value = 25
        
        # Mock first response with multiple tool calls
        mock_tool_call_1 = Mock()
        mock_tool_call_1.id = "call_1"
        mock_tool_call_1.function.name = "get_inventory_by_product_name"
        mock_tool_call_1.function.arguments = json.dumps({"product_name": "Product1"})
        
        mock_tool_call_2 = Mock()
        mock_tool_call_2.id = "call_2"
        mock_tool_call_2.function.name = "get_inventory_by_product_name"
        mock_tool_call_2.function.arguments = json.dumps({"product_name": "Product2"})
        
        mock_first_message = Mock()
        mock_first_message.tool_calls = [mock_tool_call_1, mock_tool_call_2]
        mock_first_response = Mock()
        mock_first_response.choices = [Mock(message=mock_first_message)]
        
        # Mock second response
        mock_second_message = Mock()
        mock_second_message.content = "Product1 has 25 units in stock."
        mock_second_response = Mock()
        mock_second_response.choices = [Mock(message=mock_second_message)]
        
        mock_client.chat.completions.create.side_effect = [mock_first_response, mock_second_response]
        
        # Act
        result = process_chat("Check inventory for products")
        
        # Assert - only first tool call should be processed
        assert result == "Product1 has 25 units in stock."
        mock_get_inventory.assert_called_once_with(mock_db_session, "Product1")
        mock_db_session.close.assert_called_once()
    
    @patch('app.services.chatbot_service.get_db')
    @patch('app.services.chatbot_service.get_inventory_by_product_name')
    @patch('app.services.chatbot_service.client')
    def test_process_chat_openai_api_failure(self, mock_client, mock_get_inventory, mock_get_db):
        """Test handling of OpenAI API failures."""
        # Arrange
        mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
        
        # Act & Assert
        with pytest.raises(Exception, match="OpenAI API Error"):
            process_chat("Test message")
        
        # Database functions should not be called if OpenAI fails
        mock_get_inventory.assert_not_called()
        mock_get_db.assert_not_called()