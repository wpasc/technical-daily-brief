import React from 'react';
import StoryCard from './StoryCard';

function StoryGrid({ stories, columns = 3 }) {
  if (!stories || stories.length === 0) return null;

  return (
    <div className={`story-grid columns-${columns}`}>
      {stories.map((story) => (
        <StoryCard key={story.id} story={story} />
      ))}
    </div>
  );
}

export default StoryGrid;
