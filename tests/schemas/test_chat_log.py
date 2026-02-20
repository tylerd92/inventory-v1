"""Tests for ChatLog schemas."""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.chat_log import (
    ChatLogBase,
    ChatLogCreate,
    ChatLogUpdate,
    ChatLogResponse,
    ChatLogWithUser
)


class TestChatLogSchemas:
    """Test cases for ChatLog schemas."""

    def test_chat_log_base_valid_data(self):
        """Test ChatLogBase with valid data."""
        data = {
            "user_id": 1,
            "question": "What is the inventory level for product ABC?",
            "response": "The current inventory level for product ABC is 150 units."
        }
        chat_log = ChatLogBase(**data)
        assert chat_log.user_id == 1
        assert chat_log.question == "What is the inventory level for product ABC?"
        assert chat_log.response == "The current inventory level for product ABC is 150 units."

    def test_chat_log_base_without_user_id(self):
        """Test ChatLogBase without user_id (should be valid - anonymous chat)."""
        data = {
            "question": "How many products are in stock?",
            "response": "There are 500 products currently in stock."
        }
        chat_log = ChatLogBase(**data)
        assert chat_log.user_id is None
        assert chat_log.question == "How many products are in stock?"
        assert chat_log.response == "There are 500 products currently in stock."

    def test_chat_log_base_invalid_data(self):
        """Test ChatLogBase with invalid data."""
        # Missing required question
        with pytest.raises(ValidationError):
            ChatLogBase(user_id=1, response="A response without question")

        # Missing required response
        with pytest.raises(ValidationError):
            ChatLogBase(user_id=1, question="A question without response")

        # Invalid type for user_id
        with pytest.raises(ValidationError):
            ChatLogBase(user_id="invalid", question="Test question", response="Test response")

    def test_chat_log_base_long_text(self):
        """Test ChatLogBase with long question and response text."""
        long_question = "This is a very long question " * 50  # ~1500 characters
        long_response = "This is a very long response " * 100  # ~3000 characters
        
        data = {
            "user_id": 1,
            "question": long_question,
            "response": long_response
        }
        chat_log = ChatLogBase(**data)
        assert len(chat_log.question) > 1000
        assert len(chat_log.response) > 2000

    def test_chat_log_create(self):
        """Test ChatLogCreate schema."""
        data = {
            "user_id": 2,
            "question": "Can you help me track product movements?",
            "response": "Yes, I can help you track all product movements in the inventory system."
        }
        chat_log = ChatLogCreate(**data)
        assert chat_log.user_id == 2
        assert chat_log.question == "Can you help me track product movements?"
        assert chat_log.response == "Yes, I can help you track all product movements in the inventory system."

    def test_chat_log_update_partial(self):
        """Test ChatLogUpdate with partial data."""
        # Only question
        update = ChatLogUpdate(question="Updated question?")
        assert update.question == "Updated question?"
        assert update.response is None

        # Only response
        update = ChatLogUpdate(response="Updated response.")
        assert update.question is None
        assert update.response == "Updated response."

        # Both fields
        update = ChatLogUpdate(
            question="Updated question with both fields?",
            response="Updated response with both fields."
        )
        assert update.question == "Updated question with both fields?"
        assert update.response == "Updated response with both fields."

    def test_chat_log_update_all_fields(self):
        """Test ChatLogUpdate with all fields."""
        data = {
            "question": "Completely updated question?",
            "response": "Completely updated response."
        }
        update = ChatLogUpdate(**data)
        assert update.question == "Completely updated question?"
        assert update.response == "Completely updated response."

    def test_chat_log_update_empty(self):
        """Test ChatLogUpdate with no fields (should be valid)."""
        update = ChatLogUpdate()
        assert update.question is None
        assert update.response is None

    def test_chat_log_response(self):
        """Test ChatLogResponse schema."""
        now = datetime.now()
        data = {
            "id": 1,
            "user_id": 1,
            "question": "What's the status of my order?",
            "response": "Your order is currently being processed.",
            "created_at": now
        }
        response = ChatLogResponse(**data)
        assert response.id == 1
        assert response.user_id == 1
        assert response.question == "What's the status of my order?"
        assert response.response == "Your order is currently being processed."
        assert response.created_at == now

    def test_chat_log_response_anonymous(self):
        """Test ChatLogResponse for anonymous user."""
        now = datetime.now()
        data = {
            "id": 2,
            "user_id": None,
            "question": "Can I browse products without logging in?",
            "response": "Yes, you can browse products as an anonymous user.",
            "created_at": now
        }
        response = ChatLogResponse(**data)
        assert response.id == 2
        assert response.user_id is None
        assert response.question == "Can I browse products without logging in?"
        assert response.response == "Yes, you can browse products as an anonymous user."
        assert response.created_at == now

    def test_chat_log_response_missing_id(self):
        """Test ChatLogResponse without ID (should fail)."""
        data = {
            "user_id": 1,
            "question": "Test question",
            "response": "Test response",
            "created_at": datetime.now()
        }
        with pytest.raises(ValidationError):
            ChatLogResponse(**data)

    def test_chat_log_response_missing_created_at(self):
        """Test ChatLogResponse without created_at (should fail)."""
        data = {
            "id": 1,
            "user_id": 1,
            "question": "Test question",
            "response": "Test response"
        }
        with pytest.raises(ValidationError):
            ChatLogResponse(**data)

    def test_chat_log_response_dict_conversion(self):
        """Test converting ChatLogResponse to dict."""
        now = datetime.now()
        data = {
            "id": 1,
            "user_id": 3,
            "question": "How do I export my data?",
            "response": "You can export your data from the settings menu.",
            "created_at": now
        }
        response = ChatLogResponse(**data)
        response_dict = response.model_dump()
        
        assert response_dict["id"] == 1
        assert response_dict["user_id"] == 3
        assert response_dict["question"] == "How do I export my data?"
        assert response_dict["response"] == "You can export your data from the settings menu."
        assert response_dict["created_at"] == now

    def test_chat_log_special_characters(self):
        """Test ChatLog with special characters and formatting."""
        data = {
            "user_id": 1,
            "question": "What about products with symbols like @, #, $, %?",
            "response": "Products can contain symbols: @product, #tag, $100, 50% off!"
        }
        chat_log = ChatLogBase(**data)
        assert "@" in chat_log.question
        assert "#" in chat_log.response
        assert "$" in chat_log.response
        assert "%" in chat_log.response

    def test_chat_log_multiline_text(self):
        """Test ChatLog with multiline text."""
        multiline_question = """How can I:
1. Add new products
2. Update inventory
3. Generate reports"""
        
        multiline_response = """You can:
1. Add products via the Products page
2. Update inventory from the Inventory section  
3. Generate reports from the Reports menu"""
        
        data = {
            "user_id": 1,
            "question": multiline_question,
            "response": multiline_response
        }
        chat_log = ChatLogBase(**data)
        assert "\n" in chat_log.question
        assert "\n" in chat_log.response
        assert "1." in chat_log.question
        assert "1." in chat_log.response

    def test_chat_log_unicode_characters(self):
        """Test ChatLog with unicode characters."""
        data = {
            "user_id": 1,
            "question": "What about products with émojis 🚀 and åccénts?",
            "response": "Yes! We support émojis ✅ and accénted characters perfectly 👍"
        }
        chat_log = ChatLogBase(**data)
        assert "🚀" in chat_log.question
        assert "✅" in chat_log.response
        assert "👍" in chat_log.response
        assert "é" in chat_log.question
        assert "å" in chat_log.question

    def test_chat_log_schemas_inheritance(self):
        """Test that schemas properly inherit from base classes."""
        # ChatLogCreate should inherit from ChatLogBase
        assert issubclass(ChatLogCreate, ChatLogBase)
        
        # ChatLogResponse should inherit from ChatLogBase
        assert issubclass(ChatLogResponse, ChatLogBase)

        # ChatLogWithUser should inherit from ChatLogResponse
        assert issubclass(ChatLogWithUser, ChatLogResponse)


    def test_chat_log_config_settings(self):
        """Test that ChatLogResponse has correct Pydantic configuration."""
        # Check that from_attributes=True is configured for database model compatibility
        assert hasattr(ChatLogResponse, 'model_config')
        config = ChatLogResponse.model_config
        assert config.get('from_attributes') is True

    def test_chat_log_conversation_flow(self):
        """Test multiple chat logs simulating a conversation."""
        conversations = [
            {
                "user_id": 1,
                "question": "Hello, can you help me with inventory management?",
                "response": "Hello! I'd be happy to help you with inventory management. What specific area would you like assistance with?"
            },
            {
                "user_id": 1,
                "question": "I need to check the stock levels for all electronics.",
                "response": "I can help you check stock levels. Here are the current electronics inventory levels: [inventory data would be shown here]"
            },
            {
                "user_id": 1,
                "question": "Thank you! Can you also show me recent transactions?",
                "response": "You're welcome! Here are the recent inventory transactions: [transaction data would be shown here]"
            }
        ]
        
        for i, conv_data in enumerate(conversations):
            chat_log = ChatLogBase(**conv_data)
            assert chat_log.user_id == 1
            assert len(chat_log.question) > 0
            assert len(chat_log.response) > 0