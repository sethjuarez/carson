"""
Simple smoke tests to verify the test setup is working.

These tests should pass immediately and verify that the testing
infrastructure is properly configured.
"""


def test_basic_assertion():
    """Test that basic assertions work."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test basic string operations."""
    test_string = "Hello, Carson API!"
    assert "Carson" in test_string
    assert test_string.startswith("Hello")
    assert test_string.endswith("!")


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert 3 in test_list
    assert max(test_list) == 5


def test_dictionary_operations():
    """Test basic dictionary operations."""
    test_dict = {"name": "Carson", "type": "API", "version": "0.1.0"}
    assert test_dict["name"] == "Carson"
    assert "type" in test_dict
    assert len(test_dict) == 3


class TestBasicClass:
    """Test class structure and methods."""

    def test_class_method(self):
        """Test that class methods work correctly."""
        assert self.__class__.__name__ == "TestBasicClass"

    def test_fixture_like_setup(self):
        """Test setup and teardown patterns."""
        # Setup
        data = {"test": "value"}

        # Test
        assert data["test"] == "value"

        # Teardown (implicit)
        del data


def test_import_functionality():
    """Test that basic imports work."""
    import json
    import base64
    import uuid

    # Test JSON operations
    test_data = {"message": "test"}
    json_string = json.dumps(test_data)
    parsed_data = json.loads(json_string)
    assert parsed_data["message"] == "test"

    # Test base64 operations
    test_bytes = b"test data"
    encoded = base64.b64encode(test_bytes)
    decoded = base64.b64decode(encoded)
    assert decoded == test_bytes

    # Test UUID generation
    test_uuid = uuid.uuid4()
    assert len(str(test_uuid)) == 36


def test_async_basic():
    """Test basic async functionality."""
    import asyncio

    async def async_function():
        return "async result"

    # Run the async function
    result = asyncio.run(async_function())
    assert result == "async result"
