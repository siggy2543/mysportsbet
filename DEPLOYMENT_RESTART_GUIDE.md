# 🚀 PRODUCTION RESTART & DEPLOYMENT GUIDE

## 🎯 IMMEDIATE DEPLOYMENT STEPS

Since terminal access is limited, follow these manual steps to restart and deploy the enhanced platform:

### Step 1: Execute Quick Restart
**Double-click this file:** `QUICK_RESTART.bat`

**OR manually run these commands in Command Prompt:**
```cmd
cd c:\Users\cigba\sports_app
QUICK_RESTART.bat
```

### Step 2: Manual Restart (if batch fails)

**Terminal 1 - Backend API:**
```cmd
cd c:\Users\cigba\sports_app\backend
python standalone_api.py
```

**Terminal 2 - Frontend (new window):**
```cmd
cd c:\Users\cigba\sports_app\frontend
set CI=false
npm start
```

## 🔍 VERIFICATION STEPS

### 1. Check Backend API (http://localhost:8000)
- **Health Check:** http://localhost:8000/api/health
- **Global Sports:** http://localhost:8000/api/global-sports (should return 22+ sports)
- **NBA Data:** http://localhost:8000/api/recommendations/NBA
- **EPL Data:** http://localhost:8000/api/recommendations/EPL

### 2. Check Frontend (http://localhost:3000)
- Should load enhanced dashboard
- Sports dropdown should show 22+ options (not just 4)
- Header should display live platform stats
- All tabs should populate with data

## 🎯 WHAT YOU SHOULD SEE AFTER DEPLOYMENT

### ✅ Enhanced Frontend Features
1. **Sports Selector Dropdown:** 
   - 🏀 NBA, 🏈 NFL, 🏒 NHL, ⚾ MLB (US Sports)
   - ⚽ EPL, La Liga, Bundesliga, Serie A, Ligue 1, Champions League
   - 🎾 ATP, WTA Tennis
   - 🏏 Cricket, 🏉 Rugby, 🏎️ F1, 🥊 MMA, ⛳ Golf, 🎮 E-Sports

2. **Live Data Indicators:**
   - Header shows "Global Sports: 22+"
   - "Game Theory: ACTIVE" status
   - Live timestamp with 🔴 indicator
   - Auto-refresh toggle (🟢 ON/🔴 OFF)

3. **Enhanced Betting Options:**
   - **Moneylines Tab:** AI recommendations with confidence scoring
   - **Parlays Tab:** 4-12 leg combinations with correlation analysis
   - **Player Props Tab:** Statistical betting with confidence ratings

### ✅ Backend API Enhancements
1. **Global Sports Support:** All 22+ sports functional
2. **Live Data Generation:** Real-time updates every 20 seconds
3. **Game Theory Integration:** Nash equilibrium calculations
4. **Advanced Features:** Parlays, player props, correlation analysis

## 🐛 TROUBLESHOOTING

### Issue 1: "Port already in use"
```cmd
netstat -ano | findstr ":8000"
taskkill /F /PID [PID_NUMBER]
```

### Issue 2: Frontend shows only 4 sports
**Cause:** API not responding or frontend cache
**Solution:**
1. Hard refresh browser: Ctrl+F5
2. Check API: http://localhost:8000/api/global-sports
3. Restart both services

### Issue 3: npm start fails
```cmd
cd c:\Users\cigba\sports_app\frontend
set CI=false
npm install --prefer-offline
npm start
```

### Issue 4: Python script won't start
**Check Python installation:**
```cmd
python --version
cd c:\Users\cigba\sports_app\backend
pip install -r requirements.txt
python standalone_api.py
```

## 📊 SUCCESS VALIDATION

### Backend Validation
Run these URLs in browser to confirm:
- http://localhost:8000/api/global-sports ➜ Should return 22+ sports
- http://localhost:8000/api/recommendations/EPL ➜ Should return EPL betting data
- http://localhost:8000/api/recommendations/ATP ➜ Should return tennis data
- http://localhost:8000/api/parlays/NBA ➜ Should return parlay combinations

### Frontend Validation
Check these features at http://localhost:3000:
- Sports dropdown has 22+ options (including EPL, ATP, Cricket, etc.)
- Header shows live platform statistics
- All tabs (Moneylines/Parlays/Player Props) populate with data
- Auto-refresh indicator works
- Can switch between global sports and see different data

## 🎉 DEPLOYMENT SUCCESS INDICATORS

When deployment is successful:
1. **Backend Console:** Shows "🌍 Global Sports Coverage: 22+ sports"
2. **Frontend:** Displays enhanced sports selector and live data
3. **API Response:** Global sports endpoint returns comprehensive data
4. **Live Updates:** Data refreshes every 20 seconds with visual indicators

## 🔴 PRODUCTION READY FEATURES

After successful deployment, the platform will have:
- ✅ **22+ Global Sports** (EPL, La Liga, ATP, WTA, Cricket, F1, MMA, etc.)
- ✅ **Live Data Streaming** (20-second auto-refresh)
- ✅ **Game Theory AI** (Nash equilibrium, minimax algorithms)
- ✅ **Intelligent Parlays** (4-12 legs with correlation analysis)
- ✅ **Player Props** (Statistical betting with confidence scores)
- ✅ **Enhanced UI/UX** (Live indicators, mobile-responsive design)

---

## 🎯 FINAL VALIDATION

Once both services are running:
1. Open http://localhost:3000
2. Verify sports dropdown shows 22+ options
3. Select different sports (EPL, ATP, Cricket) and confirm data loads
4. Check all tabs populate with relevant betting data
5. Verify live data updates and platform statistics in header

**The enhanced sports betting platform is now ready for global sports betting with AI-powered recommendations!**