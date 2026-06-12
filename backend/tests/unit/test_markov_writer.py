"""Tests for the zero-cost Markov article writer."""
import sys
from pathlib import Path

import pytest

# story_writer lives at the project root, not under backend/
sys.path.insert(0, str(Path(__file__).parents[3]))

from story_writer.markov_writer import MarkovChain, MarkovWriter  # noqa: E402

import random  # noqa: E402


ECON_TEXT = (
    "Central banks signaled a shift in monetary policy as inflation cooled. "
    "Investors watched bond markets closely after the announcement. "
    "Analysts said the economy could avoid a recession this year. "
    "Trade volumes rose sharply across major stock markets in early trading."
)

TECH_TEXT = (
    "The technology company unveiled a new chip designed for AI workloads. "
    "Engineers said the software platform processes data faster than rivals. "
    "Startup founders praised the internet infrastructure improvements. "
    "The smartphone maker plans to ship robot assistants next year."
)

SAMPLE_EVENTS = [
    {"title": "Central Banks Signal Policy Shift Amid Inflation Concerns", "raw_content": ECON_TEXT},
    {"title": "Tech Giants Unveil New AI Chip For Data Centers", "raw_content": TECH_TEXT},
]


@pytest.fixture
def trained_writer():
    writer = MarkovWriter(seed=42)
    writer.train(SAMPLE_EVENTS)
    return writer


class TestMarkovChain:
    def test_untrained_chain_reports_not_trained(self):
        chain = MarkovChain(order=2, rng=random.Random(1))
        assert not chain.trained

    def test_generates_sentence_ending_in_punctuation(self):
        chain = MarkovChain(order=2, rng=random.Random(1))
        chain.train(ECON_TEXT)
        sentence = chain.sentence()
        assert sentence[-1] in ".!?"
        assert sentence[0].isupper()

    def test_only_emits_words_from_corpus(self):
        chain = MarkovChain(order=2, rng=random.Random(1))
        chain.train(ECON_TEXT)
        corpus_words = set(ECON_TEXT.split())
        for _ in range(20):
            words = chain.sentence().rstrip(".").split()
            # First word is recapitalized; compare case-insensitively
            assert all(
                w.lower() in {c.lower().rstrip(".") for c in corpus_words} for w in words
            )


class TestMarkovWriter:
    def test_generates_complete_article(self, trained_writer):
        event = SAMPLE_EVENTS[0]
        article = trained_writer.generate_article(
            title=event["title"], source_name="Test Wire", raw_content=event["raw_content"]
        )
        assert article is not None
        assert article.headline
        assert article.excerpt
        assert article.content
        assert article.section in {"Economics", "Technology", "World", "Politics", "Science", "Culture"}
        assert article.priority in {"featured", "high", "medium"}
        assert article.writer_persona

    def test_respects_length_limits(self, trained_writer):
        event = SAMPLE_EVENTS[0]
        article = trained_writer.generate_article(
            title=event["title"], source_name="Test Wire", raw_content=event["raw_content"]
        )
        assert len(article.headline) <= 100
        assert len(article.excerpt) <= 200
        assert len(article.content.split()) >= 250
        assert "\n\n" in article.content  # has paragraphs

    def test_priority_sequence_guarantees_featured_then_high(self, trained_writer):
        priorities = []
        for _ in range(5):
            event = SAMPLE_EVENTS[0]
            article = trained_writer.generate_article(
                title=event["title"], source_name="Test Wire", raw_content=event["raw_content"]
            )
            priorities.append(article.priority)
        assert priorities == ["featured", "high", "high", "medium", "medium"]

    def test_deterministic_with_seed(self):
        articles = []
        for _ in range(2):
            writer = MarkovWriter(seed=7)
            writer.train(SAMPLE_EVENTS)
            event = SAMPLE_EVENTS[1]
            articles.append(
                writer.generate_article(
                    title=event["title"], source_name="Test Wire", raw_content=event["raw_content"]
                )
            )
        assert articles[0] == articles[1]

    def test_classifies_sections_by_keywords(self, trained_writer):
        assert trained_writer._classify_section(ECON_TEXT) == "Economics"
        assert trained_writer._classify_section(TECH_TEXT) == "Technology"
        assert trained_writer._classify_section("nothing relevant here") == "World"

    def test_untrained_writer_self_trains_on_event(self):
        writer = MarkovWriter(seed=3)
        article = writer.generate_article(
            title="Quiet Day In Local Markets", source_name="Test Wire", raw_content=ECON_TEXT
        )
        assert article is not None
        assert len(article.content.split()) >= 250

    def test_returns_none_when_no_text_available(self):
        writer = MarkovWriter(seed=3)
        article = writer.generate_article(title="", source_name="Test Wire", raw_content="")
        assert article is None

    def test_persona_matches_section(self, trained_writer):
        event = SAMPLE_EVENTS[1]
        article = trained_writer.generate_article(
            title=event["title"], source_name="Test Wire", raw_content=event["raw_content"]
        )
        # Technology section maps to Marcus Webb per SECTION_PERSONA_MAP
        assert article.section == "Technology"
        assert "Marcus Webb" in article.writer_persona
