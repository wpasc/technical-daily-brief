import React from 'react';

function FeaturedStory({ story }) {
  if (!story) return null;

  return (
    <article className="featured-story">
      <span className="section-badge">{story.section}</span>
      <h2>{story.title}</h2>
      <p className="excerpt">{story.excerpt}</p>
      <div className="meta">
        <span>By {story.writer_persona}</span>
        <span> | </span>
        <span>{new Date(story.published_at).toLocaleDateString()}</span>
      </div>
    </article>
  );
}

export default FeaturedStory;
