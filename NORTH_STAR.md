# North Star

The guiding document for news_site. Future agent sessions: read this first.
It defines what this project is becoming, the constraints that never bend,
and how to break ties when the owner is hands-off. Update it only when
direction genuinely changes (owner signal), not for tactical pivots.
Tactical state lives in Linear (News Site project); this file is direction.

## Mission

An AI newsroom that produces truthful, factual news analysis drawing
reasonable conclusions -- published to its own website and syndicated as
videos and posts -- run end to end by agents at zero marginal cost.

## The Idea

Most news commentary is engagement bait or partisan. The bet behind this
project is that there is durable appeal -- and real comedy -- in a
publication whose entire brand is drawing reasonable conclusions: lay out
what happened, cite the sources, make the obvious good-faith points, and
stop. A website about reasonable conclusions.

The website is home base; video and social are how people find it. One
editorial pipeline feeds every channel.

## Editorial Identity

- Truthful and factual. Every claim traceable to a source. Mechanical
  generation (extractive) is factual by construction; model-written copy
  must be checked against its sources.
- Reasonable conclusions. Analysis ends with the measured takeaway a
  sensible person would draw, stated plainly. No hot takes, no outrage.
- Good points, briefly. One genuinely good point beats ten filler
  paragraphs. Quality over volume.
- Transparent about being AI-made. Bylines stay, but the site never
  pretends to be human journalists.
- No kitsch. Standing rule: horoscopes and fake tickers were tried and
  cut. Decoration loses to factual grounding every time.

## Product Surfaces

1. Website (exists): newspaper-style front page, article pages, editorial
   images from source feeds. Canonical home; everything links back here.
2. YouTube (future): short news-analysis videos produced from pipeline
   scripts. Free account; phone verification at most.
3. X/Twitter or similar (maybe): post-sized renditions linking back.
   Only if free and within platform automation rules.
4. RSS out (future): the site syndicates itself. Cheap and on-brand.

## Pipeline (target architecture)

The owner's three stages, made concrete:

1. Events analysis -- cluster scraped stories across sources (the same
   event from BBC + Guardian + NPR = one event), rank by significance,
   attach the evidence set.
2. Story suggestion -- a ranked queue of stories worth making: the event,
   the angle, a candidate reasonable conclusion, the sources.
3. Production -- from a suggestion, render per channel:
   - Article (site): extractive or model-written, sourced.
   - Script (YouTube): spoken-word rendition of the article.
   - Video: script -> local TTS -> assembled with story imagery and
     captions via ffmpeg -> upload. All local, all free.
   - Post (X): one-paragraph rendition plus link.

Each stage must be independently useful: the site works without video;
suggestions are worth reading even if nothing gets auto-produced.

## Hard Constraints

- Zero dollars. No paid APIs, hosting, tools, or assets. Existing
  project_infra servers are sunk cost and fair game. Free tiers only when
  they do not require a payment method on file.
- Identity: never provide government ID to any platform or service.
  Phone-number verification is acceptable. No credit cards anywhere.
- Editorial intelligence comes from agent sessions (the owner's existing
  Claude subscription), not metered API calls. The runtime pipeline --
  scrape, generate, publish, produce, upload -- must run with no LLM call.
  The Claude writer engine stays parked until explicitly unparked.
- Hands-off: the owner sets direction; agents do the work. Recurring
  manual effort is a design bug.
- Don't go crazy: simplest version of each stage first; ship increments;
  no speculative platforms or features.
- project_infra is append-only and must not be broken (WEA shares it).

## Horizons

- H1 -- Credible site (in progress, Linear WPA-151): extractive writer,
  story clustering, deploy to project_infra, scheduled daily editions.
- H2 -- Editorial layer: events analysis, story suggestion queue, the
  reasonable-conclusions article format with cited sources.
- H3 -- Video: script rendition, local TTS plus ffmpeg assembly, YouTube
  channel, upload automation.
- H4 -- Distribution and feedback: X posts, RSS out, performance signals
  feeding story suggestion.

Order is advisory; each horizon ships in small pieces.

## Non-Goals

- Monetization, ads, growth hacking (revisit only on owner signal).
- Engagement-optimized or partisan content.
- Original investigative reporting or unverifiable claims.
- Paid stock assets, voices, hosting, or domains.
- Any platform requiring ID verification or a payment instrument.

## Success Criteria

- A stranger cannot find a factual claim on the site without a source.
- A fresh edition publishes daily with zero human touches.
- A video goes from story suggestion to uploaded YouTube draft with zero
  human touches and zero dollars spent.
- Owner involvement: minutes per week, direction-setting only.

## Open Questions

- Brand: keep "AI NEWS" or rename around the reasonable-conclusions
  identity? Owner floated the concept; naming undecided.
- X/Twitter: free-tier posting limits and automation ToS need a check
  before committing to the channel.
- WEA synergy: world_events_analysis already does event analysis (on
  prediction markets). Share components or stay separate?
- Video voice: which local TTS is good enough (piper? macOS say?) --
  needs a bake-off in H3.

## Relationship To Other Projects

- project_infra: hosting target; deploy checklist lives in the WPA-151
  handoff document.
- world_events_analysis: conceptual sibling, no code coupling today.

## For Future Agent Sessions

When a choice trades off cost, factuality, owner effort, or scope, the
constraint order is: truthfulness > zero cost > hands-off > scope
restraint. If a proposed feature fails one of the Hard Constraints, the
answer is no without needing to ask.
