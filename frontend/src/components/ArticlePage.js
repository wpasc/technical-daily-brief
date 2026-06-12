import React from 'react';

function ArticlePage({ story, onBack }) {
  if (!story) return null;

  return (
    <article className="article-page">
      <button className="back-link" onClick={onBack}>
        &larr; Front Page
      </button>
      <span className="section-badge">{story.section}</span>
      <h2>{story.title}</h2>
      <div className="meta">
        <span>By {story.writer_persona}</span>
        <span> | </span>
        <span>{new Date(story.published_at).toLocaleDateString()}</span>
      </div>
      {story.image_url && (
        <figure className="story-image article-image">
          <img src={story.image_url} alt={story.title} />
          {story.image_credit && <figcaption>Photo: {story.image_credit}</figcaption>}
        </figure>
      )}
      <div className="article-body">
        {story.content.split('\n\n').map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>
    </article>
  );
}

export default ArticlePage;
