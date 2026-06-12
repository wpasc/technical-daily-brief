"""Zero-cost article generator using Markov chains over scraped text.

No LLM calls. Chains are trained on the current batch of scraped events, so
generated articles remix the day's real news vocabulary. Each article is
seeded from its own source event to keep it loosely on-topic. Output is
word salad by design; the structure (headline, excerpt, sections, priority)
mirrors the LLM writer so the rest of the pipeline is unchanged.
"""
import logging
import random
import re
from collections import defaultdict
from typing import Optional

from story_writer.article import GeneratedArticle
from story_writer.personas import WriterPersona

logger = logging.getLogger(__name__)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

# Keyword -> section scoring. Zero matches falls back to World.
SECTION_KEYWORDS = {
    "Economics": [
        "economy", "economic", "market", "markets", "inflation", "bank", "banks",
        "trade", "tariff", "stocks", "investors", "gdp", "prices", "earnings",
        "budget", "tax", "jobs", "wages",
    ],
    "Technology": [
        "tech", "technology", "ai", "software", "app", "internet", "cyber",
        "chip", "chips", "robot", "startup", "smartphone", "google", "apple",
        "microsoft", "meta", "amazon", "data",
    ],
    "Science": [
        "science", "scientists", "research", "researchers", "study", "climate",
        "space", "nasa", "vaccine", "health", "disease", "species", "energy",
        "physics", "quantum", "brain", "drug",
    ],
    "Politics": [
        "election", "president", "parliament", "congress", "senate", "minister",
        "government", "policy", "vote", "voters", "campaign", "law", "court",
        "legislation", "senator", "governor",
    ],
    "Culture": [
        "film", "music", "art", "festival", "museum", "book", "fashion",
        "celebrity", "sport", "sports", "game", "tv", "theater", "food",
        "movie", "album",
    ],
    "World": [
        "war", "military", "troops", "nations", "border", "refugees",
        "diplomatic", "treaty", "embassy", "ceasefire", "summit",
    ],
}

HEADLINE_MAX_CHARS = 100
EXCERPT_MAX_CHARS = 200
SENTENCES_PER_PARAGRAPH = 3
MIN_CONTENT_WORDS = 300
MAX_CONTENT_WORDS = 450

# First articles in a run get top billing so the front page has a layout.
PRIORITY_SEQUENCE = ["featured", "high", "high"]


def _truncate_at_word(text: str, limit: int) -> str:
    """Truncate text to limit chars without splitting a word."""
    if len(text) <= limit:
        return text
    cut = text[: limit - 3].rsplit(" ", 1)[0].rstrip(",;:.")
    return cut + "..."


class MarkovChain:
    """Word-level Markov chain of configurable order."""

    def __init__(self, order: int, rng: random.Random):
        self.order = order
        self.rng = rng
        self.transitions: dict[tuple, list[str]] = defaultdict(list)
        self.starts: list[tuple] = []

    def train(self, text: str) -> None:
        """Add text to the chain, sentence by sentence."""
        for sentence in SENTENCE_SPLIT.split(text):
            words = sentence.split()
            if len(words) <= self.order:
                continue
            self.starts.append(tuple(words[: self.order]))
            for i in range(len(words) - self.order):
                state = tuple(words[i : i + self.order])
                self.transitions[state].append(words[i + self.order])

    @property
    def trained(self) -> bool:
        return bool(self.starts)

    def start_states_from(self, text: str) -> list[tuple]:
        """Sentence-start states present in both text and the trained chain."""
        states = []
        for sentence in SENTENCE_SPLIT.split(text):
            words = sentence.split()
            state = tuple(words[: self.order])
            if len(words) > self.order and state in self.transitions:
                states.append(state)
        return states

    def sentence(self, max_words: int = 28, seed_state: Optional[tuple] = None) -> str:
        """Generate one sentence, optionally starting from seed_state."""
        if seed_state is not None and seed_state in self.transitions:
            state = seed_state
        else:
            state = self.rng.choice(self.starts)
        words = list(state)
        while len(words) < max_words:
            followers = self.transitions.get(tuple(words[-self.order :]))
            if not followers:
                break
            words.append(self.rng.choice(followers))
            if words[-1][-1] in ".!?":
                break
        text = " ".join(words)
        text = text[0].upper() + text[1:]
        if text[-1] not in ".!?":
            text += "."
        return text


class MarkovWriter:
    """Drop-in replacement for ArticleWriter that costs nothing to run.

    Call train() with the batch of events first; generate_article() then
    matches the ArticleWriter call signature.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.headline_chain = MarkovChain(order=1, rng=self.rng)
        self.body_chain = MarkovChain(order=2, rng=self.rng)
        self._article_count = 0

    def train(self, events: list[dict]) -> None:
        """Train chains on a batch of events (dicts with title, raw_content)."""
        for event in events:
            self.headline_chain.train(event.get("title", ""))
            self.body_chain.train(event.get("raw_content", ""))

    def generate_article(
        self,
        title: str,
        source_name: str,
        raw_content: str,
        persona: Optional[WriterPersona] = None,
    ) -> Optional[GeneratedArticle]:
        """Generate an article remixing the trained corpus, seeded by this event."""
        if not self.body_chain.trained:
            self.train([{"title": title, "raw_content": raw_content}])
        if not self.body_chain.trained:
            logger.warning("Not enough text to train on, skipping: %s", title[:60])
            return None

        headline = self._headline(title)
        content = self._body(raw_content)
        excerpt = _truncate_at_word(content.split("\n\n")[0].split(". ")[0] + ".", EXCERPT_MAX_CHARS)
        section = self._classify_section(f"{title} {raw_content}")

        if self._article_count < len(PRIORITY_SEQUENCE):
            priority = PRIORITY_SEQUENCE[self._article_count]
        else:
            priority = "medium"
        self._article_count += 1

        if persona is None:
            persona = WriterPersona.for_section(section)

        return GeneratedArticle(
            headline=headline,
            excerpt=excerpt,
            content=content,
            section=section,
            priority=priority,
            writer_persona=f"{persona.name}, {persona.persona}",
        )

    def _headline(self, title: str) -> str:
        chain = self.headline_chain if self.headline_chain.trained else self.body_chain
        seeds = chain.start_states_from(title)
        seed = self.rng.choice(seeds) if seeds else None
        headline = chain.sentence(max_words=12, seed_state=seed).rstrip(".")
        return _truncate_at_word(headline, HEADLINE_MAX_CHARS)

    def _body(self, raw_content: str) -> str:
        target_words = self.rng.randint(MIN_CONTENT_WORDS, MAX_CONTENT_WORDS)
        event_seeds = self.body_chain.start_states_from(raw_content)
        self.rng.shuffle(event_seeds)

        paragraphs = []
        sentences = []
        word_count = 0
        while word_count < target_words:
            # Seed roughly half the sentences from this event's own text.
            seed = event_seeds.pop() if event_seeds and self.rng.random() < 0.5 else None
            sentence = self.body_chain.sentence(seed_state=seed)
            sentences.append(sentence)
            word_count += len(sentence.split())
            if len(sentences) == SENTENCES_PER_PARAGRAPH:
                paragraphs.append(" ".join(sentences))
                sentences = []
        if sentences:
            paragraphs.append(" ".join(sentences))
        return "\n\n".join(paragraphs)

    def _classify_section(self, text: str) -> str:
        lowered = text.lower()
        scores = {}
        for section, keywords in SECTION_KEYWORDS.items():
            scores[section] = sum(
                len(re.findall(rf"\b{re.escape(keyword)}\b", lowered))
                for keyword in keywords
            )
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "World"
