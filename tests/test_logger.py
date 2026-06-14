from unittest.mock import patch
from core.logger import get_logger

def test_get_logger_no_name():
    """Test get_logger returns a default logger when no name is provided."""
    logger = get_logger()
    assert logger is not None

def test_get_logger_with_name():
    """Test get_logger returns a bound logger when a name is provided."""
    with patch("core.logger.logger.bind") as mock_bind:
        mock_bind.return_value = "bound_logger"
        logger = get_logger("my_test_logger")
        mock_bind.assert_called_once_with(name="my_test_logger")
        assert logger == "bound_logger"
