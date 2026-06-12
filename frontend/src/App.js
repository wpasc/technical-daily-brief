import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import FeaturedStory from './components/FeaturedStory';
import StoryGrid from './components/StoryGrid';
import SectionHeader from './components/SectionHeader';
import ArticlePage from './components/ArticlePage';
import { fetchArticles, mockArticles } from './api/client';

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [useMock, setUseMock] = useState(false);
  const [selectedStory, setSelectedStory] = useState(null);

  useEffect(() => {
    const loadArticles = async () => {
      setLoading(true);
      const data = await fetchArticles();

      if (data && data.length > 0) {
        setArticles(data);
      } else {
        // Fall back to mock data if API returns empty
        setArticles(mockArticles);
        setUseMock(true);
      }

      setLoading(false);
    };

    loadArticles();
  }, []);

  const openStory = (story) => {
    setSelectedStory(story);
    window.scrollTo(0, 0);
  };

  const closeStory = () => setSelectedStory(null);

  // Organize articles by priority
  const featured = articles.find((a) => a.priority === 'featured');
  const high = articles.filter((a) => a.priority === 'high');
  const medium = articles.filter((a) => a.priority === 'medium');

  // Group medium priority by section
  const bySection = medium.reduce((acc, article) => {
    const section = article.section || 'General';
    if (!acc[section]) {
      acc[section] = [];
    }
    acc[section].push(article);
    return acc;
  }, {});

  if (loading) {
    return (
      <>
        <Header />
        <main className="container">
          <div className="loading">Loading articles...</div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="container">
        {useMock && (
          <div style={{
            background: '#fff3cd',
            padding: '12px',
            marginBottom: '20px',
            borderRadius: '4px',
            fontSize: '0.9rem'
          }}>
            Showing demo content. Start the backend and run the scraper to see live articles.
          </div>
        )}

        {selectedStory ? (
          <ArticlePage story={selectedStory} onBack={closeStory} />
        ) : articles.length === 0 ? (
          <div className="empty-state">
            <h3>No Articles Yet</h3>
            <p>Run the scraper and story writer to generate articles.</p>
          </div>
        ) : (
          <>
            {featured && <FeaturedStory story={featured} onSelect={openStory} />}

            {high.length > 0 && (
              <StoryGrid stories={high} columns={2} onSelect={openStory} />
            )}

            {Object.entries(bySection).map(([section, stories]) => (
              <React.Fragment key={section}>
                <SectionHeader title={section} />
                <StoryGrid stories={stories} columns={3} onSelect={openStory} />
              </React.Fragment>
            ))}
          </>
        )}
      </main>

      <footer className="footer">
        <div className="container">
          <p>AI NEWS &mdash; articles generated automatically from public RSS feeds.</p>
        </div>
      </footer>
    </>
  );
}

export default App;
