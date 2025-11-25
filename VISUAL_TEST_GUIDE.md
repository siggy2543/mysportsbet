# 🎨 Visual Testing Guide - Frontend Display Verification

## Quick Visual Tests to Perform

### 1. Open Frontend
Navigate to: **http://localhost:3000**

---

### 2. Check Moneyline Bets Display

**What to Look For:**
- [ ] Bets are visible (not blank cards)
- [ ] Each bet shows: `Away @ Home` format (e.g., "Brooklyn Nets @ Boston Celtics")
- [ ] Recommendation displayed (e.g., "Boston Celtics Moneyline")
- [ ] Odds shown with +/- (e.g., "-17" or "+250")
- [ ] Confidence bar visible (percentage display)
- [ ] AI Calibrated badge shows
- [ ] Expected Value (EV) displayed
- [ ] Kelly Percentage shown
- [ ] GT Score visible
- [ ] Risk level indicator (Low/Medium/High)

**Expected Result:**
```
╔═══════════════════════════════════════╗
║  Brooklyn Nets @ Boston Celtics      ║
║  ✅ Boston Celtics Moneyline          ║
║  Odds: -17  |  85% confidence        ║
║  🎯 AI Calibrated                     ║
║  EV: +573% | Kelly: 0.0%             ║
║  GT Score: 0.31 | Risk: Low          ║
╚═══════════════════════════════════════╝
```

---

### 3. Check Parlay Combinations Display

**What to Look For:**
- [ ] Parlay section is visible (not empty)
- [ ] **9 total parlays** displayed
- [ ] **3 three-leg parlays** (labeled "3-Leg Parlay")
- [ ] **3 four-leg parlays** (labeled "4-Leg Parlay")
- [ ] **3 five-leg parlays** (labeled "5-Leg Parlay")
- [ ] Each leg shows matchup format: "Away @ Home"
- [ ] Each leg shows recommendation (e.g., "Warriors ML")
- [ ] Each leg shows odds (e.g., "-42")
- [ ] Each leg shows confidence percentage
- [ ] Combined odds displayed (e.g., "2.43x")
- [ ] Total confidence shown
- [ ] Risk level indicator
- [ ] AI Optimized badge visible

**Expected Result for 3-Leg Parlay:**
```
╔═══════════════════════════════════════╗
║  🎲 3-Leg Parlay                      ║
║  Combined Odds: 2.43x                 ║
║  Confidence: 36.1% | Risk: High      ║
║  ✨ AI Optimized                      ║
║                                       ║
║  Leg 1:                               ║
║  Washington Wizards @ Toronto Raptors ║
║  ✅ Toronto Raptors ML | -26 | 78.9% ║
║                                       ║
║  Leg 2:                               ║
║  LA Clippers @ Charlotte Hornets     ║
║  ✅ Charlotte Hornets ML | -35 | 73.9%║
║                                       ║
║  Leg 3:                               ║
║  Portland @ Golden State Warriors    ║
║  ✅ GSW ML | -42 | 70.2%             ║
╚═══════════════════════════════════════╝
```

---

### 4. Test Sports Selector

**Sports to Test (Click Through Each):**

**US Sports:**
- [ ] 🏀 NBA Basketball
- [ ] 🏈 NFL Football
- [ ] 🏒 NHL Hockey
- [ ] ⚾ MLB Baseball
- [ ] 🏀 NCAAB
- [ ] 🏈 NCAAF

**Global Soccer:**
- [ ] ⚽ EPL (Premier League)
- [ ] ⚽ La Liga
- [ ] ⚽ Bundesliga
- [ ] ⚽ Serie A
- [ ] ⚽ Ligue 1
- [ ] ⚽ Champions League
- [ ] ⚽ MLS

**Combat Sports:**
- [ ] 🥊 UFC
- [ ] 🥊 Boxing

**Tennis:**
- [ ] 🎾 ATP Tennis
- [ ] 🎾 WTA Tennis

**Individual Sports:**
- [ ] ⛳ Golf
- [ ] 🏎️ NASCAR
- [ ] 🏎️ Formula 1

**E-Sports:**
- [ ] 🎮 Esports

**Expected Behavior:**
- Clicking each sport loads new recommendations
- Bets change to match selected sport
- Parlays update for new sport
- Loading should take < 2 seconds

---

### 5. Test Date Filtering

**Tabs to Test:**
- [ ] Click "Today" tab
  - Should show bets with "Today" date category
  - Date badge should say "Today"
  
- [ ] Click "Tomorrow" tab
  - Should show bets with "Tomorrow" date category
  - Date badge should say "Tomorrow"

**Expected Behavior:**
- Different bets appear for Today vs Tomorrow
- Smooth transition between tabs
- No blank screens during switch

---

### 6. Visual Quality Checks

**Performance:**
- [ ] Page loads in < 2 seconds
- [ ] No flickering or layout shifts
- [ ] Smooth scrolling
- [ ] Responsive to clicks

**Design:**
- [ ] Clean, modern appearance
- [ ] Readable fonts and colors
- [ ] Icons display correctly (🏀, ⚽, 🥊, etc.)
- [ ] Confidence bars animate smoothly
- [ ] Badges are visible and styled
- [ ] Cards have proper spacing
- [ ] No overlapping elements

**Mobile Responsiveness (Optional):**
- [ ] Resize browser window
- [ ] Cards stack vertically on narrow screens
- [ ] Text remains readable
- [ ] Buttons stay accessible

---

### 7. Console Check (Developer Tools)

**Open Browser Console (F12):**
- [ ] No red errors
- [ ] No 404 errors for API calls
- [ ] No missing resource errors
- [ ] React warnings acceptable (minor)

**Network Tab:**
- [ ] `/api/recommendations/{sport}?date=today` returns 200
- [ ] `/api/parlays/{sport}?date=today` returns 200
- [ ] Response times < 5 seconds

---

## ✅ PASS CRITERIA

**All Tests Pass If:**
1. ✅ All bets visible with matchup, recommendation, odds
2. ✅ 9 parlays displayed (3 each of 3/4/5-leg)
3. ✅ All 24 sports load successfully
4. ✅ Date filtering works (Today/Tomorrow)
5. ✅ No console errors
6. ✅ Fast, responsive UI
7. ✅ Clean, professional appearance

---

## ❌ COMMON ISSUES & FIXES

### Issue: Bets Not Visible
**Symptoms:** Empty cards or blank screen  
**Causes:**
- API not running
- Component props mismatch
- Network error

**Fix:**
```bash
# Check API logs
docker logs sports_app-api-1

# Restart API
docker-compose restart api

# Rebuild frontend
docker-compose up -d --build --no-deps frontend
```

---

### Issue: Parlays Not Showing
**Symptoms:** Parlay section empty  
**Causes:**
- Parlay generation takes time (5-30s)
- Not enough bets available
- Sport doesn't have parlay data

**Fix:**
- Wait 30 seconds and refresh
- Try different sport (NBA, NFL work best)
- Check API logs for parlay generation errors

---

### Issue: Wrong Bet Structure
**Symptoms:** Shows "home_team" or "away_team" instead of matchup  
**Causes:**
- Old frontend code cached
- Component not updated

**Fix:**
```bash
# Force rebuild frontend
docker-compose down frontend
docker-compose up -d --build --no-cache frontend

# Clear browser cache
Ctrl + Shift + Delete (Chrome/Edge)
Cmd + Shift + Delete (Mac)
```

---

### Issue: Sports Don't Load
**Symptoms:** 404 errors when selecting sport  
**Causes:**
- Sport is off-season (MLS, NASCAR, MLB, F1)
- Invalid sport code
- API mapping issue

**Fix:**
- Try in-season sports (NBA, NFL, NHL, UFC)
- Check sport aliases are working
- Review API logs for errors

---

## 🎯 FINAL CHECKLIST

Before declaring victory:
- [ ] Frontend accessible at http://localhost:3000
- [ ] At least 5 different sports tested
- [ ] Both moneyline and parlay sections visible
- [ ] 9 parlays confirmed (count them!)
- [ ] Date filtering works
- [ ] No major console errors
- [ ] UI looks professional
- [ ] Response times acceptable

---

## 📸 SCREENSHOT LOCATIONS

**Take screenshots of:**
1. **Full page view** showing both bets and parlays
2. **Single bet card** showing all details
3. **3-leg parlay** expanded view
4. **Sports selector** with all 24 options
5. **Console tab** showing no errors

---

## 🎉 SUCCESS INDICATORS

**You'll know it's working when:**
- ✅ You see actual game matchups (not "undefined @ undefined")
- ✅ You count exactly 9 parlay cards
- ✅ Each parlay has 3, 4, or 5 legs (not random)
- ✅ Clicking sports changes the displayed bets
- ✅ Everything loads fast and looks professional
- ✅ Your first reaction is "This looks great!"

---

*Visual testing guide created: November 22, 2025*  
*Use this to verify all frontend enhancements are working correctly*
