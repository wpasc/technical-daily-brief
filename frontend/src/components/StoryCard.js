import React from 'react';

function StoryCard({ story }) {
  return (
    <article className="story-card">
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
