import React, { useState, useEffect, useCallback, useMemo, memo } from 'react';
import './OptimizedPlatform.css';
import './EnhancedFeatures.css';

// Enhanced Moneyline Card with Add to Slip button
const MoneylineCard = memo(({ bet, dateType, onAddToSlip, inSlip }) => {
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
      <button 
        className={`add-to-slip-btn ${inSlip ? 'in-slip' : ''}`}
        onClick={() => onAddToSlip(bet)}
        disabled={inSlip}
      >
        {inSlip ? '✓ In Slip' : '+ Add to Slip'}
      </button>
    </div>
  );
});

// Parlay Card
const ParlayCard = memo(({ parlay, dateType, onAddToSlip, inSlip }) => {
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
      <button 
        className={`add-to-slip-btn ${inSlip ? 'in-slip' : ''}`}
        onClick={() => onAddToSlip(parlay)}
        disabled={inSlip}
      >
        {inSlip ? '✓ In Slip' : '+ Add Parlay to Slip'}
      </button>
    </div>
  );
});

// Bet Slip Component
const BetSlip = memo(({ bets, onRemove, onClear, bankroll, onUpdateBankroll }) => {
  const [betAmounts, setBetAmounts] = useState({});
  
  const totalPotentialPayout = useMemo(() => {
    return bets.reduce((sum, bet) => {
      const amount = betAmounts[bet.id] || 0;
      const odds = bet.odds?.recommended_odds || bet.combined_odds || 100;
      const decimal = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
      return sum + (amount * decimal);
    }, 0);
  }, [bets, betAmounts]);

  const totalRisk = useMemo(() => {
    return Object.values(betAmounts).reduce((sum, amount) => sum + amount, 0);
  }, [betAmounts]);

  const updateBetAmount = (betId, amount) => {
    setBetAmounts(prev => ({ ...prev, [betId]: parseFloat(amount) || 0 }));
  };

  const autoSizeBets = () => {
    const newAmounts = {};
    bets.forEach(bet => {
      const kelly = (bet.kelly_pct || 0) / 100;
      const suggested = bankroll * kelly * 0.25; // Quarter Kelly for safety
      newAmounts[bet.id] = Math.max(10, Math.min(suggested, bankroll * 0.05));
    });
    setBetAmounts(newAmounts);
  };

  return (
    <div className="bet-slip">
      <div className="slip-header">
        <h3>🎫 Bet Slip ({bets.length})</h3>
        <button className="clear-slip-btn" onClick={onClear} disabled={bets.length === 0}>
          Clear All
        </button>
      </div>
      
      <div className="bankroll-section">
        <label>💰 Bankroll:</label>
        <input 
          type="number" 
          value={bankroll} 
          onChange={(e) => onUpdateBankroll(parseFloat(e.target.value) || 0)}
          min="0"
          step="100"
          placeholder="Enter bankroll"
        />
        <button className="auto-size-btn" onClick={autoSizeBets} disabled={bets.length === 0}>
          Auto-Size Bets (Kelly)
        </button>
      </div>

      <div className="slip-bets">
        {bets.length === 0 ? (
          <div className="empty-slip">
            <p>No bets selected</p>
            <small>Click "+ Add to Slip" on any bet</small>
          </div>
        ) : (
          bets.map(bet => (
            <div key={bet.id} className="slip-bet-item">
              <div className="slip-bet-header">
                <span className="slip-bet-title">
                  {bet.matchup || `${bet.num_legs}-Leg Parlay`}
                </span>
                <button className="remove-bet-btn" onClick={() => onRemove(bet.id)}>×</button>
              </div>
              <div className="slip-bet-details">
                <span className="slip-bet-pick">{bet.bet || `${bet.legs?.length} legs`}</span>
                <span className="slip-bet-odds">
                  {bet.odds?.recommended_odds > 0 ? '+' : ''}{bet.odds?.recommended_odds || bet.combined_odds?.toFixed(0)}
                </span>
              </div>
              <div className="slip-bet-amount">
                <label>Bet Amount: $</label>
                <input 
                  type="number" 
                  value={betAmounts[bet.id] || ''}
                  onChange={(e) => updateBetAmount(bet.id, e.target.value)}
                  min="0"
                  step="10"
                  placeholder="0"
                />
                <small className="kelly-suggestion">
                  Suggested: ${(bankroll * ((bet.kelly_pct || 0) / 100) * 0.25).toFixed(2)}
                </small>
              </div>
            </div>
          ))
        )}
      </div>

      {bets.length > 0 && (
        <div className="slip-summary">
          <div className="summary-row">
            <span>Total Risk:</span>
            <span className="risk-amount">${totalRisk.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Potential Payout:</span>
            <span className="payout-amount">${totalPotentialPayout.toFixed(2)}</span>
          </div>
          <div className="summary-row profit-row">
            <span>Potential Profit:</span>
            <span className="profit-amount">+${(totalPotentialPayout - totalRisk).toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>% of Bankroll:</span>
            <span className={totalRisk > bankroll * 0.1 ? 'warning' : ''}>
              {bankroll > 0 ? ((totalRisk / bankroll) * 100).toFixed(1) : 0}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
});

// Advanced Filters Component
const AdvancedFilters = memo(({ filters, onChange }) => {
  return (
    <div className="advanced-filters">
      <div className="filter-section">
        <label>Min Confidence:</label>
        <select value={filters.minConfidence} onChange={(e) => onChange('minConfidence', e.target.value)}>
          <option value="0">All</option>
          <option value="70">70%+</option>
          <option value="75">75%+</option>
          <option value="80">80%+</option>
          <option value="85">85%+</option>
        </select>
      </div>

      <div className="filter-section">
        <label>Min Expected Value:</label>
        <select value={filters.minEV} onChange={(e) => onChange('minEV', e.target.value)}>
          <option value="0">All</option>
          <option value="100">100%+</option>
          <option value="200">200%+</option>
          <option value="300">300%+</option>
          <option value="500">500%+</option>
        </select>
      </div>

      <div className="filter-section">
        <label>Risk Level:</label>
        <select value={filters.riskLevel} onChange={(e) => onChange('riskLevel', e.target.value)}>
          <option value="all">All</option>
          <option value="Low">Low Risk Only</option>
          <option value="Medium">Medium Risk</option>
          <option value="High">High Risk</option>
        </select>
      </div>

      <div className="filter-section">
        <label>Odds Range:</label>
        <select value={filters.oddsRange} onChange={(e) => onChange('oddsRange', e.target.value)}>
          <option value="all">All Odds</option>
          <option value="favorites">Favorites (-200 or better)</option>
          <option value="underdogs">Underdogs (+150 or better)</option>
          <option value="pickems">Pick'ems (-150 to +150)</option>
        </select>
      </div>

      <div className="filter-section">
        <label>Sort By:</label>
        <select value={filters.sortBy} onChange={(e) => onChange('sortBy', e.target.value)}>
          <option value="confidence">Highest Confidence</option>
          <option value="ev">Best Expected Value</option>
          <option value="kelly">Highest Kelly %</option>
          <option value="time">Game Time</option>
        </select>
      </div>
    </div>
  );
});

const EnhancedBettingPlatform = () => {
  const [selectedSport, setSelectedSport] = useState('NBA');
  const [selectedDate, setSelectedDate] = useState('today');
  const [moneylines, setMoneylines] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState('');
  const [cache, setCache] = useState({});
  const [realTimeEnabled, setRealTimeEnabled] = useState(false);
  
  // New state for enhancements
  const [betSlip, setBetSlip] = useState([]);
  const [bankroll, setBankroll] = useState(1000);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    minConfidence: '0',
    minEV: '0',
    riskLevel: 'all',
    oddsRange: 'all',
    sortBy: 'confidence'
  });

  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  // Sports options (same as before)
  const sportsOptions = useMemo(() => [
    { value: 'NBA', label: '🏀 NBA Basketball', region: 'US' },
    { value: 'NFL', label: '🏈 NFL Football', region: 'US' },
    { value: 'NHL', label: '🏒 NHL Hockey', region: 'US' },
    { value: 'MLB', label: '⚾ MLB Baseball', region: 'US' },
    { value: 'NCAAB', label: '🏀 NCAA Basketball', region: 'US' },
    { value: 'NCAAF', label: '🏈 NCAA Football', region: 'US' },
    { value: 'EPL', label: '⚽ English Premier League', region: 'UK' },
    { value: 'LALIGA', label: '⚽ La Liga', region: 'ES' },
    { value: 'BUNDESLIGA', label: '⚽ Bundesliga', region: 'DE' },
    { value: 'SERIEA', label: '⚽ Serie A', region: 'IT' },
    { value: 'LIGUE1', label: '⚽ Ligue 1', region: 'FR' },
    { value: 'UCL', label: '⚽ Champions League', region: 'EU' },
    { value: 'MLS', label: '⚽ MLS', region: 'US' },
    { value: 'MMA', label: '🥊 MMA', region: 'Global' },
    { value: 'UFC', label: '🥊 UFC', region: 'Global' },
    { value: 'BOXING', label: '🥊 Boxing', region: 'Global' },
    { value: 'ATP', label: '🎾 ATP Tennis', region: 'Global' },
    { value: 'WTA', label: '🎾 WTA Tennis', region: 'Global' },
    { value: 'GOLF', label: '⛳ Golf', region: 'Global' },
    { value: 'NASCAR', label: '🏎️ NASCAR', region: 'US' },
    { value: 'F1', label: '🏎️ Formula 1', region: 'Global' },
    { value: 'ESPORTS', label: '🎮 E-Sports', region: 'Global' }
  ], []);

  // No client-side filtering needed - API already filters by date
  const filteredMoneylines = useMemo(() => {
    let filtered = moneylines;

    // Apply confidence filter
    if (filters.minConfidence !== '0') {
      filtered = filtered.filter(bet => bet.confidence >= parseFloat(filters.minConfidence));
    }

    // Apply EV filter
    if (filters.minEV !== '0') {
      filtered = filtered.filter(bet => bet.expected_value >= parseFloat(filters.minEV));
    }

    // Apply risk filter
    if (filters.riskLevel !== 'all') {
      filtered = filtered.filter(bet => bet.risk === filters.riskLevel);
    }

    // Apply odds range filter
    if (filters.oddsRange !== 'all') {
      filtered = filtered.filter(bet => {
        const odds = bet.odds?.recommended_odds || 0;
        switch(filters.oddsRange) {
          case 'favorites': return odds < -100 && odds >= -200;
          case 'underdogs': return odds >= 150;
          case 'pickems': return odds >= -150 && odds <= 150;
          default: return true;
        }
      });
    }

    // Apply sorting
    switch(filters.sortBy) {
      case 'confidence':
        filtered = [...filtered].sort((a, b) => b.confidence - a.confidence);
        break;
      case 'ev':
        filtered = [...filtered].sort((a, b) => b.expected_value - a.expected_value);
        break;
      case 'kelly':
        filtered = [...filtered].sort((a, b) => (b.kelly_pct || 0) - (a.kelly_pct || 0));
        break;
      case 'time':
        filtered = [...filtered].sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
        break;
      default:
        break;
    }

    return filtered;
  }, [moneylines, filters]);

  const filteredParlays = useMemo(() => {
    return parlays;
  }, [parlays]);

  // Bet Slip functions
  const addToBetSlip = useCallback((bet) => {
    setBetSlip(prev => {
      if (prev.some(b => b.id === bet.id)) return prev;
      return [...prev, bet];
    });
  }, []);

  const removeFromBetSlip = useCallback((betId) => {
    setBetSlip(prev => prev.filter(b => b.id !== betId));
  }, []);

  const clearBetSlip = useCallback(() => {
    setBetSlip([]);
  }, []);

  const updateFilter = useCallback((filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  }, []);

  // Fetch data (same as before)
  const fetchData = useCallback(async () => {
    if (loading) return;
    
    const cacheKey = `${selectedSport}-${selectedDate}`;
    const cachedData = cache[cacheKey];
    
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
        fetch(`${API_BASE_URL}/api/enhanced-recommendations/${selectedSport}?date=${selectedDate}`, { signal: controller.signal }),
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
      
      setCache(prev => ({ ...prev, [cacheKey]: newData }));

    } catch (err) {
      console.error('❌ Fetch error:', err.message);
      setError(err.name === 'AbortError' ? 'Request timed out' : `Connection error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedSport, selectedDate, API_BASE_URL, cache, loading]);

  useEffect(() => {
    fetchData();
    const interval = realTimeEnabled ? setInterval(fetchData, 60000) : null;
    return () => { if (interval) clearInterval(interval); };
  }, [selectedSport, selectedDate, realTimeEnabled]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="optimized-betting-platform">
      <header className="platform-header">
        <div className="header-content">
          <h1>🎰 AI-Powered Sports Betting</h1>
          <div className="header-stats">
            <span className="stat">📊 {filteredMoneylines.length} Bets</span>
            <span className="stat">🎯 {filteredParlays.length} Parlays</span>
            <span className="stat">💰 Bankroll: ${bankroll.toLocaleString()}</span>
            <span className="stat">🎫 Slip: {betSlip.length}</span>
          </div>
        </div>
        <div className="header-controls">
          <button 
            className={`toggle-filters-btn ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            🔍 {showFilters ? 'Hide' : 'Show'} Filters
          </button>
          <button 
            className={`realtime-toggle ${realTimeEnabled ? 'active' : ''}`}
            onClick={() => setRealTimeEnabled(!realTimeEnabled)}
            title="Enable 60-second auto-refresh"
          >
            {realTimeEnabled ? '🔄 Auto-Refresh ON' : '⏸️ Auto-Refresh OFF'}
          </button>
        </div>
      </header>

      {showFilters && (
        <AdvancedFilters filters={filters} onChange={updateFilter} />
      )}

      <div className="main-layout">
        <div className="bets-section">
          <div className="controls-bar">
            <div className="sport-selector">
              <label>Sport:</label>
              <select value={selectedSport} onChange={(e) => setSelectedSport(e.target.value)}>
                {sportsOptions.map(sport => (
                  <option key={sport.value} value={sport.value}>
                    {sport.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="date-tabs">
              <button 
                className={selectedDate === 'today' ? 'active' : ''}
                onClick={() => setSelectedDate('today')}
              >
                Today
              </button>
              <button 
                className={selectedDate === 'tomorrow' ? 'active' : ''}
                onClick={() => setSelectedDate('tomorrow')}
              >
                Tomorrow
              </button>
            </div>

            <div className="refresh-controls">
              <button className="refresh-btn" onClick={fetchData} disabled={loading}>
                {loading ? '⌛ Loading...' : '🔄 Refresh'}
              </button>
              {lastUpdate && <span className="last-update">Updated: {lastUpdate}</span>}
            </div>
          </div>

          {error && (
            <div className="error-banner">
              <span>⚠️ {error}</span>
              <button onClick={fetchData}>Retry</button>
            </div>
          )}

          <div className="bets-content">
            <section className="moneyline-section">
              <h2>💰 Moneyline Bets ({filteredMoneylines.length})</h2>
              {filteredMoneylines.length === 0 && !loading ? (
                <div className="no-bets">
                  <p>No bets match your filters</p>
                  <small>Try adjusting your filter settings</small>
                </div>
              ) : (
                <div className="bets-grid">
                  {filteredMoneylines.map((bet, idx) => (
                    <MoneylineCard 
                      key={`${bet.id}-${idx}`} 
                      bet={bet} 
                      dateType={selectedDate}
                      onAddToSlip={addToBetSlip}
                      inSlip={betSlip.some(b => b.id === bet.id)}
                    />
                  ))}
                </div>
              )}
            </section>

            <section className="parlay-section">
              <h2>🎲 Parlay Combinations ({filteredParlays.length})</h2>
              <div className="parlays-grid">
                {filteredParlays.map((parlay, idx) => (
                  <ParlayCard 
                    key={`${parlay.id}-${idx}`} 
                    parlay={parlay} 
                    dateType={selectedDate}
                    onAddToSlip={addToBetSlip}
                    inSlip={betSlip.some(b => b.id === parlay.id)}
                  />
                ))}
              </div>
            </section>
          </div>
        </div>

        <aside className="bet-slip-sidebar">
          <BetSlip 
            bets={betSlip}
            onRemove={removeFromBetSlip}
            onClear={clearBetSlip}
            bankroll={bankroll}
            onUpdateBankroll={setBankroll}
          />
        </aside>
      </div>
    </div>
  );
};

export default EnhancedBettingPlatform;
