-- AI Learning System - Historical Predictions and Feedback Loop
-- Add tables for tracking predictions and outcomes to improve AI accuracy over time

-- Predictions History Table
CREATE TABLE IF NOT EXISTS predictions_history (
    id SERIAL PRIMARY KEY,
    prediction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sport VARCHAR(50) NOT NULL,
    game_id VARCHAR(100),
    home_team VARCHAR(200) NOT NULL,
    away_team VARCHAR(200) NOT NULL,
    game_start_time TIMESTAMP NOT NULL,
    prediction_type VARCHAR(50) NOT NULL, -- 'moneyline', 'parlay', 'spread', 'total'
    predicted_winner VARCHAR(200),
    confidence_score DECIMAL(5,2) NOT NULL,
    ai_reasoning TEXT,
    odds_at_prediction JSONB, -- Store odds snapshot
    actual_outcome VARCHAR(200), -- Actual winner
    was_correct BOOLEAN,
    profit_loss DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 100)
);

-- Parlay History Table
CREATE TABLE IF NOT EXISTS parlay_history (
    id SERIAL PRIMARY KEY,
    parlay_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sport VARCHAR(50) NOT NULL,
    num_legs INTEGER NOT NULL,
    total_confidence DECIMAL(5,2) NOT NULL,
    payout_multiplier DECIMAL(10,2) NOT NULL,
    legs JSONB NOT NULL, -- Array of leg details
    actual_results JSONB, -- Actual outcomes
    was_successful BOOLEAN,
    profit_loss DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Model Performance Tracking
CREATE TABLE IF NOT EXISTS ai_performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    sport VARCHAR(50) NOT NULL,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2), -- Percentage
    average_confidence DECIMAL(5,2),
    total_profit_loss DECIMAL(10,2) DEFAULT 0,
    roi DECIMAL(5,2), -- Return on investment percentage
    best_confidence_range VARCHAR(50), -- e.g., "70-80%"
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, sport)
);

-- Confidence Calibration Table
-- Tracks how well predicted confidence matches actual outcomes
CREATE TABLE IF NOT EXISTS confidence_calibration (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    confidence_bucket VARCHAR(20) NOT NULL, -- e.g., "60-70", "70-80"
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    actual_accuracy DECIMAL(5,2),
    adjustment_factor DECIMAL(5,4) DEFAULT 1.0000, -- Used to calibrate future predictions
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sport, confidence_bucket)
);

-- Team Performance History
-- Track team-specific prediction accuracy for better future predictions
CREATE TABLE IF NOT EXISTS team_prediction_history (
    id SERIAL PRIMARY KEY,
    sport VARCHAR(50) NOT NULL,
    team_name VARCHAR(200) NOT NULL,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    average_confidence DECIMAL(5,2),
    as_favorite_accuracy DECIMAL(5,2), -- When predicted to win
    as_underdog_accuracy DECIMAL(5,2), -- When predicted to lose
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sport, team_name)
);

-- Learning Insights Table
-- Store AI-generated insights from analyzing historical data
CREATE TABLE IF NOT EXISTS learning_insights (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sport VARCHAR(50) NOT NULL,
    insight_type VARCHAR(100) NOT NULL, -- 'pattern', 'trend', 'anomaly'
    insight_text TEXT NOT NULL,
    confidence_impact DECIMAL(5,4), -- How much this insight affects confidence
    is_active BOOLEAN DEFAULT TRUE,
    validation_count INTEGER DEFAULT 0, -- How many times this insight proved correct
    expires_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_predictions_sport_date ON predictions_history(sport, prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_outcome ON predictions_history(was_correct) WHERE was_correct IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_parlay_sport_date ON parlay_history(sport, parlay_date DESC);
CREATE INDEX IF NOT EXISTS idx_ai_metrics_sport_date ON ai_performance_metrics(sport, metric_date DESC);
CREATE INDEX IF NOT EXISTS idx_team_history_sport ON team_prediction_history(sport, team_name);

-- Functions for calculating metrics

-- Function to update daily AI metrics
CREATE OR REPLACE FUNCTION update_daily_ai_metrics(p_sport VARCHAR, p_date DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO ai_performance_metrics (
        metric_date,
        sport,
        total_predictions,
        correct_predictions,
        accuracy_rate,
        average_confidence,
        total_profit_loss
    )
    SELECT 
        p_date,
        p_sport,
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE was_correct = TRUE) as correct,
        (COUNT(*) FILTER (WHERE was_correct = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as accuracy,
        AVG(confidence_score) as avg_conf,
        SUM(COALESCE(profit_loss, 0)) as profit
    FROM predictions_history
    WHERE sport = p_sport 
    AND DATE(prediction_date) = p_date
    AND was_correct IS NOT NULL
    ON CONFLICT (metric_date, sport) 
    DO UPDATE SET
        total_predictions = EXCLUDED.total_predictions,
        correct_predictions = EXCLUDED.correct_predictions,
        accuracy_rate = EXCLUDED.accuracy_rate,
        average_confidence = EXCLUDED.average_confidence,
        total_profit_loss = EXCLUDED.total_profit_loss,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to get calibrated confidence
CREATE OR REPLACE FUNCTION get_calibrated_confidence(
    p_sport VARCHAR,
    p_original_confidence DECIMAL
) RETURNS DECIMAL AS $$
DECLARE
    v_bucket VARCHAR(20);
    v_adjustment DECIMAL;
BEGIN
    -- Determine confidence bucket
    v_bucket := CASE 
        WHEN p_original_confidence >= 80 THEN '80-100'
        WHEN p_original_confidence >= 70 THEN '70-80'
        WHEN p_original_confidence >= 60 THEN '60-70'
        WHEN p_original_confidence >= 50 THEN '50-60'
        ELSE '0-50'
    END;
    
    -- Get adjustment factor
    SELECT adjustment_factor INTO v_adjustment
    FROM confidence_calibration
    WHERE sport = p_sport AND confidence_bucket = v_bucket;
    
    -- Return calibrated confidence
    RETURN LEAST(100, GREATEST(0, p_original_confidence * COALESCE(v_adjustment, 1.0)));
END;
$$ LANGUAGE plpgsql;

-- View for quick performance overview
CREATE OR REPLACE VIEW ai_performance_overview AS
SELECT 
    sport,
    COUNT(*) as total_predictions,
    COUNT(*) FILTER (WHERE was_correct = TRUE) as correct_predictions,
    ROUND((COUNT(*) FILTER (WHERE was_correct = TRUE)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as accuracy_rate,
    ROUND(AVG(confidence_score), 2) as avg_confidence,
    ROUND(SUM(COALESCE(profit_loss, 0)), 2) as total_profit_loss,
    MAX(prediction_date) as last_prediction
FROM predictions_history
WHERE was_correct IS NOT NULL
GROUP BY sport
ORDER BY accuracy_rate DESC;

-- Initial data for confidence calibration (will be updated based on actual results)
INSERT INTO confidence_calibration (sport, confidence_bucket, adjustment_factor) VALUES
('NBA', '80-100', 1.0), ('NBA', '70-80', 1.0), ('NBA', '60-70', 1.0), ('NBA', '50-60', 1.0), ('NBA', '0-50', 1.0),
('NFL', '80-100', 1.0), ('NFL', '70-80', 1.0), ('NFL', '60-70', 1.0), ('NFL', '50-60', 1.0), ('NFL', '0-50', 1.0),
('EPL', '80-100', 1.0), ('EPL', '70-80', 1.0), ('EPL', '60-70', 1.0), ('EPL', '50-60', 1.0), ('EPL', '0-50', 1.0),
('MMA', '80-100', 1.0), ('MMA', '70-80', 1.0), ('MMA', '60-70', 1.0), ('MMA', '50-60', 1.0), ('MMA', '0-50', 1.0)
ON CONFLICT (sport, confidence_bucket) DO NOTHING;

COMMENT ON TABLE predictions_history IS 'Stores all AI predictions with outcomes for learning and improvement';
COMMENT ON TABLE ai_performance_metrics IS 'Daily aggregated metrics to track AI model performance over time';
COMMENT ON TABLE confidence_calibration IS 'Calibration factors to adjust predicted confidence based on historical accuracy';
COMMENT ON TABLE learning_insights IS 'AI-generated insights from analyzing patterns in historical data';
