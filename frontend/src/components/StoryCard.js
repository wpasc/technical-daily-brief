import React from 'react';

function StoryCard({ story, onSelect }) {
  return (
    <article className="story-card clickable" onClick={() => onSelect(story)}>
      {story.image_url && (
        <figure className="story-image card-image">
          <img src={story.image_url} alt={story.title} loading="lazy" />
        </figure>
      )}
      <span className="section-badge">{story.section}</span>
      <h3>{story.title}</h3>
      <p className="excerpt">{story.excerpt}</p>
      <div className="meta">
        <span>{story.writer_persona}</span>
      </div>
    </article>
  );
}

export default StoryCard;
