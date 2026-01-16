"""Article generation prompt template."""

ARTICLE_GENERATION_PROMPT = """Write a news article based on this source material:

Title: {title}
Source: {source_name}
Content: {raw_content}

Generate a response in the following JSON format:
{{
    "headline": "A compelling, accurate headline (max 100 characters)",
    "excerpt": "A 1-2 sentence summary capturing the key point (max 200 characters)",
    "content": "The full article (300-500 words). Write in clear, engaging prose with proper paragraphs.",
    "section": "One of: Economics, Technology, World, Politics, Science, Culture",
    "priority": "One of: featured (for major breaking news), high (for important stories), medium (for standard coverage)"
}}

Guidelines:
- Write factually based on the source material
- Do not fabricate quotes or statistics not in the source
- Use clear, accessible language
- Structure with a strong lead paragraph followed by supporting details
- Maintain journalistic objectivity
- If the source is about a minor topic, use "medium" priority
- Only use "featured" for truly major world events

Respond ONLY with the JSON object, no additional text."""

SYSTEM_PROMPT_TEMPLATE = """You are {name}, {persona}. {style_description}

Write news articles that are:
- Factual and well-sourced
- Clear and accessible
- Engaging without being sensational
- Properly structured with a strong lead

You must respond in valid JSON format only."""
