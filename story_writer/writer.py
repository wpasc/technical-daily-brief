"""Main article writer using LLM."""
import json
import logging
import os
import re
from typing import Optional

from anthropic import Anthropic

from story_writer.article import GeneratedArticle
from story_writer.personas import WriterPersona
from story_writer.prompts.article_prompt import (
    ARTICLE_GENERATION_PROMPT,
    SYSTEM_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


class ArticleWriter:
    """Generates articles from events using Claude API."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize the article writer.

        Args:
            model: Claude model to use
            temperature: Generation temperature
            max_tokens: Maximum tokens for response
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.logger = logging.getLogger(__name__)

    def generate_article(
        self,
        title: str,
        source_name: str,
        raw_content: str,
        persona: Optional[WriterPersona] = None,
        max_retries: int = 3,
    ) -> Optional[GeneratedArticle]:
        """
        Generate an article from source material.

        Args:
            title: Original article title
            source_name: News source name
            raw_content: Raw article content
            persona: Writer persona to use (auto-selected if None)
            max_retries: Maximum retry attempts

        Returns:
            GeneratedArticle or None if generation fails
        """
        # Start with default persona, will update after determining section
        if persona is None:
            persona = WriterPersona.default()

        # Build prompts
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            name=persona.name,
            persona=persona.persona,
            style_description=persona.style_description,
        )

        user_prompt = ARTICLE_GENERATION_PROMPT.format(
            title=title,
            source_name=source_name,
            raw_content=raw_content[:4000],  # Limit content length
        )

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )

                content = response.content[0].text
                article_data = self._parse_response(content)

                if article_data:
                    # Get appropriate persona for the determined section
                    section_persona = WriterPersona.for_section(article_data["section"])

                    return GeneratedArticle(
                        headline=article_data["headline"],
                        excerpt=article_data["excerpt"],
                        content=article_data["content"],
                        section=article_data["section"],
                        priority=article_data["priority"],
                        writer_persona=f"{section_persona.name}, {section_persona.persona}",
                    )

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to generate article after {max_retries} attempts")
                    return None

        return None

    def _parse_response(self, content: str) -> Optional[dict]:
        """
        Parse JSON response from LLM.

        Args:
            content: Raw response content

        Returns:
            Parsed dictionary or None
        """
        try:
            # Try direct JSON parse
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in content
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        self.logger.error(f"Failed to parse response: {content[:200]}...")
        return None
