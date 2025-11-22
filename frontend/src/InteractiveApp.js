import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8080/api';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [bankroll, setBankroll] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [error, setError] = useState(null);
  const [timezone, setTimezone] = useState('EST');

  const fetchBankroll = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/bankroll`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setBankroll(data);
    } catch (error) {
      console.error('Error fetching bankroll:', error);
      setError(`Bankroll error: ${error.message}`);
    }
  }, []);

  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/recommendations/${selectedSport}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      
      // Handle both old and new API response formats
      if (data.recommendations) {
        setRecommendations(data.recommendations);
        setTimezone(data.timezone || 'EST');
      } else if (Array.isArray(data)) {
        setRecommendations(data);
      } else {
        setRecommendations([]);
      }
      
      setLastUpdate(new Date().toLocaleTimeString('en-US', {timeZone: 'America/New_York'}));
      setError(null);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError(`API error: ${error.message}`);
      setRecommendations([]);
    }
  }, [selectedSport]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchBankroll(), fetchRecommendations()]);
    setLoading(false);
  }, [fetchBankroll, fetchRecommendations]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(fetchData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [fetchData, autoRefresh]);

  const handleSportChange = (sport) => {
    setSelectedSport(sport);
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const manualRefresh = () => {
    fetchData();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 85) return '#00ff88';
    if (confidence >= 75) return '#ffaa00';
    return '#ff6b6b';
  };

  const getEVColor = (ev) => {
    if (ev > 0.2) return '#00ff88';
    if (ev > 0.1) return '#ffaa00';
    return '#ff6b6b';
  };

  const formatTime = (timeString) => {
    try {
      const date = new Date(timeString);
      return date.toLocaleString('en-US', {
        timeZone: 'America/New_York',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return 'TBD';
    }
  };

  if (loading && !recommendations.length) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <p>Loading live betting data for {timezone} timezone...</p>
        <p>Fetching {selectedSport} recommendations...</p>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="header">
        <div className="header-main">
          <h1>🏀 Live Sports Betting Dashboard</h1>
          <div className="timezone-badge">{timezone} Time Zone</div>
        </div>
        
        <div className="header-controls">
          <div className="sport-selector">
            {['NBA', 'NFL', 'NHL', 'MLB'].map(sport => (
              <button
                key={sport}
                className={`sport-btn ${selectedSport === sport ? 'active' : ''}`}
                onClick={() => handleSportChange(sport)}
              >
                {sport}
              </button>
            ))}
          </div>
          
          <div className="control-buttons">
            <button 
              className={`auto-refresh-btn ${autoRefresh ? 'active' : ''}`}
              onClick={toggleAutoRefresh}
            >
              {autoRefresh ? '🔄 Auto' : '⏸️ Manual'}
            </button>
            <button className="refresh-btn" onClick={manualRefresh}>
              🔄 Refresh Now
            </button>
          </div>
        </div>

        <div className="bankroll-info">
          {bankroll && (
            <>
              <div className="bankroll-item">
                <span className="label">Total Bankroll:</span>
                <span className="value">${bankroll.total_bankroll || bankroll.total || '200.00'}</span>
              </div>
              <div className="bankroll-item">
                <span className="label">Daily Remaining:</span>
                <span className="value">${bankroll.daily_remaining || '50.00'}</span>
              </div>
            </>
          )}
        </div>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error} - Showing available data
        </div>
      )}

      <main className="main-content">
        <div className="section-header">
          <h2>🎯 Live {selectedSport} Recommendations</h2>
          <div className="update-info">
            {lastUpdate && (
              <span className="last-update">
                Last updated: {lastUpdate} {timezone}
              </span>
            )}
            <span className="recommendations-count">
              {recommendations.length} active recommendations
            </span>
          </div>
        </div>

        <div className="recommendations-grid">
          {recommendations.length > 0 ? (
            recommendations.map((rec, index) => (
              <div key={rec.id || index} className="recommendation-card interactive">
                <div className="game-header">
                  <h3 className="matchup">{rec.matchup}</h3>
                  <div className="game-time">{formatTime(rec.start_time)}</div>
                </div>

                <div className="confidence-section">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill" 
                      style={{ 
                        width: `${rec.confidence}%`,
                        backgroundColor: getConfidenceColor(rec.confidence)
                      }}
                    ></div>
                  </div>
                  <span className="confidence-text">
                    {rec.confidence.toFixed(1)}% confidence
                  </span>
                </div>

                <div className="bet-details">
                  <div className="bet-info">
                    <div className="bet-type">{rec.bet_type || 'Moneyline'}</div>
                    <div className="selection">{rec.selection || rec.bet}</div>
                  </div>
                  
                  <div className="bet-metrics">
                    <div className="metric">
                      <span className="metric-label">Suggested Bet:</span>
                      <span className="metric-value">${rec.suggested_amount || rec.bet_size}</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Expected Value:</span>
                      <span 
                        className={`metric-value ${rec.expected_value > 0 ? 'positive' : 'negative'}`}
                        style={{ color: getEVColor(rec.expected_value) }}
                      >
                        {rec.expected_value > 0 ? '+' : ''}{rec.expected_value.toFixed(3)}
                      </span>
                    </div>
                    {rec.kelly_pct && (
                      <div className="metric">
                        <span className="metric-label">Kelly %:</span>
                        <span className="metric-value">{rec.kelly_pct}%</span>
                      </div>
                    )}
                  </div>

                  {rec.odds && (
                    <div className="odds-section">
                      <h4>Odds:</h4>
                      <div className="odds-grid">
                        {rec.odds.home_ml && (
                          <div className="odds-item">
                            <span>Home ML:</span>
                            <span>{rec.odds.home_ml > 0 ? '+' : ''}{rec.odds.home_ml}</span>
                          </div>
                        )}
                        {rec.odds.away_ml && (
                          <div className="odds-item">
                            <span>Away ML:</span>
                            <span>{rec.odds.away_ml > 0 ? '+' : ''}{rec.odds.away_ml}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {rec.reasoning && (
                  <div className="reasoning-section">
                    <h4>Analysis:</h4>
                    <p>{rec.reasoning}</p>
                  </div>
                )}

                <div className="action-section">
                  <div className="risk-badge" data-risk={rec.risk}>
                    {rec.risk} risk
                  </div>
                  <div className="legal-notice">
                    ⚖️ Manual betting required - Place on DraftKings
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="no-recommendations">
              <div className="no-recs-content">
                <p>🔍 No {selectedSport} recommendations available</p>
                <p>Try refreshing or check back in a few minutes</p>
                <button className="refresh-btn-large" onClick={manualRefresh}>
                  🔄 Refresh Data
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="dashboard-footer">
          <div className="system-status">
            <div className="status-item">
              <span className="status-indicator active"></span>
              <span>Live Data Active</span>
            </div>
            <div className="status-item">
              <span className="status-indicator active"></span>
              <span>Legal Compliance Mode</span>
            </div>
            <div className="status-item">
              <span className="status-indicator active"></span>
              <span>{timezone} Timezone</span>
            </div>
          </div>

          <div className="compliance-notice">
            <h3>🛡️ Legal Compliance Notice</h3>
            <ul>
              <li>All recommendations are for analysis purposes only</li>
              <li>Manual verification required before placing any bets</li>
              <li>Always bet responsibly within your means</li>
              <li>Updated live for {timezone} timezone</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;