# Story Writer

LLM-powered article generation module that transforms raw news events into polished articles.

## Purpose

Takes unprocessed events from the backend API, uses Claude to generate well-written articles with distinct writer personas, and submits the generated articles back to the API.

## Architecture

```
story_writer/
  run_writer.py       # CLI entry point
  writer.py           # ArticleWriter class using Anthropic SDK
  personas.py         # Writer persona definitions
  prompts/
    article_prompt.py # Prompt templates for article generation
    system_prompts.py # System prompts for each persona
```

## Usage

```bash
# From project root
source .venv/bin/activate

# Normal run (generates and submits articles)
python story_writer/run_writer.py

# Dry run (shows what would be generated)
python story_writer/run_writer.py --dry-run

# Limit events to process
python story_writer/run_writer.py --limit 5

# Custom API URL
python story_writer/run_writer.py --api-url http://localhost:8000
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Required. Your Claude API key.

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
2. For each event:
   - Selects appropriate writer persona
   - Constructs prompt with event content
   - Calls Claude API to generate article
   - Parses response into `GeneratedArticle`
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
