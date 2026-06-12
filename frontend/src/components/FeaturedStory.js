import React from 'react';

function FeaturedStory({ story, onSelect }) {
  if (!story) return null;

  return (
    <article className="featured-story clickable" onClick={() => onSelect(story)}>
      {story.image_url && (
        <figure className="story-image featured-image">
          <img src={story.image_url} alt={story.title} loading="lazy" />
          {story.image_credit && <figcaption>Photo: {story.image_credit}</figcaption>}
        </figure>
      )}
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
