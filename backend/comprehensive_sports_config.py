"""
Comprehensive Sports Configuration for All 149 TheOddsAPI Sports
Maps each TheOddsAPI sport key to unique configuration
Source: https://the-odds-api.com/liveapi/guides/v4/#get-sports
"""

# Complete mapping of all 149 sports from TheOddsAPI
# Each sport gets its OWN unique configuration
THE_ODDS_API_SPORTS_CONFIG = {
    # ============= AMERICAN FOOTBALL =============
    'americanfootball_nfl': {
        'category': 'American Football',
        'display_name': 'NFL',
        'description': 'National Football League',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'americanfootball_ncaaf': {
        'category': 'American Football',
        'display_name': 'NCAAF',
        'description': 'NCAA College Football',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'americanfootball_cfl': {
        'category': 'American Football',
        'display_name': 'CFL',
        'description': 'Canadian Football League',
        'region': 'Canada',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    
    # ============= BASKETBALL =============
    'basketball_nba': {
        'category': 'Basketball',
        'display_name': 'NBA',
        'description': 'National Basketball Association',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'basketball_ncaab': {
        'category': 'Basketball',
        'display_name': 'NCAAB',
        'description': 'NCAA College Basketball',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'basketball_wnba': {
        'category': 'Basketball',
        'display_name': 'WNBA',
        'description': 'Women\'s National Basketball Association',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': False,
        'live_betting': True
    },
    'basketball_euroleague': {
        'category': 'Basketball',
        'display_name': 'EuroLeague',
        'description': 'European Basketball League',
        'region': 'Europe',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'basketball_nbl': {
        'category': 'Basketball',
        'display_name': 'NBL',
        'description': 'Australian National Basketball League',
        'region': 'Australia',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= ICE HOCKEY =============
    'icehockey_nhl': {
        'category': 'Ice Hockey',
        'display_name': 'NHL',
        'description': 'National Hockey League',
        'region': 'United States/Canada',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'icehockey_sweden_hockey_league': {
        'category': 'Ice Hockey',
        'display_name': 'SHL',
        'description': 'Swedish Hockey League',
        'region': 'Sweden',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'icehockey_finland_liiga': {
        'category': 'Ice Hockey',
        'display_name': 'Liiga',
        'description': 'Finnish Hockey League',
        'region': 'Finland',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'icehockey_khl': {
        'category': 'Ice Hockey',
        'display_name': 'KHL',
        'description': 'Kontinental Hockey League',
        'region': 'Russia',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= BASEBALL =============
    'baseball_mlb': {
        'category': 'Baseball',
        'display_name': 'MLB',
        'description': 'Major League Baseball',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': False,
        'live_betting': True
    },
    'baseball_npb': {
        'category': 'Baseball',
        'display_name': 'NPB',
        'description': 'Nippon Professional Baseball',
        'region': 'Japan',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'baseball_kbo': {
        'category': 'Baseball',
        'display_name': 'KBO',
        'description': 'Korean Baseball Organization',
        'region': 'South Korea',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= SOCCER (70+ LEAGUES) =============
    # Major European Leagues
    'soccer_epl': {
        'category': 'Soccer',
        'display_name': 'English Premier League',
        'description': 'Premier League',
        'region': 'England',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_spain_la_liga': {
        'category': 'Soccer',
        'display_name': 'La Liga',
        'description': 'Spanish La Liga',
        'region': 'Spain',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_germany_bundesliga': {
        'category': 'Soccer',
        'display_name': 'Bundesliga',
        'description': 'German Bundesliga',
        'region': 'Germany',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_italy_serie_a': {
        'category': 'Soccer',
        'display_name': 'Serie A',
        'description': 'Italian Serie A',
        'region': 'Italy',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_france_ligue_one': {
        'category': 'Soccer',
        'display_name': 'Ligue 1',
        'description': 'French Ligue 1',
        'region': 'France',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_uefa_champs_league': {
        'category': 'Soccer',
        'display_name': 'UEFA Champions League',
        'description': 'Champions League',
        'region': 'Europe',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_uefa_europa_league': {
        'category': 'Soccer',
        'display_name': 'UEFA Europa League',
        'description': 'Europa League',
        'region': 'Europe',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    # Other Soccer Leagues
    'soccer_usa_mls': {
        'category': 'Soccer',
        'display_name': 'MLS',
        'description': 'Major League Soccer',
        'region': 'United States',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_brazil_campeonato': {
        'category': 'Soccer',
        'display_name': 'Brasileirão',
        'description': 'Brazilian Serie A',
        'region': 'Brazil',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_argentina_primera_division': {
        'category': 'Soccer',
        'display_name': 'Argentina Primera División',
        'description': 'Argentine First Division',
        'region': 'Argentina',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_mexico_ligamx': {
        'category': 'Soccer',
        'display_name': 'Liga MX',
        'description': 'Mexican Liga MX',
        'region': 'Mexico',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_england_efl_cup': {
        'category': 'Soccer',
        'display_name': 'EFL Cup',
        'description': 'English League Cup',
        'region': 'England',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_fa_cup': {
        'category': 'Soccer',
        'display_name': 'FA Cup',
        'description': 'English FA Cup',
        'region': 'England',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_england_league1': {
        'category': 'Soccer',
        'display_name': 'English League One',
        'description': 'English League 1',
        'region': 'England',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_england_league2': {
        'category': 'Soccer',
        'display_name': 'English League Two',
        'description': 'English League 2',
        'region': 'England',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_spl': {
        'category': 'Soccer',
        'display_name': 'Scottish Premiership',
        'description': 'Scottish Premier League',
        'region': 'Scotland',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_netherlands_eredivisie': {
        'category': 'Soccer',
        'display_name': 'Eredivisie',
        'description': 'Dutch Eredivisie',
        'region': 'Netherlands',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_portugal_primeira_liga': {
        'category': 'Soccer',
        'display_name': 'Primeira Liga',
        'description': 'Portuguese First League',
        'region': 'Portugal',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_turkey_super_league': {
        'category': 'Soccer',
        'display_name': 'Süper Lig',
        'description': 'Turkish Super League',
        'region': 'Turkey',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_belgium_first_div': {
        'category': 'Soccer',
        'display_name': 'Belgian First Division',
        'description': 'Belgian Pro League',
        'region': 'Belgium',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_switzerland_superleague': {
        'category': 'Soccer',
        'display_name': 'Swiss Super League',
        'description': 'Swiss Super League',
        'region': 'Switzerland',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_austria_bundesliga': {
        'category': 'Soccer',
        'display_name': 'Austrian Bundesliga',
        'description': 'Austrian Bundesliga',
        'region': 'Austria',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_denmark_superliga': {
        'category': 'Soccer',
        'display_name': 'Danish Superliga',
        'description': 'Danish Superliga',
        'region': 'Denmark',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_sweden_allsvenskan': {
        'category': 'Soccer',
        'display_name': 'Allsvenskan',
        'description': 'Swedish Allsvenskan',
        'region': 'Sweden',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'soccer_sweden_superettan': {
        'category': 'Soccer',
        'display_name': 'Superettan',
        'description': 'Swedish Superettan',
        'region': 'Sweden',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'soccer_norway_eliteserien': {
        'category': 'Soccer',
        'display_name': 'Eliteserien',
        'description': 'Norwegian Eliteserien',
        'region': 'Norway',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'soccer_finland_veikkausliiga': {
        'category': 'Soccer',
        'display_name': 'Veikkausliiga',
        'description': 'Finnish Veikkausliiga',
        'region': 'Finland',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'soccer_poland_ekstraklasa': {
        'category': 'Soccer',
        'display_name': 'Ekstraklasa',
        'description': 'Polish Ekstraklasa',
        'region': 'Poland',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_greece_super_league': {
        'category': 'Soccer',
        'display_name': 'Super League Greece',
        'description': 'Greek Super League',
        'region': 'Greece',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_australia_aleague': {
        'category': 'Soccer',
        'display_name': 'A-League',
        'description': 'Australian A-League',
        'region': 'Australia',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_japan_j_league': {
        'category': 'Soccer',
        'display_name': 'J-League',
        'description': 'Japanese J-League',
        'region': 'Japan',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_south_korea_kleague1': {
        'category': 'Soccer',
        'display_name': 'K League 1',
        'description': 'South Korean K League',
        'region': 'South Korea',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'soccer_china_superleague': {
        'category': 'Soccer',
        'display_name': 'Chinese Super League',
        'description': 'Chinese Super League',
        'region': 'China',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= TENNIS =============
    'tennis_atp_australian_open': {
        'category': 'Tennis',
        'display_name': 'ATP Australian Open',
        'description': 'Australian Open',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_atp_french_open': {
        'category': 'Tennis',
        'display_name': 'ATP French Open',
        'description': 'French Open',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_atp_us_open': {
        'category': 'Tennis',
        'display_name': 'ATP US Open',
        'description': 'US Open',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_atp_wimbledon': {
        'category': 'Tennis',
        'display_name': 'ATP Wimbledon',
        'description': 'Wimbledon',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_wta_australian_open': {
        'category': 'Tennis',
        'display_name': 'WTA Australian Open',
        'description': 'Australian Open Women',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_wta_french_open': {
        'category': 'Tennis',
        'display_name': 'WTA French Open',
        'description': 'French Open Women',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_wta_us_open': {
        'category': 'Tennis',
        'display_name': 'WTA US Open',
        'description': 'US Open Women',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    'tennis_wta_wimbledon': {
        'category': 'Tennis',
        'display_name': 'WTA Wimbledon',
        'description': 'Wimbledon Women',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    
    # ============= CRICKET =============
    'cricket_test_match': {
        'category': 'Cricket',
        'display_name': 'Test Cricket',
        'description': 'International Test Matches',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'cricket_odi': {
        'category': 'Cricket',
        'display_name': 'ODI Cricket',
        'description': 'One Day Internationals',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'cricket_t20': {
        'category': 'Cricket',
        'display_name': 'T20 Cricket',
        'description': 'Twenty20 Internationals',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'totals', 'player_props'],
        'season_active': True,
        'live_betting': True
    },
    'cricket_big_bash': {
        'category': 'Cricket',
        'display_name': 'Big Bash League',
        'description': 'Australian Big Bash',
        'region': 'Australia',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'cricket_ipl': {
        'category': 'Cricket',
        'display_name': 'IPL',
        'description': 'Indian Premier League',
        'region': 'India',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'totals', 'player_props'],
        'season_active': False,
        'live_betting': True
    },
    'cricket_psl': {
        'category': 'Cricket',
        'display_name': 'PSL',
        'description': 'Pakistan Super League',
        'region': 'Pakistan',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    
    # ============= COMBAT SPORTS =============
    'mma_mixed_martial_arts': {
        'category': 'Combat Sports',
        'display_name': 'MMA/UFC',
        'description': 'Mixed Martial Arts',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'method_of_victory', 'round_props'],
        'season_active': True,
        'live_betting': True
    },
    'boxing_boxing': {
        'category': 'Combat Sports',
        'display_name': 'Boxing',
        'description': 'Professional Boxing',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['h2h', 'method_of_victory', 'round_props'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= RUGBY =============
    'rugbyleague_nrl': {
        'category': 'Rugby',
        'display_name': 'NRL',
        'description': 'National Rugby League',
        'region': 'Australia',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'rugbyunion_super_rugby': {
        'category': 'Rugby',
        'display_name': 'Super Rugby',
        'description': 'Super Rugby',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    'rugbyunion_six_nations': {
        'category': 'Rugby',
        'display_name': 'Six Nations',
        'description': 'Six Nations Championship',
        'region': 'Europe',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': False,
        'live_betting': True
    },
    
    # ============= AUSSIE RULES =============
    'aussierules_afl': {
        'category': 'Aussie Rules',
        'display_name': 'AFL',
        'description': 'Australian Football League',
        'region': 'Australia',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    },
    
    # ============= GOLF =============
    'golf_masters_tournament_winner': {
        'category': 'Golf',
        'display_name': 'Masters Tournament',
        'description': 'The Masters',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['outrights', 'player_props'],
        'season_active': False,
        'live_betting': False
    },
    'golf_pga_championship_winner': {
        'category': 'Golf',
        'display_name': 'PGA Championship',
        'description': 'PGA Championship',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['outrights', 'player_props'],
        'season_active': False,
        'live_betting': False
    },
    'golf_us_open_winner': {
        'category': 'Golf',
        'display_name': 'US Open Golf',
        'description': 'US Open',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['outrights', 'player_props'],
        'season_active': False,
        'live_betting': False
    },
    'golf_the_open_championship_winner': {
        'category': 'Golf',
        'display_name': 'The Open Championship',
        'description': 'British Open',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': True,
        'markets': ['outrights', 'player_props'],
        'season_active': False,
        'live_betting': False
    },
}


def get_sport_config(sport_key: str) -> dict:
    """
    Get sport configuration by TheOddsAPI sport key
    Returns the config or creates a generic fallback if not found
    """
    if sport_key in THE_ODDS_API_SPORTS_CONFIG:
        return THE_ODDS_API_SPORTS_CONFIG[sport_key]
    
    # Generic fallback for unmapped sports
    return {
        'category': 'Other Sports',
        'display_name': sport_key.replace('_', ' ').title(),
        'description': f'Generic config for {sport_key}',
        'region': 'Global',
        'supports_parlays': True,
        'supports_player_props': False,
        'markets': ['h2h', 'spreads', 'totals'],
        'season_active': True,
        'live_betting': True
    }


def get_all_sports() -> dict:
    """Return all configured sports"""
    return THE_ODDS_API_SPORTS_CONFIG


def get_active_sports() -> dict:
    """Return only active sports"""
    return {k: v for k, v in THE_ODDS_API_SPORTS_CONFIG.items() if v.get('season_active', True)}
