import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import './OptimizedPlatform.css';

// Memoized components for performance
const MoneylineCard = memo(({ bet, dateType }) => {
  const formatOdds = (odds) => {
    if (!odds) return 'N/A';
    return odds > 0 ? `+${odds}` : odds;
  };

  return (
    <div className="bet-card moneyline-card">
      <div className="bet-header">
        <span className="bet-icon">💰</span>
        <h4>{bet.matchup}</h4>
        <span className={`date-badge ${dateType}`}>
          {dateType === 'today' ? '🔴 TODAY' : '📅 TOMORROW'}
        </span>
      </div>
      <div className="bet-details">
        <div className="recommended-bet">
          <span className="bet-label">RECOMMENDED BET:</span>
          <span className="bet-pick">{bet.bet}</span>
          <span className="odds">{formatOdds(bet.odds?.recommended_odds || bet.odds?.american)}</span>
        </div>
      </div>
      <div className="bet-meta">
        <span className="confidence">
          <span className="confidence-bar" style={{width: `${bet.confidence}%`}}></span>
          {bet.confidence}% Confidence
          {bet.ai_calibrated && <span className="ai-badge">🎯 AI Calibrated</span>}
        </span>
        <span className="game-time">🕐 {new Date(bet.start_time).toLocaleTimeString()}</span>
        <span className="ev-stat">EV: +{bet.expected_value?.toFixed(1)}%</span>
      </div>
      <div className="bet-stats">
        <span className="stat">Risk: {bet.risk}</span>
        <span className="stat">Kelly: {bet.kelly_pct?.toFixed(1)}%</span>
        <span className="stat">GT Score: {bet.game_theory_score?.toFixed(2)}</span>
      </div>
      {bet.reasoning && (
        <div className="ai-reasoning">
          <strong>💡 AI Analysis:</strong> {bet.reasoning.substring(0, 200)}...
        </div>
      )}
    </div>
  );
});

const ParlayCard = memo(({ parlay, dateType }) => {
  const formatOdds = (odds) => {
    if (!odds) return 'N/A';
    return odds > 0 ? `+${odds}` : odds;
  };

  return (
    <div className="bet-card parlay-card">
      <div className="bet-header">
        <span className="bet-icon">🎯</span>
        <h4>{parlay.num_legs || parlay.legs?.length || 0}-Leg Parlay</h4>
        <span className={`date-badge ${dateType}`}>
          {dateType === 'today' ? '🔴 TODAY' : '📅 TOMORROW'}
        </span>
      </div>
      <div className="parlay-legs">
        {parlay.legs?.map((leg, idx) => (
          <div key={idx} className="parlay-leg">
            <span className="leg-number">#{idx + 1}</span>
            <div className="leg-details">
              <span className="leg-matchup">{leg.matchup}</span>
              <span className="leg-pick">{leg.bet}</span>
              <span className="leg-odds">{formatOdds(leg.odds)}</span>
              <span className="leg-confidence">{leg.confidence}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="bet-meta">
        <span className="confidence">
          <span className="confidence-bar" style={{width: `${parlay.total_confidence || parlay.avg_confidence}%`}}></span>
          {parlay.total_confidence || parlay.avg_confidence}% Combined
          {parlay.ai_optimized && <span className="ai-badge">🎯 AI Optimized</span>}
        </span>
        <span className="payout">💵 Payout: {(parlay.combined_odds || parlay.expected_payout || 0).toFixed(2)}x</span>
        <span className="risk">Risk: {parlay.risk_level || 'Medium'}</span>
      </div>
      {parlay.reasoning && (
        <div className="parlay-reasoning">
          <strong>💡 Strategy:</strong> {parlay.reasoning.substring(0, 180)}...
        </div>
      )}
    </div>
  );
});

const OptimizedLiveBettingPlatform = () => {
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [selectedDate, setSelectedDate] = useState('today');
  const [moneylines, setMoneylines] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isRealTime, setIsRealTime] = useState(true);
  const [currentDateTime, setCurrentDateTime] = useState(new Date());
  const [cache, setCache] = useState({});

  // Use relative URLs - nginx will proxy to backend API
  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  // Memoized sports options - Expanded coverage
  const sportsOptions = useMemo(() => [
    // US Sports
    { value: 'NBA', label: '🏀 NBA Basketball' },
    { value: 'NFL', label: '🏈 NFL Football' },
    { value: 'NHL', label: '🏒 NHL Hockey' },
    { value: 'MLB', label: '⚾ MLB Baseball' },
    { value: 'NCAAB', label: '🏀 NCAA Basketball' },
    { value: 'NCAAF', label: '🏈 NCAA Football' },
    // Global Soccer
    { value: 'EPL', label: '⚽ Premier League' },
    { value: 'LALIGA', label: '⚽ La Liga' },
    { value: 'BUNDESLIGA', label: '⚽ Bundesliga' },
    { value: 'SERIEA', label: '⚽ Serie A' },
    { value: 'LIGUE1', label: '⚽ Ligue 1' },
    { value: 'UCL', label: '⚽ Champions League' },
    { value: 'MLS', label: '⚽ MLS Soccer' },
    // Combat Sports
    { value: 'MMA', label: '🥊 MMA/UFC' },
    { value: 'UFC', label: '🥊 UFC' },
    { value: 'BOXING', label: '🥊 Boxing' },
    // Tennis
    { value: 'ATP', label: '🎾 ATP Tennis' },
    { value: 'WTA', label: '🎾 WTA Tennis' },
    // Other Sports
    { value: 'GOLF', label: '⛳ PGA Golf' },
    { value: 'NASCAR', label: '🏎️ NASCAR' },
    { value: 'F1', label: '🏎️ Formula 1' },
    { value: 'ESPORTS', label: '🎮 Esports' }
  ], []);

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentDateTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // No client-side filtering needed - API already filters by date
  // Just pass through the moneylines from the API
  const filteredMoneylines = useMemo(() => {
    return moneylines;
  }, [moneylines]);

  const filteredParlays = useMemo(() => {
    // Parlays are already filtered by API based on date parameter
    return parlays;
  }, [parlays]);

  // Optimized fetch with caching
  const fetchData = useCallback(async () => {
    if (loading) return;
    
    const cacheKey = `${selectedSport}-${selectedDate}`;
    const cachedData = cache[cacheKey];
    
    // Use cache if less than 30 seconds old
    if (cachedData && (Date.now() - cachedData.timestamp < 30000)) {
      console.log('📦 Using cached data for', cacheKey);
      setMoneylines(cachedData.moneylines);
      setParlays(cachedData.parlays);
      setLastUpdate(new Date(cachedData.timestamp).toLocaleTimeString());
      return;
    }

    console.log('🚀 Fetching fresh data for', selectedSport, selectedDate);
    setLoading(true);
    setError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);

      const [moneylineRes, parlayRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/recommendations/${selectedSport}?date=${selectedDate}`, { signal: controller.signal }),
        fetch(`${API_BASE_URL}/api/parlays/${selectedSport}?date=${selectedDate}`, { signal: controller.signal })
      ]);

      clearTimeout(timeoutId);

      if (!moneylineRes.ok || !parlayRes.ok) {
        throw new Error(`API Error: ${moneylineRes.status}/${parlayRes.status}`);
      }

      const moneylineData = await moneylineRes.json();
      const parlayData = await parlayRes.json();

      const newData = {
        moneylines: moneylineData.recommendations || [],
        parlays: parlayData.parlays || [],
        timestamp: Date.now()
      };

      setMoneylines(newData.moneylines);
      setParlays(newData.parlays);
      setLastUpdate(new Date().toLocaleTimeString());
      
      // Update cache
      setCache(prev => ({ ...prev, [cacheKey]: newData }));

    } catch (err) {
      console.error('❌ Fetch error:', err.message);
      setError(err.name === 'AbortError' ? 'Request timed out' : `Connection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedSport, selectedDate, API_BASE_URL, cache, loading]);

  // Auto-refresh every 60 seconds when real-time is enabled
  useEffect(() => {
    if (isRealTime) {
      const interval = setInterval(fetchData, 60000);
      return () => clearInterval(interval);
    }
  }, [fetchData, isRealTime]);

  useEffect(() => {
    fetchData();
  }, [selectedSport, selectedDate]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="optimized-betting-platform">
      <div className="header">
        <div className="header-content">
          <h1>🎯 AI-Enhanced Betting Platform</h1>
          <div className="live-indicator">
            <span className="pulse-dot"></span>
            <span>LIVE {currentDateTime.toLocaleTimeString()}</span>
          </div>
        </div>
        
        <div className="controls">
          <div className="sport-selector">
            <label>Sport:</label>
            <select value={selectedSport} onChange={(e) => setSelectedSport(e.target.value)}>
              {sportsOptions.map(sport => (
                <option key={sport.value} value={sport.value}>{sport.label}</option>
              ))}
            </select>
          </div>
          
          <div className="date-selector">
            <label>Date:</label>
            <div className="date-tabs">
              <button 
                className={selectedDate === 'today' ? 'active' : ''}
                onClick={() => setSelectedDate('today')}
              >
                🔴 Today
              </button>
              <button 
                className={selectedDate === 'tomorrow' ? 'active' : ''}
                onClick={() => setSelectedDate('tomorrow')}
              >
                📅 Tomorrow
              </button>
            </div>
          </div>
          
          <button 
            className={`refresh-btn ${isRealTime ? 'active' : ''}`}
            onClick={() => setIsRealTime(!isRealTime)}
          >
            {isRealTime ? '🔄 Live' : '⏸️ Paused'}
          </button>
        </div>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}
      
      {loading && <div className="loading-spinner">🔄 Loading betting intelligence...</div>}

      <div className="betting-content">
        <section className="moneylines-section">
          <h2>💰 Moneyline Bets ({filteredMoneylines.length})</h2>
          {lastUpdate && <p className="update-time">Last updated: {lastUpdate}</p>}
          <div className="bets-grid">
            {filteredMoneylines.map((bet, idx) => (
              <MoneylineCard key={`${bet.id}-${idx}`} bet={bet} dateType={selectedDate} />
            ))}
          </div>
        </section>

        <section className="parlays-section">
          <h2>🎯 Parlay Combinations ({filteredParlays.length})</h2>
          <div className="bets-grid">
            {filteredParlays.map((parlay, idx) => (
              <ParlayCard key={`parlay-${idx}`} parlay={parlay} dateType={selectedDate} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default OptimizedLiveBettingPlatform;
