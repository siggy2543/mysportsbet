import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8080/api';

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [bankroll, setBankroll] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [recsResponse, bankrollResponse] = await Promise.all([
        fetch(`${API_BASE}/recommendations/NBA`).then(r => r.json()),
        fetch(`${API_BASE}/bankroll`).then(r => r.json())
      ]);
      
      setRecommendations(recsResponse.recommendations || []);
      setBankroll(bankrollResponse);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateBankroll = async (newBalance) => {
    try {
      await axios.post(`${API_BASE}/bankroll/update?balance=${newBalance}`);
      fetchData();
    } catch (error) {
      console.error('Error updating bankroll:', error);
    }
  };

  const logBetResult = async (betId, amount, won, payout = 0) => {
    try {
      await axios.post(`${API_BASE}/log-bet?bet_id=${betId}&amount=${amount}&won=${won}&payout=${payout}`);
      fetchData();
    } catch (error) {
      console.error('Error logging bet:', error);
    }
  };

  const formatCurrency = (amount) => `$${amount.toFixed(2)}`;
  const formatPercentage = (value) => `${value.toFixed(1)}%`;

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#28a745';
    if (confidence >= 70) return '#ffc107';
    return '#dc3545';
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#dc3545';
      default: return '#6c757d';
    }
  };

  if (loading && !bankroll) {
    return (
      <div className="app">
        <div className="loading">
          <h2>🔄 Loading Sports Betting Dashboard...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎯 Legal Sports Betting Analysis</h1>
        <div className="header-info">
          <span className="status">✅ LIVE</span>
          <span className="update-time">Last update: {lastUpdate.toLocaleTimeString()}</span>
        </div>
      </header>

      {bankroll && (
        <div className="bankroll-section">
          <div className="bankroll-card">
            <h3>💰 Bankroll Status</h3>
            <div className="bankroll-grid">
              <div className="bankroll-item">
                <span className="label">Balance:</span>
                <span className="value">{formatCurrency(bankroll.balance)}</span>
              </div>
              <div className="bankroll-item">
                <span className="label">Daily Limit:</span>
                <span className="value">{formatCurrency(bankroll.daily_limit)}</span>
              </div>
              <div className="bankroll-item">
                <span className="label">Daily Remaining:</span>
                <span className="value">{formatCurrency(bankroll.daily_remaining)}</span>
              </div>
              <div className="bankroll-item">
                <span className="label">Suggested Bet:</span>
                <span className="value">{formatCurrency(bankroll.suggested_bet)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="recommendations-section">
        <div className="section-header">
          <h2>🎯 Today's Betting Recommendations</h2>
          <button onClick={fetchData} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>

        {recommendations.length === 0 ? (
          <div className="no-recommendations">
            <h3>No high-confidence recommendations available</h3>
            <p>Waiting for games with 70%+ confidence threshold...</p>
          </div>
        ) : (
          <div className="recommendations-grid">
            {recommendations.map((rec, index) => (
              <div key={rec.id} className="recommendation-card">
                <div className="card-header">
                  <h3>{rec.matchup}</h3>
                  <span className="sport-badge">{rec.sport}</span>
                </div>
                
                <div className="bet-info">
                  <div className="bet-main">
                    <span className="bet-text">{rec.bet}</span>
                    <span 
                      className="confidence"
                      style={{ color: getConfidenceColor(rec.confidence) }}
                    >
                      {formatPercentage(rec.confidence)} confidence
                    </span>
                  </div>
                  
                  <div className="bet-details">
                    <div className="detail-item">
                      <span>Expected Value:</span>
                      <span className={rec.expected_value > 0 ? 'positive' : 'negative'}>
                        {rec.expected_value > 0 ? '+' : ''}{rec.expected_value}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span>Suggested Bet:</span>
                      <span className="bet-amount">{formatCurrency(rec.bet_size)}</span>
                    </div>
                    <div className="detail-item">
                      <span>Kelly %:</span>
                      <span>{formatPercentage(rec.kelly_pct)}</span>
                    </div>
                    <div className="detail-item">
                      <span>Risk Level:</span>
                      <span 
                        className="risk-badge"
                        style={{ color: getRiskColor(rec.risk) }}
                      >
                        {rec.risk.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="odds-section">
                  <h4>Odds:</h4>
                  <div className="odds-grid">
                    <span>Home: {rec.odds.home_ml}</span>
                    <span>Away: {rec.odds.away_ml}</span>
                  </div>
                </div>

                <div className="reasoning">
                  <h4>AI Analysis:</h4>
                  <p>{rec.reasoning}</p>
                </div>

                <div className="manual-betting-notice">
                  <span className="warning">⚠️ MANUAL BETTING REQUIRED</span>
                  <p>Place this bet manually through official DraftKings website/app</p>
                </div>

                <div className="action-buttons">
                  <button 
                    className="btn-primary"
                    onClick={() => window.open('https://sportsbook.draftkings.com', '_blank')}
                  >
                    🎯 Place Bet on DraftKings
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="compliance-footer">
        <div className="compliance-notice">
          <h4>🔒 Legal Compliance Notice</h4>
          <ul>
            <li>✅ Analysis only - No automated betting</li>
            <li>✅ Manual execution required</li>
            <li>✅ Terms of Service compliant</li>
            <li>✅ Educational purpose only</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;