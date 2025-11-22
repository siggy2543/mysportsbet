import React, { useState, useEffect } from 'react';
import './EnhancedInteractiveApp.css';

const EnhancedInteractiveApp = () => {
  const [activeTab, setActiveTab] = useState('moneylines');
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [moneylines, setMoneylines] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [playerProps, setPlayerProps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [globalSports, setGlobalSports] = useState({});

  // Enhanced sports list with global coverage - 22+ sports
  const sportsOptions = [
    { value: 'NBA', label: '🏀 NBA', region: 'US' },
    { value: 'NFL', label: '🏈 NFL', region: 'US' },
    { value: 'NHL', label: '🏒 NHL', region: 'US' },
    { value: 'MLB', label: '⚾ MLB', region: 'US' },
    { value: 'EPL', label: '⚽ Premier League', region: 'Global' },
    { value: 'LALIGA', label: '⚽ La Liga', region: 'Global' },
    { value: 'BUNDESLIGA', label: '⚽ Bundesliga', region: 'Global' },
    { value: 'SERIEA', label: '⚽ Serie A', region: 'Global' },
    { value: 'LIGUE1', label: '⚽ Ligue 1', region: 'Global' },
    { value: 'CHAMPIONSLEAGUE', label: '⚽ Champions League', region: 'Global' },
    { value: 'ATP', label: '🎾 ATP Tennis', region: 'Global' },
    { value: 'WTA', label: '🎾 WTA Tennis', region: 'Global' },
    { value: 'CRICKET', label: '🏏 Cricket', region: 'Global' },
    { value: 'RUGBY', label: '🏉 Rugby', region: 'Global' },
    { value: 'FORMULA1', label: '🏎️ Formula 1', region: 'Global' },
    { value: 'MMA', label: '🥊 MMA/UFC', region: 'Global' },
    { value: 'BOXING', label: '🥊 Boxing', region: 'Global' },
    { value: 'GOLF', label: '⛳ Golf', region: 'Global' },
    { value: 'ESPORTS', label: '🎮 E-Sports', region: 'Global' },
    { value: 'DARTS', label: '🎯 Darts', region: 'Global' },
    { value: 'SNOOKER', label: '🎱 Snooker', region: 'Global' },
    { value: 'CYCLING', label: '🚴 Cycling', region: 'Global' }
  ];

  const fetchData = async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      // Fetch comprehensive data from all enhanced endpoints
      const [moneylineResponse, parlayResponse, playerPropsResponse, globalSportsResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/recommendations/${selectedSport}`),
        fetch(`http://localhost:8000/api/parlays/${selectedSport}`),
        fetch(`http://localhost:8000/api/player-props/${selectedSport}`),
        fetch(`http://localhost:8000/api/global-sports`)
      ]);

      const moneylineData = await moneylineResponse.json();
      const parlayData = await parlayResponse.json();
      const playerPropsData = await playerPropsResponse.json();
      const globalData = await globalSportsResponse.json();

      setMoneylines(moneylineData.recommendations || []);
      setParlays(parlayData.parlays || []);
      setPlayerProps(playerPropsData.player_props || []);
      setGlobalSports(globalData || {});

      setLastUpdate(new Date().toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour12: true
      }));

      // Log successful data fetch
      console.log(`✅ Live data updated for ${selectedSport}:`, {
        moneylines: moneylineData.recommendations?.length || 0,
        parlays: parlayData.parlays?.length || 0,
        playerProps: playerPropsData.player_props?.length || 0,
        globalSports: Object.keys(globalData || {}).length
      });

    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGlobalSports = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/global-sports');
      const data = await response.json();
      setGlobalSports(data || {});
      console.log('Global sports data loaded:', Object.keys(data || {}).length, 'sports');
    } catch (error) {
      console.error('Error fetching global sports:', error);
      setGlobalSports({});
    }
  };

  useEffect(() => {
    fetchData();
    fetchGlobalSports();
  }, [selectedSport]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchData, 20000); // Refresh every 20 seconds for live betting
      return () => clearInterval(interval);
    }
  }, [autoRefresh, selectedSport]);

  const getConfidenceColor = (confidence) => {
    if (confidence >= 85) return '#00ff88';
    if (confidence >= 75) return '#00d4ff';
    if (confidence >= 65) return '#ffaa00';
    return '#ff4757';
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'low': return '#00ff88';
      case 'medium': return '#ffaa00';
      case 'high': return '#ff6b6b';
      default: return '#888';
    }
  };

  const formatOdds = (odds) => {
    if (typeof odds === 'number') {
      return odds > 0 ? `+${odds}` : `${odds}`;
    }
    return 'N/A';
  };

  const renderMoneylines = () => (
    <div className="recommendations-grid">
      {moneylines.map((rec, index) => (
        <div key={rec.id || index} className="recommendation-card">
          <div className="card-header">
            <h3 className="matchup">{rec.matchup}</h3>
            <div className="sport-badge">{selectedSport}</div>
          </div>
          
          <div className="bet-info">
            <div className="bet-type">{rec.bet}</div>
            <div className="odds">{formatOdds(rec.odds?.recommended_odds)}</div>
          </div>

          <div className="confidence-section">
            <div className="confidence-label">Confidence</div>
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ 
                  width: `${rec.confidence}%`,
                  backgroundColor: getConfidenceColor(rec.confidence)
                }}
              />
              <span className="confidence-text">{rec.confidence?.toFixed(1)}%</span>
            </div>
          </div>

          <div className="metrics-row">
            <div className="metric">
              <span className="metric-label">Expected Value</span>
              <span className="metric-value">{(rec.expected_value * 100)?.toFixed(1)}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Kelly %</span>
              <span className="metric-value">{rec.kelly_pct?.toFixed(1)}%</span>
            </div>
          </div>

          <div className="risk-row">
            <span className="risk-label">Risk Level:</span>
            <span 
              className="risk-badge"
              style={{ backgroundColor: getRiskColor(rec.risk) }}
            >
              {rec.risk?.toUpperCase()}
            </span>
          </div>

          {rec.game_theory_score && (
            <div className="game-theory-score">
              <span>🧠 Game Theory Edge: {rec.game_theory_score?.toFixed(1)}</span>
            </div>
          )}

          <div className="reasoning">
            <p>{rec.reasoning}</p>
          </div>

          <div className="manual-warning">
            ⚠️ Manual betting required - Legal compliance mode
          </div>
        </div>
      ))}
    </div>
  );

  const renderParlays = () => (
    <div className="parlays-grid">
      {parlays.map((parlay, index) => (
        <div key={parlay.id || index} className="parlay-card">
          <div className="parlay-header">
            <h3 className="parlay-title">{parlay.legs?.length}-Leg Parlay</h3>
            <div className="parlay-odds">+{Math.round((parlay.combined_odds - 1) * 100)}</div>
          </div>

          <div className="parlay-metrics">
            <div className="parlay-metric">
              <span className="metric-label">Combined Confidence</span>
              <div className="confidence-bar">
                <div 
                  className="confidence-fill"
                  style={{ 
                    width: `${parlay.total_confidence}%`,
                    backgroundColor: getConfidenceColor(parlay.total_confidence)
                  }}
                />
                <span className="confidence-text">{parlay.total_confidence?.toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="parlay-payout">
              <span className="metric-label">Expected Payout</span>
              <span className="payout-amount">${parlay.expected_payout?.toFixed(2)}</span>
            </div>
          </div>

          <div className="parlay-legs">
            {parlay.legs?.map((leg, legIndex) => (
              <div key={legIndex} className="parlay-leg">
                <div className="leg-matchup">{leg.matchup}</div>
                <div className="leg-bet">{leg.bet}</div>
                <div className="leg-confidence">{leg.confidence?.toFixed(1)}%</div>
              </div>
            ))}
          </div>

          <div className="parlay-risk">
            <span className="risk-label">Risk Level:</span>
            <span 
              className="risk-badge"
              style={{ backgroundColor: getRiskColor(parlay.risk_level) }}
            >
              {parlay.risk_level?.toUpperCase()}
            </span>
          </div>

          <div className="correlation-risk">
            <span>🔗 Correlation Risk: {(parlay.correlation_risk * 100)?.toFixed(1)}%</span>
          </div>

          <div className="game-theory-edge">
            <span>🧠 Game Theory Edge: {parlay.game_theory_edge?.toFixed(1)}</span>
          </div>

          <div className="parlay-reasoning">
            <p>{parlay.reasoning}</p>
          </div>

          <div className="manual-warning">
            ⚠️ Manual betting required - Legal compliance mode
          </div>
        </div>
      ))}
    </div>
  );

  const renderPlayerProps = () => (
    <div className="player-props-grid">
      {playerProps.map((prop, index) => (
        <div key={index} className="player-prop-card">
          <div className="prop-header">
            <h3 className="player-name">{prop.player}</h3>
            <div className="game-info">{prop.game}</div>
          </div>

          <div className="prop-details">
            <div className="prop-type">{prop.prop_type?.replace('_', ' ').toUpperCase()}</div>
            <div className="prop-line">Line: {prop.line}</div>
          </div>

          <div className="prop-prediction">
            <div className="prediction-badge">
              <span className="prediction-text">{prop.prediction?.toUpperCase()}</span>
              <span className="prop-odds">
                {prop.prediction === 'over' ? formatOdds(prop.over_odds) : formatOdds(prop.under_odds)}
              </span>
            </div>
          </div>

          <div className="confidence-section">
            <div className="confidence-label">Confidence</div>
            <div className="confidence-bar">
              <div 
                className="confidence-fill"
                style={{ 
                  width: `${prop.confidence}%`,
                  backgroundColor: getConfidenceColor(prop.confidence)
                }}
              />
              <span className="confidence-text">{prop.confidence?.toFixed(1)}%</span>
            </div>
          </div>

          <div className="prop-reasoning">
            <p>{prop.reasoning}</p>
          </div>

          <div className="manual-warning">
            ⚠️ Manual betting required - Legal compliance mode
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="enhanced-interactive-app">
      <div className="app-header">
        <h1 className="app-title">🎯 Enhanced Live Sports Betting Platform</h1>
        <div className="platform-stats">
          <div className="stat-item">
            <span className="stat-label">Global Sports:</span>
            <span className="stat-value">22+</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Game Theory:</span>
            <span className="stat-value">ACTIVE</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">🔴 Live Data:</span>
            <span className="stat-value">{loading ? '🔄 UPDATING...' : (lastUpdate || 'Loading...')}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Auto-Refresh:</span>
            <span className="stat-value">{autoRefresh ? '🟢 ON (20s)' : '🔴 OFF'}</span>
          </div>
        </div>
        <div className="header-controls">
          <div className="sport-selector">
            <select 
              value={selectedSport} 
              onChange={(e) => setSelectedSport(e.target.value)}
              className="sport-select"
            >
              {sportsOptions.map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label} {sport.region === 'Global' ? '🌍' : '🇺🇸'}
                </option>
              ))}
            </select>
          </div>
          
          <div className="refresh-controls">
            <label className="auto-refresh-toggle">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto-refresh
            </label>
            <button 
              onClick={fetchData} 
              className="refresh-button"
              disabled={loading}
            >
              {loading ? '🔄' : '↻'} Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="status-bar">
        <div className="status-item">
          <span className="status-label">Last Update:</span>
          <span className="status-value">{lastUpdate || 'Never'} EST</span>
        </div>
        <div className="status-item">
          <span className="status-label">Sport:</span>
          <span className="status-value">{selectedSport}</span>
        </div>
        <div className="status-item">
          <span className="status-label">Features:</span>
          <span className="status-value">🧠 Game Theory | 🎯 AI Enhanced</span>
        </div>
      </div>

      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'moneylines' ? 'active' : ''}`}
          onClick={() => setActiveTab('moneylines')}
        >
          💰 Moneylines ({moneylines.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'parlays' ? 'active' : ''}`}
          onClick={() => setActiveTab('parlays')}
        >
          🎲 Parlays ({parlays.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'player-props' ? 'active' : ''}`}
          onClick={() => setActiveTab('player-props')}
        >
          👤 Player Props ({playerProps.length})
        </button>
      </div>

      <div className="tab-content">
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner">🔄</div>
            <div className="loading-text">Loading {activeTab}...</div>
          </div>
        )}

        {activeTab === 'moneylines' && renderMoneylines()}
        {activeTab === 'parlays' && renderParlays()}
        {activeTab === 'player-props' && renderPlayerProps()}

        {!loading && (
          (activeTab === 'moneylines' && moneylines.length === 0) ||
          (activeTab === 'parlays' && parlays.length === 0) ||
          (activeTab === 'player-props' && playerProps.length === 0)
        ) && (
          <div className="no-data">
            <div className="no-data-icon">📊</div>
            <div className="no-data-text">
              No {activeTab.replace('-', ' ')} available for {selectedSport} at this time.
            </div>
            <button onClick={fetchData} className="retry-button">
              Try Again
            </button>
          </div>
        )}
      </div>

      <div className="app-footer">
        <div className="footer-info">
          <span>🚨 Manual Betting Required | ⚖️ Legal Compliance Mode</span>
          <span>🧠 Enhanced with Game Theory Algorithms</span>
          <span>🌍 Global Sports Coverage Available</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedInteractiveApp;