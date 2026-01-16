const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export async function fetchArticles() {
  try {
    const response = await fetch(`${API_BASE}/articles`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching articles:', error);
    return [];
  }
}

export async function fetchArticle(id) {
  try {
    const response = await fetch(`${API_BASE}/articles/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching article:', error);
    return null;
  }
}

// Mock data for offline development
export const mockArticles = [
  {
    id: '1',
    title: 'Major Climate Summit Reaches Historic Agreement',
    excerpt: 'World leaders have agreed on unprecedented measures to combat climate change at the global summit.',
    content: 'In a landmark decision, world leaders gathered at the International Climate Summit have reached a historic agreement...',
    section: 'World',
    priority: 'featured',
    writer_persona: 'Sarah Mitchell, Investigative Correspondent',
    published_at: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Tech Giants Unveil New AI Safety Standards',
    excerpt: 'Leading technology companies announce joint commitment to responsible AI development.',
    content: 'In a coordinated effort, the worlds largest technology companies have unveiled new safety standards...',
    section: 'Technology',
    priority: 'high',
    writer_persona: 'Marcus Webb, Technology Analyst',
    published_at: new Date().toISOString(),
  },
  {
    id: '3',
    title: 'Central Banks Signal Policy Shift Amid Inflation Concerns',
    excerpt: 'Federal Reserve and European Central Bank indicate potential rate adjustments in coming months.',
    content: 'Central banks around the world are signaling a potential shift in monetary policy...',
    section: 'Economics',
    priority: 'high',
    writer_persona: 'Alex Chen, Senior Analytical Reporter',
    published_at: new Date().toISOString(),
  },
  {
    id: '4',
    title: 'Breakthrough in Quantum Computing Achieved',
    excerpt: 'Scientists demonstrate error-corrected quantum computer for the first time.',
    content: 'Researchers at a leading university have achieved a major breakthrough in quantum computing...',
    section: 'Science',
    priority: 'medium',
    writer_persona: 'Marcus Webb, Technology Analyst',
    published_at: new Date().toISOString(),
  },
  {
    id: '5',
    title: 'New Study Reveals Impact of Remote Work on Productivity',
    excerpt: 'Research shows mixed results for remote work arrangements across different industries.',
    content: 'A comprehensive new study examining remote work patterns has revealed interesting trends...',
    section: 'Economics',
    priority: 'medium',
    writer_persona: 'Alex Chen, Senior Analytical Reporter',
    published_at: new Date().toISOString(),
  },
  {
    id: '6',
    title: 'Cultural Festival Draws Record Crowds',
    excerpt: 'Annual celebration of diverse traditions brings together communities from around the world.',
    content: 'This years International Cultural Festival has drawn record attendance...',
    section: 'Culture',
    priority: 'medium',
    writer_persona: 'Elena Rodriguez, Human Interest Reporter',
    published_at: new Date().toISOString(),
  },
];
