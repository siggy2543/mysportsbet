import React, { useState, useEffect, useCallback } from 'react';
import './SimplifiedPlatform.css';

// Sport emoji mapping for better UI (outside component)
const sportEmojiMap = {
  'basketball': '🏀', 'americanfootball': '🏈', 'icehockey': '🏒', 'baseball': '⚾',
  'soccer': '⚽', 'tennis': '🎾', 'cricket': '🏏', 'rugby': '🏉', 'formula1': '🏎️',
  'mma': '🥊', 'boxing': '🥊', 'golf': '⛳', 'cycling': '🚴', 'darts': '🎯',
  'aussierules': '🏉', 'volleyball': '🏐', 'handball': '🤾', 'waterpolo': '🤽',
  'tableTennis': '🏓', 'esports': '🎮', 'snooker': '🎱', 'bowls': '🎳'
};

const SimplifiedLiveBettingPlatform = () => {
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [moneylines, setMoneylines] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRealTime, setIsRealTime] = useState(true);
  const [currentDateTime, setCurrentDateTime] = useState(new Date());
  
  // Dynamic sports loaded from The Odds API (all 149 sports)
  const [globalSportsOptions, setGlobalSportsOptions] = useState([]);
  const [sportsLoading, setSportsLoading] = useState(true);

  const API_BASE_URL = 'http://localhost:8000';

  // Update current time every second for real-time display
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Load all 149 sports from The Odds API on mount
  useEffect(() => {
    const fetchSports = async () => {
      try {
        setSportsLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/odds/sports`);
        const data = await response.json();
        
        if (data.sports) {
          const formattedSports = data.sports.map(sport => {
            const sportKey = sport.group.toLowerCase().replace(/_/g, '');
            const emoji = sportEmojiMap[sportKey] || sportEmojiMap[sport.key.toLowerCase()] || '🏆';
            
            return {
              value: sport.key,
              label: `${emoji} ${sport.title}`,
              region: sport.group,
              active: sport.active,
              category: sport.group
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
        // Fallback to default NBA
        setGlobalSportsOptions([
          { value: 'NBA', label: '🏀 NBA Basketball', region: 'Basketball', active: true, category: 'Basketball' }
        ]);
      } finally {
        setSportsLoading(false);
      }
    };
    
    fetchSports();
  }, [API_BASE_URL]);

  const fetchData = useCallback(async () => {
    if (loading) return;
    
    console.log('🚀 Starting fetch for', selectedSport, 'at', new Date().toLocaleTimeString());
    setLoading(true);
    setError(null);

    try {
      // Add timeout for stability
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      // Fetch recommendations and parlays
      const [moneylineRes, parlayRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/recommendations/${selectedSport}`, { signal: controller.signal }),
        fetch(`${API_BASE_URL}/api/parlays/${selectedSport}`, { signal: controller.signal })
      ]);

      clearTimeout(timeoutId);
      console.log('📡 API responses:', moneylineRes.status, parlayRes.status);

      if (!moneylineRes.ok || !parlayRes.ok) {
        throw new Error(`API Error: ${moneylineRes.status}/${parlayRes.status}`);
      }

      const moneylineData = await moneylineRes.json();
      const parlayData = await parlayRes.json();

      console.log('✅ Data received:', moneylineData.recommendations?.length, 'recommendations,', parlayData.parlays?.length, 'parlays');

      setMoneylines(moneylineData.recommendations || []);
      setParlays(parlayData.parlays || []);
      setLastUpdate(new Date().toLocaleTimeString());

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('⏰ Request timed out');
        setError('Request timed out. Please try again.');
      } else {
        console.error('❌ Fetch error:', err.message);
        setError(`Connection error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [selectedSport, API_BASE_URL]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-refresh data every 60 seconds when real-time is enabled (more stable)
  useEffect(() => {
    if (isRealTime) {
      const autoRefresh = setInterval(() => {
        console.log('🔄 Auto-refreshing data...');
        fetchData();
      }, 60000); // 60 seconds for stability
      return () => clearInterval(autoRefresh);
    }
  }, [fetchData, isRealTime]);

  useEffect(() => {
    console.log('🏃 useEffect triggered for sport:', selectedSport);
    fetchData();
  }, [selectedSport, fetchData]);

  return (
    <div className="enhanced-live-betting-platform">
      <div className="header">
        <div className="header-left">
          <h1>Enhanced Live Betting Platform - 149 Global Sports</h1>
          <div className="live-indicators">
            <span className="live-dot"></span>
            <span className="live-text">LIVE {currentDateTime.toLocaleTimeString()}</span>
            <button 
              className={`real-time-toggle ${isRealTime ? 'active' : ''}`}
              onClick={() => setIsRealTime(!isRealTime)}
              title={isRealTime ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
            >
              {isRealTime ? '🔄 LIVE' : '⏸️ PAUSED'}
            </button>
          </div>
        </div>
        <div className="sports-selector">
          <label>Select Sport ({sportsLoading ? '...' : globalSportsOptions.length} available): </label>
          <select 
            value={selectedSport}
            disabled={sportsLoading} 
            onChange={(e) => setSelectedSport(e.target.value)}
          >
            {/* Group sports by category */}
            <optgroup label="🇺🇸 US Sports">
              {globalSportsOptions.filter(s => s.category === 'US Sports').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="⚽ Global Soccer">
              {globalSportsOptions.filter(s => s.category === 'Global Soccer').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🎾 Tennis">
              {globalSportsOptions.filter(s => s.category === 'Tennis').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🌍 International">
              {globalSportsOptions.filter(s => s.category === 'International').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🥊 Combat Sports">
              {globalSportsOptions.filter(s => s.category === 'Combat Sports').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🏌️ Individual Sports">
              {globalSportsOptions.filter(s => s.category === 'Individual Sports').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🏎️ Motorsports">
              {globalSportsOptions.filter(s => s.category === 'Motorsports').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
            <optgroup label="🎮 E-Sports">
              {globalSportsOptions.filter(s => s.category === 'E-Sports').map(sport => (
                <option key={sport.value} value={sport.value}>
                  {sport.label}
                </option>
              ))}
            </optgroup>
          </select>
        </div>
      </div>

      {loading && (
        <div className="loading-indicator">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <div className="loading-text">
              Loading {globalSportsOptions.find(s => s.value === selectedSport)?.label || selectedSport} data...
            </div>
            <div className="loading-subtext">Fetching live market intelligence</div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          ❌ Error: {error}
        </div>
      )}

      <div className="content">
        <div className="section">
          <h2>💰 Live Moneyline Recommendations ({moneylines.length})</h2>
          {moneylines.slice(0, 8).map((rec, index) => (
            <div key={index} className="recommendation-card">
              <div className="card-header">
                <div className="matchup">{rec.matchup}</div>
                <div className="live-badge">🔴 LIVE</div>
              </div>
              <div className="bet">{rec.bet}</div>
              <div className="metrics-grid">
                <div className="metric">
                  <span className="confidence">Confidence: {rec.confidence}%</span>
                </div>
                <div className="metric">
                  <span className="odds">Odds: {rec.odds?.american}</span>
                </div>
                <div className="metric">
                  <span className="expected-value">EV: +{rec.expected_value}%</span>
                </div>
                <div className="metric">
                  <span className="kelly">Kelly: {rec.kelly_pct}%</span>
                </div>
              </div>
              <div className="reasoning">{rec.reasoning}</div>
              <div className="risk-level">
                <span className={`risk-badge ${rec.risk?.toLowerCase()}`}>
                  {rec.risk} Risk
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="section">
          <h2>🎲 Live Game Theory Parlays ({parlays.length})</h2>
          {parlays.slice(0, 5).map((parlay, index) => (
            <div key={index} className="parlay-card">
              <div className="parlay-header">
                <div className="parlay-title">
                  {parlay.num_legs}-Leg Parlay
                  <span className="execution-badge">
                    {parlay.execution_ready ? '✅ READY' : '⚠️ REVIEW'}
                  </span>
                </div>
                <div className="live-badge">🔴 LIVE</div>
              </div>
              <div className="parlay-metrics">
                <div className="metric">
                  <span className="label">Total Confidence:</span>
                  <span className="value">{parlay.total_confidence?.toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span className="label">Expected Value:</span>
                  <span className="value expected-value">${parlay.expected_value?.toFixed(2)}</span>
                </div>
                <div className="metric">
                  <span className="label">Correlation Risk:</span>
                  <span className="value">{(parlay.correlation_risk * 100)?.toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span className="label">Game Theory Edge:</span>
                  <span className="value kelly">{parlay.game_theory_edge?.toFixed(2)}</span>
                </div>
              </div>
              <div className="parlay-legs">
                {parlay.legs?.map((leg, legIndex) => (
                  <div key={legIndex} className="leg">
                    <div className="leg-matchup">{leg.matchup}</div>
                    <div className="leg-bet">{leg.bet}</div>
                    <div className="leg-details">
                      <span className="leg-odds">{leg.odds}</span>
                      <span className="leg-confidence">{leg.confidence}%</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="parlay-payout">
                <span className="payout-label">Expected Payout (100 bet):</span>
                <span className="payout-value">${parlay.expected_payout?.toFixed(2)}</span>
              </div>
              <div className="parlay-reasoning">{parlay.reasoning}</div>
              <div className="risk-level">
                <span className={`risk-badge ${parlay.risk_level?.toLowerCase()}`}>
                  {parlay.risk_level} Risk
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {lastUpdate && (
        <div className="last-update">
          <div className="update-info">
            <span className="update-text">Last data refresh: {lastUpdate}</span>
            <span className="next-update">
              {isRealTime ? 'Auto-refresh every 60s' : 'Auto-refresh paused'}
            </span>
          </div>
          <button className="manual-refresh" onClick={fetchData} disabled={loading}>
            {loading ? '🔄 Refreshing...' : '🔄 Refresh Now'}
          </button>
        </div>
      )}
    </div>
  );
};

export default SimplifiedLiveBettingPlatform;