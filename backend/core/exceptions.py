"""Custom exceptions for the news site application."""


class NewsSiteError(Exception):
    """Base exception for news site errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NewsScraperError(NewsSiteError):
    """Error during news scraping."""
    pass


class ArticleWriterError(NewsSiteError):
    """Error during article generation."""
    pass


class DatabaseError(NewsSiteError):
    """Database operation error."""
    pass


class ConfigurationError(NewsSiteError):
    """Configuration loading error."""
    pass


class ValidationError(NewsSiteError):
    """Data validation error."""
    pass


class NotFoundError(NewsSiteError):
    """Resource not found error."""
    pass
