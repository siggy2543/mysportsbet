import React, { useState, useEffect, useCallback, useRef } from 'react';
import './EnhancedInteractiveApp.css';

// Sport emoji mapping for better UI (outside component to avoid re-creation)
const sportEmojiMap = {
  'basketball': '🏀', 'americanfootball': '🏈', 'icehockey': '🏒', 'baseball': '⚾',
  'soccer': '⚽', 'tennis': '🎾', 'cricket': '🏏', 'rugby': '🏉', 'formula1': '🏎️',
  'mma': '🥊', 'boxing': '🥊', 'golf': '⛳', 'cycling': '🚴', 'darts': '🎯',
  'aussierules': '🏉', 'volleyball': '🏐', 'handball': '🤾', 'waterpolo': '🤽',
  'tableTennis': '🏓', 'esports': '🎮', 'snooker': '🎱', 'bowls': '🎳'
};

const EnhancedLiveBettingPlatform = () => {
  // API Base URL - Use port 8000 for API access
  const API_BASE_URL = 'http://localhost:8000';

  // Core State Management 
  const [activeTab, setActiveTab] = useState('live-dashboard');
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [moneylines, setMoneylines] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [playerProps, setPlayerProps] = useState([]);
  const [liveParlays, setLiveParlays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [parlayLegs, setParlayLegs] = useState(2); // New: 2, 3, 4, or 5 legs
  const [parlayBuilder, setParlayBuilder] = useState([]); // New: Multi-leg parlay builder
  
  // Use ref to track loading state for useCallback dependency
  const isLoadingRef = useRef(false);

  // Dynamic sports loaded from The Odds API (all 149 sports)
  const [globalSportsOptions, setGlobalSportsOptions] = useState([]);
  const [sportsLoading, setSportsLoading] = useState(true);
  
  // Load all 149 sports from The Odds API on mount
  useEffect(() => {
    const fetchSports = async () => {
      try {
        setSportsLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/odds/sports`);
        const data = await response.json();
        
        if (data.sports) {
          const formattedSports = data.sports.map(sport => {
            // Get emoji based on sport group/title
            const sportKey = sport.group.toLowerCase().replace(/_/g, '');
            const emoji = sportEmojiMap[sportKey] || sportEmojiMap[sport.key.toLowerCase()] || '🏆';
            
            return {
              value: sport.key,
              label: `${emoji} ${sport.title}`,
              region: sport.group,
              active: sport.active,
              has_outrights: sport.has_outrights,
              description: sport.description,
              markets: ['ML', 'Spread', 'O/U', 'Props', 'Parlays']
            };
          });
          
          // Sort by active first, then alphabetically
          formattedSports.sort((a, b) => {
            if (a.active !== b.active) return b.active - a.active;
            return a.label.localeCompare(b.label);
          });
          
          setGlobalSportsOptions(formattedSports);
          console.log(`✅ Loaded ${data.total_sports} sports (${data.active_sports} active)`);
        }
      } catch (err) {
        console.error('Error fetching sports:', err);
        setError('Failed to load sports list');
        // Fallback to default NBA if API fails
        setGlobalSportsOptions([
          { value: 'NBA', label: '🏀 NBA Basketball', region: 'Basketball', active: true, markets: ['ML', 'O/U', 'Props', 'Parlays'] }
        ]);
      } finally {
        setSportsLoading(false);
      }
    };
    
    fetchSports();
  }, [API_BASE_URL]);

  // Enhanced API Data Fetching
  const fetchComprehensiveData = useCallback(async () => {
    console.log('🚀 fetchComprehensiveData called for sport:', selectedSport, 'loading:', isLoadingRef.current);
    if (isLoadingRef.current) {
      console.log('⏸️ Already loading, skipping request');
      return;
    }
    
    console.log('📡 Starting API fetch for', selectedSport);
    isLoadingRef.current = true;
    setLoading(true);
    setError(null);
    
    try {
      // Parallel fetch all data types for selected sport
      const endpoints = [
        `${API_BASE_URL}/api/recommendations/${selectedSport}`,
        `${API_BASE_URL}/api/parlays/${selectedSport}`,
        `${API_BASE_URL}/api/player-props/${selectedSport}`,
        `${API_BASE_URL}/api/live-parlays/${selectedSport}`,
        `${API_BASE_URL}/api/global-sports`
      ];

      const [
        moneylineRes, 
        parlayRes, 
        playerPropsRes, 
        liveParlayRes,
        globalSportsRes
      ] = await Promise.all(
        endpoints.map(url => fetch(url).catch(err => ({ error: err.message })))
      );

      // Process responses safely with detailed logging
      const processResponse = async (response, fallback = []) => {
        if (response.error) {
          console.error('Network error:', response.error);
          return fallback;
        }
        if (!response.ok) {
          console.error(`HTTP ${response.status} ${response.statusText} for ${response.url}`);
          return fallback;
        }
        try {
          const data = await response.json();
          console.log(`✅ Success: ${response.url} returned ${JSON.stringify(data).length} chars`);
          return data;
        } catch (parseError) {
          console.error('JSON Parse Error:', parseError.message, 'for', response.url);
          return fallback;
        }
      };

      const [
        moneylineData,
        parlayData, 
        playerPropsData,
        liveParlayData,
        globalSportsData
      ] = await Promise.all([
        processResponse(moneylineRes, { recommendations: [] }),
        processResponse(parlayRes, { parlays: [] }),
        processResponse(playerPropsRes, { player_props: [] }),
        processResponse(liveParlayRes, { live_parlays: [] }),
        processResponse(globalSportsRes, {})
      ]);

      // Update state with fetched data
      setMoneylines(moneylineData.recommendations || []);
      setParlays(parlayData.parlays || []);
      setPlayerProps(playerPropsData.player_props || []);
      setLiveParlays(liveParlayData.live_parlays || []);

      setLastUpdate(new Date().toLocaleTimeString('en-US', {
        timeZone: 'America/New_York',
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }));

      // Success logging
      console.log(`🎯 Live data updated for ${selectedSport}:`, {
        moneylines: moneylineData.recommendations?.length || 0,
        parlays: parlayData.parlays?.length || 0,
        playerProps: playerPropsData.player_props?.length || 0,
        liveParlays: liveParlayData.live_parlays?.length || 0,
        globalSports: Object.keys(globalSportsData || {}).length
      });

    } catch (error) {
      console.error('❌ API Error:', error);
      setError(`⚠️ API error: ${error.message} - Showing available data`);
    } finally {
      isLoadingRef.current = false;
      setLoading(false);
    }
  }, [selectedSport]);

  // Auto-refresh Effect
  useEffect(() => {
    fetchComprehensiveData();
  }, [selectedSport, fetchComprehensiveData]);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchComprehensiveData, 20000); // 20-second live updates
      return () => clearInterval(interval);
    }
  }, [autoRefresh, fetchComprehensiveData]);

  // Utility Functions
  const getConfidenceColor = (confidence) => {
    if (confidence >= 85) return '#00ff88'; // High confidence - green
    if (confidence >= 75) return '#00d4ff'; // Good confidence - blue  
    if (confidence >= 65) return '#ffaa00'; // Medium confidence - orange
    return '#ff4757'; // Low confidence - red
  };

  const getRiskColor = (risk) => {
    const riskLower = risk?.toLowerCase();
    switch (riskLower) {
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
    if (odds?.american) {
      return formatOdds(odds.american);
    }
    return 'N/A';
  };

  const convertOddsToDecimal = (odds) => {
    if (typeof odds !== 'number') return 1;
    if (odds > 0) {
      return 1 + (odds / 100);
    } else {
      return 1 + (100 / Math.abs(odds));
    }
  };

  const getSelectedSportInfo = () => {
    return globalSportsOptions.find(sport => sport.value === selectedSport) || {};
  };

  // Render Live Dashboard (New Feature)
  const renderLiveDashboard = () => (
    <div className="live-dashboard">
      <div className="dashboard-header">
        <h2>🔴 Live Global Sports Dashboard</h2>
        <div className="live-indicators">
          <div className="live-indicator">
            <span className="indicator-dot pulsing"></span>
            <span>Live Data Feed</span>
          </div>
          <div className="refresh-timer">
            <span>Next update: {autoRefresh ? '20s' : 'Manual'}</span>
          </div>
        </div>
      </div>

      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-number">{moneylines.length}</div>
          <div className="stat-label">Moneylines</div>
          <div className="stat-quality">
            {moneylines.filter(m => m.confidence >= 80).length} High Confidence
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{parlays.length}</div>
          <div className="stat-label">Parlays</div>
          <div className="stat-quality">
            {parlays.filter(p => p.total_confidence >= 75).length} Recommended
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{playerProps.length}</div>
          <div className="stat-label">Player Props</div>
          <div className="stat-quality">
            {playerProps.filter(p => p.confidence >= 75).length} Strong Plays
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-number">{liveParlays.length}</div>
          <div className="stat-label">Live Parlays</div>
          <div className="stat-quality">Ready to Execute</div>
        </div>
      </div>

      <div className="top-picks-section">
        <h3>🎯 Top High-Confidence Picks</h3>
        <div className="top-picks-grid">
          {[...moneylines, ...playerProps]
            .filter(pick => pick.confidence >= 85)
            .sort((a, b) => b.confidence - a.confidence)
            .slice(0, 6)
            .map((pick, index) => (
              <div key={index} className="top-pick-card">
                <div className="pick-type">
                  {pick.matchup ? 'Moneyline' : 'Player Prop'}
                </div>
                <div className="pick-details">
                  <strong>{pick.matchup || `${pick.player} - ${pick.prop_type}`}</strong>
                  <div className="pick-bet">{pick.bet || pick.prediction}</div>
                </div>
                <div className="pick-confidence">
                  <span style={{ color: getConfidenceColor(pick.confidence) }}>
                    {pick.confidence?.toFixed(1)}%
                  </span>
                </div>
                <div className="pick-odds">
                  {formatOdds(pick.odds?.american || pick.over_odds || pick.under_odds)}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );

  // Enhanced Live Parlays Section
  const renderLiveParlays = () => (
    <div className="live-parlays-section">
      <div className="section-header">
        <h2>🎲 Live Parlay Opportunities - {selectedSport}</h2>
        <div className="parlay-filters">
          <span className="high-confidence-count">
            {liveParlays.filter(p => p.total_confidence >= 80).length} High Confidence Available
          </span>
        </div>
      </div>

      <div className="live-parlays-grid">
        {liveParlays.length > 0 ? liveParlays.map((parlay, index) => (
          <div key={parlay.id || index} className="live-parlay-card">
            <div className="parlay-header">
              <div className="parlay-title">
                <span className="parlay-legs">{parlay.legs?.length}-Leg</span>
                <span className="parlay-sport">{selectedSport}</span>
              </div>
              <div className="parlay-payout">
                <div className="payout-odds">+{Math.round((parlay.combined_odds - 1) * 100)}</div>
                <div className="payout-amount">${parlay.expected_payout?.toFixed(2)}</div>
              </div>
            </div>

            <div className="parlay-confidence-bar">
              <div className="confidence-label">Total Confidence</div>
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

            <div className="parlay-legs">
              {parlay.legs?.map((leg, legIndex) => (
                <div key={legIndex} className="parlay-leg">
                  <div className="leg-info">
                    <div className="leg-matchup">{leg.matchup}</div>
                    <div className="leg-bet">{leg.bet}</div>
                  </div>
                  <div className="leg-metrics">
                    <span className="leg-odds">{formatOdds(leg.odds)}</span>
                    <span 
                      className="leg-confidence"
                      style={{ color: getConfidenceColor(leg.confidence) }}
                    >
                      {leg.confidence?.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="parlay-analytics">
              <div className="analytics-row">
                <span className="analytics-label">🔗 Correlation Risk:</span>
                <span className="analytics-value">{(parlay.correlation_risk * 100)?.toFixed(1)}%</span>
              </div>
              <div className="analytics-row">
                <span className="analytics-label">🧠 Game Theory Edge:</span>
                <span className="analytics-value">{parlay.game_theory_edge?.toFixed(1)}</span>
              </div>
              <div className="analytics-row">
                <span className="analytics-label">📊 Expected Value:</span>
                <span className="analytics-value">+{(parlay.expected_value * 100)?.toFixed(1)}%</span>
              </div>
            </div>

            <div className="execution-section">
              <div className="risk-indicator">
                <span className="risk-label">Risk Level:</span>
                <span 
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(parlay.risk_level) }}
                >
                  {parlay.risk_level?.toUpperCase()}
                </span>
              </div>
              
              {parlay.total_confidence >= 80 && (
                <div className="ready-to-execute">
                  <span className="execute-icon">🎯</span>
                  <span className="execute-text">READY TO EXECUTE</span>
                </div>
              )}
            </div>

            <div className="parlay-reasoning">
              <details>
                <summary>📋 Analysis & Reasoning</summary>
                <p>{parlay.reasoning}</p>
              </details>
            </div>

            <div className="manual-execution-notice">
              ⚠️ Manual execution required - Copy details to your betting platform
            </div>
          </div>
        )) : (
          <div className="no-live-parlays">
            <div className="no-data-icon">🎲</div>
            <div className="no-data-text">
              No high-confidence live parlays available for {selectedSport} right now.
            </div>
            <div className="no-data-subtitle">
              Live parlays update every 20 seconds based on real-time data.
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Enhanced Main Render
  return (
    <div className="enhanced-live-betting-platform">
      {/* Global Header */}
      <div className="platform-header">
        <div className="header-title">
          <h1>🎯 Live Global Sports Betting Platform</h1>
          <div className="platform-tagline">
            149 Global Sports • AI-Powered Predictions • Multi-Leg Parlay Builder (2-5 Legs)
          </div>
        </div>
        
        <div className="header-stats">
          <div className="stat-item live-indicator">
            <span className="stat-dot pulsing"></span>
            <span className="stat-label">Live Feed:</span>
            <span className="stat-value">{loading ? 'Updating...' : 'Active'}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Last Update:</span>
            <span className="stat-value">{lastUpdate || 'Loading...'} EST</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Global Sports:</span>
            <span className="stat-value">{sportsLoading ? '...' : globalSportsOptions.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Auto-Refresh:</span>
            <span className="stat-value">{autoRefresh ? '🟢 20s' : '🔴 OFF'}</span>
          </div>
        </div>
      </div>

      {/* Enhanced Controls */}
      <div className="platform-controls">
        <div className="sport-selection">
          <label className="control-label">Select Sport:</label>
          <select 
            value={selectedSport} 
            onChange={(e) => setSelectedSport(e.target.value)}
            className="sport-selector"
          >
            {globalSportsOptions.map(sport => (
              <option key={sport.value} value={sport.value}>
                {sport.label} ({sport.region})
              </option>
            ))}
          </select>
          <div className="selected-sport-info">
            <span className="sport-markets">
              Markets: {getSelectedSportInfo().markets?.join(', ') || 'Loading...'}
            </span>
          </div>
        </div>
        
        <div className="platform-settings">
          <label className="auto-refresh-toggle">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span className="toggle-slider"></span>
            Auto-Refresh (20s)
          </label>
          
          <button 
            onClick={fetchComprehensiveData} 
            className="refresh-button"
            disabled={loading}
          >
            {loading ? '🔄' : '↻'} Refresh All Data
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{error}</span>
          <button 
            onClick={() => setError(null)}
            className="error-dismiss"
          >
            ✕
          </button>
        </div>
      )}

      {/* Enhanced Navigation */}
      <div className="platform-navigation">
        <button 
          className={`nav-tab ${activeTab === 'live-dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('live-dashboard')}
        >
          <span className="tab-icon">📊</span>
          <span className="tab-label">Live Dashboard</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'moneylines' ? 'active' : ''}`}
          onClick={() => setActiveTab('moneylines')}
        >
          <span className="tab-icon">💰</span>
          <span className="tab-label">Moneylines</span>
          <span className="tab-count">({moneylines.length})</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'live-parlays' ? 'active' : ''}`}
          onClick={() => setActiveTab('live-parlays')}
        >
          <span className="tab-icon">🎲</span>
          <span className="tab-label">Live Parlays</span>
          <span className="tab-count">({liveParlays.length})</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'player-props' ? 'active' : ''}`}
          onClick={() => setActiveTab('player-props')}
        >
          <span className="tab-icon">👤</span>
          <span className="tab-label">Player Props</span>
          <span className="tab-count">({playerProps.length})</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'parlays' ? 'active' : ''}`}
          onClick={() => setActiveTab('parlays')}
        >
          <span className="tab-icon">🎯</span>
          <span className="tab-label">Intelligent Parlays</span>
          <span className="tab-count">({parlays.length})</span>
        </button>
        <button 
          className={`nav-tab ${activeTab === 'parlay-builder' ? 'active' : ''}`}
          onClick={() => setActiveTab('parlay-builder')}
        >
          <span className="tab-icon">🏗️</span>
          <span className="tab-label">Parlay Builder</span>
          <span className="tab-count">({parlayLegs} Legs)</span>
        </button>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <div className="loading-text">Loading live {activeTab} data...</div>
            <div className="loading-subtitle">Fetching real-time predictions from {selectedSport}</div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="platform-content">
        {activeTab === 'live-dashboard' && renderLiveDashboard()}
        {activeTab === 'live-parlays' && renderLiveParlays()}
        {activeTab === 'moneylines' && (
          <div className="moneylines-section">
            <h2>💰 Live Moneylines - {selectedSport}</h2>
            <div className="recommendations-grid">
              {moneylines.map((rec, index) => (
                <div key={rec.id || index} className="recommendation-card">
                  <div className="card-header">
                    <h3 className="matchup">{rec.matchup}</h3>
                    <div className="sport-badge">{selectedSport}</div>
                  </div>
                  
                  <div className="bet-info">
                    <div className="bet-type">{rec.bet}</div>
                    <div className="odds">{formatOdds(rec.odds?.american)}</div>
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
                      <span className="metric-value">+{rec.expected_value?.toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Game Theory</span>
                      <span className="metric-value">{rec.game_theory_score?.toFixed(1)}</span>
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

                  <details className="reasoning-details">
                    <summary>📋 Analysis</summary>
                    <p>{rec.reasoning}</p>
                  </details>

                  <div className="execution-notice">
                    ⚠️ Manual execution required - Copy to your betting platform
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {activeTab === 'player-props' && (
          <div className="player-props-section">
            <h2>👤 Player Props - {selectedSport}</h2>
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

                  <details className="reasoning-details">
                    <summary>📋 Analysis</summary>
                    <p>{prop.reasoning}</p>
                  </details>

                  <div className="execution-notice">
                    ⚠️ Manual execution required
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {activeTab === 'parlays' && (
          <div className="parlays-section">
            <h2>🎯 Intelligent Parlays - {selectedSport}</h2>
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

                  <div className="parlay-analytics">
                    <div className="analytics-metric">
                      <span>🔗 Correlation Risk: {(parlay.correlation_risk * 100)?.toFixed(1)}%</span>
                    </div>
                    <div className="analytics-metric">
                      <span>🧠 Game Theory Edge: {parlay.game_theory_edge?.toFixed(1)}</span>  
                    </div>
                  </div>

                  <details className="reasoning-details">
                    <summary>📋 Parlay Analysis</summary>
                    <p>{parlay.reasoning}</p>
                  </details>

                  <div className="execution-notice">
                    ⚠️ Manual execution required
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* NEW: Multi-Leg Parlay Builder */}
        {activeTab === 'parlay-builder' && (
          <div className="parlay-builder-section">
            <div className="section-header">
              <h2>🏗️ Custom Parlay Builder - {selectedSport}</h2>
              <div className="builder-controls">
                <label>Select Number of Legs:</label>
                <div className="leg-selector">
                  {[2, 3, 4, 5].map(legs => (
                    <button
                      key={legs}
                      className={`leg-option ${parlayLegs === legs ? 'active' : ''}`}
                      onClick={() => {
                        setParlayLegs(legs);
                        // Initialize parlay builder with empty legs
                        setParlayBuilder(Array(legs).fill(null));
                      }}
                    >
                      {legs} Legs
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="builder-grid">
              {parlayBuilder.map((leg, index) => (
                <div key={index} className="builder-leg-slot">
                  <div className="leg-slot-header">
                    <span className="leg-number">Leg {index + 1}</span>
                    {leg && (
                      <button 
                        className="remove-leg"
                        onClick={() => {
                          const newBuilder = [...parlayBuilder];
                          newBuilder[index] = null;
                          setParlayBuilder(newBuilder);
                        }}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                  
                  {leg ? (
                    <div className="selected-leg">
                      <div className="leg-matchup">{leg.matchup}</div>
                      <div className="leg-bet">{leg.bet}</div>
                      <div className="leg-odds">{formatOdds(leg.odds)}</div>
                    </div>
                  ) : (
                    <div className="empty-leg-slot">
                      <div className="slot-icon">➕</div>
                      <div className="slot-text">Select a bet from available games</div>
                      <select 
                        className="game-selector"
                        onChange={(e) => {
                          if (e.target.value) {
                            // Parse the selected game and add it to the parlay
                            const gameData = JSON.parse(e.target.value);
                            const newBuilder = [...parlayBuilder];
                            newBuilder[index] = gameData;
                            setParlayBuilder(newBuilder);
                          }
                        }}
                      >
                        <option value="">Choose a game...</option>
                        {moneylines.slice(0, 10).map((game, gameIdx) => (
                          <React.Fragment key={gameIdx}>
                            <option value={JSON.stringify({
                              matchup: `${game.home_team} vs ${game.away_team}`,
                              bet: `${game.home_team} ML`,
                              odds: game.home_odds
                            })}>
                              {game.home_team} ML ({formatOdds(game.home_odds)})
                            </option>
                            <option value={JSON.stringify({
                              matchup: `${game.home_team} vs ${game.away_team}`,
                              bet: `${game.away_team} ML`,
                              odds: game.away_odds
                            })}>
                              {game.away_team} ML ({formatOdds(game.away_odds)})
                            </option>
                          </React.Fragment>
                        ))}
                      </select>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Parlay Summary */}
            {parlayBuilder.filter(leg => leg !== null).length >= 2 && (
              <div className="parlay-summary">
                <div className="summary-header">
                  <h3>📊 Parlay Summary</h3>
                </div>
                <div className="summary-stats">
                  <div className="stat-item">
                    <span className="stat-label">Total Legs:</span>
                    <span className="stat-value">{parlayBuilder.filter(leg => leg !== null).length}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Combined Odds:</span>
                    <span className="stat-value">
                      {formatOdds(
                        parlayBuilder
                          .filter(leg => leg !== null)
                          .reduce((total, leg) => total * convertOddsToDecimal(leg.odds), 1)
                      )}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">$100 Bet Pays:</span>
                    <span className="stat-value payout">
                      ${(
                        100 * 
                        parlayBuilder
                          .filter(leg => leg !== null)
                          .reduce((total, leg) => total * convertOddsToDecimal(leg.odds), 1)
                      ).toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="summary-actions">
                  <button 
                    className="btn-place-parlay"
                    onClick={() => {
                      alert('Parlay saved! Visit your sportsbook to place this bet manually.');
                      // Reset builder
                      setParlayBuilder(Array(parlayLegs).fill(null));
                    }}
                  >
                    💰 Save Parlay (Manual Placement Required)
                  </button>
                  <button 
                    className="btn-clear-parlay"
                    onClick={() => setParlayBuilder(Array(parlayLegs).fill(null))}
                  >
                    🗑️ Clear All
                  </button>
                </div>
              </div>
            )}

            {parlayBuilder.filter(leg => leg !== null).length < 2 && (
              <div className="builder-hint">
                <span className="hint-icon">💡</span>
                <span className="hint-text">
                  Select at least 2 legs to build a parlay. Higher legs = higher payout but lower chance of winning!
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Enhanced Footer */}
      <div className="platform-footer">
        <div className="footer-stats">
          <span>🌍 149 Global Sports Coverage</span>
          <span>🧠 AI Game Theory Algorithms</span>
          <span>🎯 Multi-Leg Parlay Builder (2-5 Legs)</span>
          <span>📊 Real-time Live Odds via The Odds API</span>
        </div>
        <div className="footer-disclaimer">
          <span>⚖️ Manual betting required for legal compliance</span>
          <span>🔴 Live predictions for production betting</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedLiveBettingPlatform;