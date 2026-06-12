import React from 'react';

function Header() {
  const dateline = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <header className="header">
      <div className="container header-content">
        <h1>AI NEWS</h1>
        <p className="tagline">Automated news from open-source feeds</p>
        <div className="masthead-line">
          <span>{dateline}</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
