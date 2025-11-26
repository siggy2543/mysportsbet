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
  const [activeTab, setActiveTab] = useState('bets'); // 'bets' or 'parlay-builder'
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

  // Parlay Builder State
  const [parlayLegs, setParlayLegs] = useState(3);
  const [parlayBuilder, setParlayBuilder] = useState([]);
  const [parlayStake, setParlayStake] = useState(100);

  const API_BASE_URL = process.env.REACT_APP_API_URL || '';

  // Dynamic sports loaded from The Odds API (all 149 sports)
  const [sportsOptions, setSportsOptions] = useState([]);
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
            // Get emoji based on sport group
            const sportKey = sport.group.toLowerCase().replace(/[\s_]/g, '');
            const emojiMap = {
              'americanfootball': '🏈', 'basketball': '🏀', 'icehockey': '🏒',
              'baseball': '⚾', 'soccer': '⚽', 'tennis': '🎾', 'cricket': '🏏',
              'rugby': '🏉', 'boxing': '🥊', 'mma': '🥊', 'golf': '⛳',
              'motorsport': '🏎️', 'aussierules': '🏉', 'darts': '🎯',
              'volleyball': '🏐', 'handball': '🤾', 'tabletennis': '🏓'
            };
            const emoji = emojiMap[sportKey] || '🏆';
            
            return {
              value: sport.key,
              label: `${emoji} ${sport.title}`,
              group: sport.group,
              active: sport.active,
              description: sport.description
            };
          });
          
          // Sort: active sports first, then alphabetically
          formattedSports.sort((a, b) => {
            if (a.active !== b.active) return b.active - a.active;
            return a.label.localeCompare(b.label);
          });
          
          setSportsOptions(formattedSports);
          console.log(`✅ Loaded ${data.total_sports} sports (${data.active_sports} active)`);
        }
      } catch (err) {
        console.error('❌ Error fetching sports:', err);
        // Fallback to NBA if API fails
        setSportsOptions([{ value: 'NBA', label: '🏀 NBA Basketball', active: true }]);
      } finally {
        setSportsLoading(false);
      }
    };
    
    fetchSports();
  }, [API_BASE_URL]);

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
          <h1>🎰 AI-Powered Sports Betting - 149 Global Sports</h1>
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
          <div className="tab-selector" style={{marginBottom: '20px', display: 'flex', gap: '10px', borderBottom: '2px solid #333'}}>
            <button 
              className={activeTab === 'bets' ? 'tab-active' : 'tab-inactive'}
              onClick={() => setActiveTab('bets')}
              style={{
                padding: '10px 20px',
                background: activeTab === 'bets' ? '#4CAF50' : '#333',
                color: 'white',
                border: 'none',
                borderRadius: '8px 8px 0 0',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              💰 Live Bets
            </button>
            <button 
              className={activeTab === 'parlay-builder' ? 'tab-active' : 'tab-inactive'}
              onClick={() => setActiveTab('parlay-builder')}
              style={{
                padding: '10px 20px',
                background: activeTab === 'parlay-builder' ? '#4CAF50' : '#333',
                color: 'white',
                border: 'none',
                borderRadius: '8px 8px 0 0',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              🎯 Parlay Builder (2-5 Legs)
            </button>
          </div>

          <div className="controls-bar">
            <div className="sport-selector">
              <label>Sport ({sportsLoading ? 'Loading...' : `${sportsOptions.length} available`}):</label>
              <select 
                value={selectedSport} 
                onChange={(e) => setSelectedSport(e.target.value)}
                disabled={sportsLoading}
              >
                {sportsOptions.map(sport => (
                  <option key={sport.value} value={sport.value}>
                    {sport.label} {!sport.active ? '(Inactive)' : ''}
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

          {activeTab === 'bets' && (
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
          )}

          {activeTab === 'parlay-builder' && (
            <div className="parlay-builder-content" style={{padding: '20px', background: '#1a1a1a', borderRadius: '12px'}}>
              <h2 style={{marginBottom: '20px', color: '#4CAF50'}}>🎯 Custom Parlay Builder</h2>
              
              <div style={{marginBottom: '30px', padding: '20px', background: '#222', borderRadius: '8px'}}>
                <label style={{display: 'block', marginBottom: '10px', fontSize: '16px', fontWeight: 'bold'}}>
                  Select Number of Legs:
                </label>
                <div style={{display: 'flex', gap: '10px'}}>
                  {[2, 3, 4, 5].map(legs => (
                    <button
                      key={legs}
                      onClick={() => setParlayLegs(legs)}
                      style={{
                        padding: '12px 24px',
                        background: parlayLegs === legs ? '#4CAF50' : '#333',
                        color: 'white',
                        border: parlayLegs === legs ? '2px solid #66ff66' : '2px solid #444',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontSize: '16px',
                        fontWeight: 'bold',
                        transition: 'all 0.3s'
                      }}
                    >
                      {legs} Legs
                    </button>
                  ))}
                </div>
              </div>

              <div style={{marginBottom: '30px'}}>
                <h3 style={{marginBottom: '15px', color: '#66ff66'}}>
                  Select {parlayLegs} Games (Current: {parlayBuilder.length}/{parlayLegs})
                </h3>
                {filteredMoneylines.length === 0 ? (
                  <div className="no-bets">
                    <p>No games available for {selectedSport}</p>
                    <small>Try selecting a different sport or date</small>
                  </div>
                ) : (
                  <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px'}}>
                    {filteredMoneylines.slice(0, 10).map((bet, idx) => {
                      const isInParlay = parlayBuilder.some(b => b.id === bet.id);
                      const canAdd = parlayBuilder.length < parlayLegs;
                      
                      return (
                        <div 
                          key={`parlay-${bet.id}-${idx}`}
                          style={{
                            padding: '15px',
                            background: isInParlay ? '#2d5a2d' : '#2a2a2a',
                            border: isInParlay ? '2px solid #4CAF50' : '2px solid #444',
                            borderRadius: '8px',
                            cursor: canAdd || isInParlay ? 'pointer' : 'not-allowed',
                            opacity: (!canAdd && !isInParlay) ? 0.5 : 1,
                            transition: 'all 0.3s'
                          }}
                          onClick={() => {
                            if (isInParlay) {
                              setParlayBuilder(parlayBuilder.filter(b => b.id !== bet.id));
                            } else if (canAdd) {
                              setParlayBuilder([...parlayBuilder, bet]);
                            }
                          }}
                        >
                          <div style={{marginBottom: '10px'}}>
                            <strong style={{color: '#4CAF50', fontSize: '14px'}}>{bet.matchup}</strong>
                          </div>
                          <div style={{marginBottom: '8px'}}>
                            <span style={{color: '#aaa', fontSize: '12px'}}>Pick: </span>
                            <span style={{color: 'white', fontWeight: 'bold'}}>{bet.bet}</span>
                          </div>
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                            <span style={{color: '#ffcc00', fontWeight: 'bold'}}>
                              {bet.odds?.recommended_odds > 0 ? '+' : ''}{bet.odds?.recommended_odds}
                            </span>
                            <span style={{
                              padding: '4px 8px',
                              background: bet.confidence >= 75 ? '#2d5a2d' : '#5a4d2d',
                              borderRadius: '4px',
                              fontSize: '11px',
                              fontWeight: 'bold'
                            }}>
                              {bet.confidence}% Conf
                            </span>
                          </div>
                          {isInParlay && (
                            <div style={{marginTop: '10px', color: '#4CAF50', fontSize: '12px', textAlign: 'center'}}>
                              ✓ In Parlay
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {parlayBuilder.length > 0 && (
                <div style={{padding: '20px', background: '#222', borderRadius: '8px', marginTop: '20px'}}>
                  <h3 style={{marginBottom: '15px', color: '#66ff66'}}>Your {parlayLegs}-Leg Parlay</h3>
                  
                  <div style={{marginBottom: '20px'}}>
                    {parlayBuilder.map((bet, idx) => (
                      <div 
                        key={`selected-${bet.id}-${idx}`}
                        style={{
                          padding: '12px',
                          background: '#2a2a2a',
                          borderLeft: '4px solid #4CAF50',
                          marginBottom: '10px',
                          borderRadius: '4px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center'
                        }}
                      >
                        <div>
                          <div style={{fontWeight: 'bold', marginBottom: '4px'}}>{bet.matchup}</div>
                          <div style={{fontSize: '13px', color: '#aaa'}}>{bet.bet}</div>
                        </div>
                        <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
                          <span style={{color: '#ffcc00', fontWeight: 'bold'}}>
                            {bet.odds?.recommended_odds > 0 ? '+' : ''}{bet.odds?.recommended_odds}
                          </span>
                          <button
                            onClick={() => setParlayBuilder(parlayBuilder.filter(b => b.id !== bet.id))}
                            style={{
                              background: '#d32f2f',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '6px 12px',
                              cursor: 'pointer',
                              fontSize: '12px'
                            }}
                          >
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {parlayBuilder.length === parlayLegs && (
                    <div style={{marginTop: '20px', padding: '20px', background: '#1a3a1a', borderRadius: '8px', border: '2px solid #4CAF50'}}>
                      <h4 style={{marginBottom: '15px', color: '#66ff66'}}>Parlay Summary</h4>
                      <div style={{marginBottom: '15px'}}>
                        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                          <span>Number of Legs:</span>
                          <span style={{fontWeight: 'bold'}}>{parlayLegs}</span>
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                          <span>Combined Odds:</span>
                          <span style={{color: '#ffcc00', fontWeight: 'bold'}}>
                            {(() => {
                              const decimalOdds = parlayBuilder.map(bet => {
                                const odds = bet.odds?.recommended_odds || 0;
                                return odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
                              });
                              const combined = decimalOdds.reduce((acc, odd) => acc * odd, 1);
                              const americanOdds = combined >= 2 ? Math.round((combined - 1) * 100) : Math.round(-100 / (combined - 1));
                              return americanOdds > 0 ? `+${americanOdds}` : americanOdds;
                            })()}
                          </span>
                        </div>
                        <div style={{marginBottom: '15px'}}>
                          <label style={{display: 'block', marginBottom: '8px'}}>Stake Amount:</label>
                          <input
                            type="number"
                            value={parlayStake}
                            onChange={(e) => setParlayStake(parseFloat(e.target.value) || 0)}
                            style={{
                              width: '100%',
                              padding: '10px',
                              background: '#333',
                              border: '1px solid #666',
                              borderRadius: '4px',
                              color: 'white',
                              fontSize: '16px'
                            }}
                            min="1"
                            step="10"
                          />
                        </div>
                        <div style={{display: 'flex', justifyContent: 'space-between', padding: '15px 0', borderTop: '1px solid #444'}}>
                          <span style={{fontSize: '18px', fontWeight: 'bold'}}>Potential Payout:</span>
                          <span style={{fontSize: '20px', color: '#4CAF50', fontWeight: 'bold'}}>
                            ${(() => {
                              const decimalOdds = parlayBuilder.map(bet => {
                                const odds = bet.odds?.recommended_odds || 0;
                                return odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
                              });
                              const combined = decimalOdds.reduce((acc, odd) => acc * odd, 1);
                              return (parlayStake * combined).toFixed(2);
                            })()}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          alert(`Placing ${parlayLegs}-leg parlay with $${parlayStake} stake!`);
                          setParlayBuilder([]);
                          setParlayStake(100);
                        }}
                        style={{
                          width: '100%',
                          padding: '15px',
                          background: '#4CAF50',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          fontSize: '18px',
                          fontWeight: 'bold',
                          cursor: 'pointer',
                          transition: 'all 0.3s'
                        }}
                        onMouseEnter={(e) => e.target.style.background = '#66ff66'}
                        onMouseLeave={(e) => e.target.style.background = '#4CAF50'}
                      >
                        🎯 Place {parlayLegs}-Leg Parlay
                      </button>
                    </div>
                  )}

                  {parlayBuilder.length < parlayLegs && (
                    <div style={{textAlign: 'center', padding: '15px', background: '#2a2a1a', borderRadius: '8px', color: '#ffcc00'}}>
                      ⚠️ Select {parlayLegs - parlayBuilder.length} more game(s) to complete your parlay
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
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
