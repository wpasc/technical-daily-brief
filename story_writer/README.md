# Story Writer

Article generation module that transforms raw news events into articles.

Two engines:

- **markov** (default): zero-cost Markov chains trained on the day's scraped
  text. No API calls, no key. Output is word salad that remixes real news
  vocabulary, seeded per-event so each article loosely tracks a real story.
- **claude**: LLM-generated articles via the Anthropic API. Requires
  `ANTHROPIC_API_KEY`. Swap back in when the budget allows.

## Purpose

Takes unprocessed events from the backend API, generates articles with
distinct writer personas, and submits the generated articles back to the API.

## Architecture

```
story_writer/
  run_writer.py       # CLI entry point (--engine markov|claude)
  article.py          # GeneratedArticle dataclass shared by engines
  markov_writer.py    # MarkovWriter: zero-cost chain-based generation
  writer.py           # ArticleWriter class using Anthropic SDK
  personas.py         # Writer persona definitions
  prompts/
    article_prompt.py # Prompt templates for article generation (claude)
    system_prompts.py # System prompts for each persona
```

## Usage

```bash
# From project root
source .venv/bin/activate

# Normal run (markov engine, free)
python story_writer/run_writer.py

# Use Claude instead (requires ANTHROPIC_API_KEY)
python story_writer/run_writer.py --engine claude

# Dry run (shows what would be generated)
python story_writer/run_writer.py --dry-run

# Limit events to process
python story_writer/run_writer.py --limit 5

# Custom API URL
python story_writer/run_writer.py --api-url http://localhost:8000
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Only required for `--engine claude`.

## Writer Personas

Articles are written by one of five AI personas, each with a distinct voice:

| Persona | Style | Best For |
|---------|-------|----------|
| Alex Chen | Data-driven, factual | Analytics, statistics |
| Sarah Mitchell | Investigative, thorough | Deep investigations |
| Marcus Webb | Technical, explanatory | Technology, science |
| Elena Rodriguez | Empathetic, human-focused | Human interest stories |
| David Park | Opinionated, analytical | Commentary, opinion |

Personas are defined in `personas.py` and matched to content type during generation.

## How It Works

1. Fetches unprocessed events from `GET /api/events?processed=false`
2. markov engine only: trains headline/body chains on the whole batch
3. For each event:
   - Generates headline, excerpt, and body (chain sampling or Claude API)
   - Classifies section (keyword scoring or Claude) and selects persona
   - Submits to `POST /api/articles`
   - Marks event as processed via `PATCH /api/events/{id}`

## Generated Article Structure

Each article includes:
- `headline`: Article title
- `content`: Full article body
- `excerpt`: Brief summary (for cards/previews)
- `section`: Category (Politics, Technology, etc.)
- `priority`: Display priority (featured, high, medium)
- `writer_persona`: Which persona wrote it

## Customizing Prompts

Edit files in `prompts/` to adjust:
- `system_prompts.py`: Per-persona system instructions
- `article_prompt.py`: Article generation template

## Data Flow

```
GET /api/events --> ArticleWriter --> Claude API --> GeneratedArticle --> POST /api/articles
       |                                                                        |
       +-- (mark processed) <-- PATCH /api/events/{id} <------------------------+
```
