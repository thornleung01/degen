#!/usr/bin/env python3
"""
Complete Basketball Predictor with Real Data Integration
Automatically fetches real data from Basketball Reference when available
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import time


class IntegratedPlayerStatsAPI:
    """
    Complete prediction API with automatic Basketball Reference integration
    Falls back to sample data if library not available
    """
    
    def __init__(self, prefer_real_data: bool = True):
        """
        Initialize API with optional real data fetching
        
        Args:
            prefer_real_data: If True and library available, uses real data
        """
        self.use_real_data = False
        self.client = None
        self.cache = {}
        
        if prefer_real_data:
            try:
                from basketball_reference_web_scraper import client
                from basketball_reference_web_scraper.data import Team
                self.client = client
                self.Team = Team
                self.use_real_data = True
                print("✅ Using real Basketball Reference data")
            except ImportError:
                print("ℹ️  Using sample data (install basketball-reference-scraper for real data)")
    
    def predict_stat(self,
                    player_name: str,
                    stat: str,
                    threshold: float,
                    opponent: Optional[str] = None,
                    last_n_games: Optional[int] = None,
                    season: int = 2024,
                    player_id: Optional[str] = None) -> Dict:
        """
        Get prediction for a player stat
        
        Args:
            player_name: Full player name (e.g., "LeBron James")
            stat: Stat to predict ('points', 'assists', 'rebounds', etc.)
            threshold: Target value
            opponent: Optional - specific opponent abbreviation
            last_n_games: Optional - only analyze last N games
            season: Season year (default: 2024)
            player_id: Optional - Basketball Reference player ID (speeds up lookup)
            
        Returns:
            Dictionary with probability and statistics
        """
        # Get player data
        games_df = self._get_player_games(player_name, season, player_id)
        
        if games_df.empty:
            return {
                'error': f'No data found for {player_name}',
                'player': player_name,
                'stat': stat,
                'threshold': threshold
            }
        
        # Filter by opponent if specified
        if opponent:
            games_df = games_df[games_df['opponent'].str.contains(opponent, case=False, na=False)]
            if games_df.empty:
                return {
                    'error': f'No games found against {opponent}',
                    'player': player_name
                }
        
        # Filter to last N games
        if last_n_games:
            games_df = games_df.sort_values('date', ascending=False).head(last_n_games)
        
        # Get stat values
        if stat not in games_df.columns:
            return {
                'error': f'Stat "{stat}" not available in data',
                'available_stats': list(games_df.columns)
            }
        
        stat_values = games_df[stat].dropna().values
        
        if len(stat_values) == 0:
            return {'error': f'No {stat} data available'}
        
        # Calculate probability
        hits = np.sum(stat_values >= threshold)
        probability = (hits / len(stat_values)) * 100
        
        # Statistics
        mean = np.mean(stat_values)
        std_dev = np.std(stat_values)
        median = np.median(stat_values)
        
        # Trend calculation
        trend = self._calculate_trend(stat_values)
        
        # Confidence score
        consistency = max(0, 1 - (std_dev / (mean + 0.01)))
        sample_confidence = min(len(stat_values) / 20, 1.0)
        confidence = ((consistency + sample_confidence) / 2) * 100
        
        # Hit rates at different thresholds
        hit_rates = {}
        for pct in [0.7, 0.85, 1.0, 1.15, 1.3]:
            thresh = mean * pct
            rate = (np.sum(stat_values >= thresh) / len(stat_values)) * 100
            hit_rates[f'{thresh:.1f}+'] = round(rate, 1)
        
        result = {
            'player': player_name,
            'stat': stat,
            'threshold': threshold,
            'probability': round(probability, 1),
            'confidence': round(confidence, 1),
            'sample_size': len(stat_values),
            'games_analyzed': len(games_df),
            'average': round(mean, 1),
            'median': round(median, 1),
            'std_dev': round(std_dev, 1),
            'min': round(np.min(stat_values), 1),
            'max': round(np.max(stat_values), 1),
            'trend': trend,
            'hit_rates': hit_rates,
            'times_hit': int(hits),
            'times_missed': int(len(stat_values) - hits),
            'data_source': 'Basketball Reference' if self.use_real_data else 'Sample Data'
        }
        
        if opponent:
            result['opponent_filter'] = opponent
        if last_n_games:
            result['time_filter'] = f'Last {last_n_games} games'
        
        return result
    
    def _get_player_games(self, 
                         player_name: str, 
                         season: int,
                         player_id: Optional[str] = None) -> pd.DataFrame:
        """Fetch player game data from Basketball Reference or sample data"""
        
        cache_key = f"{player_name}_{season}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if self.use_real_data:
            df = self._fetch_real_data(player_name, season, player_id)
        else:
            df = self._generate_sample_data(player_name)
        
        self.cache[cache_key] = df
        return df
    
    def _fetch_real_data(self, 
                        player_name: str, 
                        season: int,
                        player_id: Optional[str] = None) -> pd.DataFrame:
        """Fetch real data from Basketball Reference"""
        
        try:
            # Get player ID if not provided
            if not player_id:
                player_id = self._search_player(player_name)
            
            if not player_id:
                print(f"⚠️  Could not find player ID for {player_name}")
                return pd.DataFrame()
            
            print(f"📥 Fetching {player_name} data for {season} season...")
            
            # Get game logs
            games = self.client.regular_season_player_box_scores(
                player_identifier=player_id,
                season_end_year=season
            )
            
            if not games:
                print(f"❌ No games found")
                return pd.DataFrame()
            
            df = pd.DataFrame(games)
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            print(f"✅ Loaded {len(df)} games")
            
            # Rate limiting (20 req/min = 3 seconds between calls)
            time.sleep(3)
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return pd.DataFrame()
    
    def _search_player(self, player_name: str) -> Optional[str]:
        """Search for player and return Basketball Reference ID"""
        
        try:
            # Check common players first
            if player_name in COMMON_PLAYERS:
                return COMMON_PLAYERS[player_name]
            
            # Search Basketball Reference
            results = self.client.search(term=player_name)
            
            if results:
                player_id = results[0]['identifier']
                print(f"  Found: {results[0]['name']} (ID: {player_id})")
                return player_id
            
            return None
            
        except Exception as e:
            print(f"  Search error: {e}")
            return None
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize Basketball Reference column names"""
        
        column_mapping = {
            'made_field_goals': 'field_goals_made',
            'attempted_field_goals': 'field_goals_attempted',
            'made_three_point_field_goals': '3pm',
            'attempted_three_point_field_goals': '3pa',
            'made_free_throws': 'free_throws_made',
            'attempted_free_throws': 'free_throws_attempted',
            'offensive_rebounds': 'off_rebounds',
            'defensive_rebounds': 'def_rebounds',
        }
        
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Calculate total rebounds
        if 'rebounds' not in df.columns:
            if 'off_rebounds' in df.columns and 'def_rebounds' in df.columns:
                df['rebounds'] = df['off_rebounds'] + df['def_rebounds']
        
        # Convert minutes from seconds if needed
        if 'seconds_played' in df.columns and 'minutes' not in df.columns:
            df['minutes'] = df['seconds_played'] / 60
        
        # Clean opponent names
        if 'opponent' in df.columns:
            df['opponent'] = df['opponent'].apply(
                lambda x: str(x).replace('Team.', '').replace('_', ' ').upper()
            )
        
        return df
    
    def _generate_sample_data(self, player_name: str) -> pd.DataFrame:
        """Generate sample data for testing"""
        from datetime import timedelta
        
        np.random.seed(hash(player_name) % 2**32)
        
        n_games = 30
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=i*3)).strftime('%Y-%m-%d') 
                 for i in range(n_games)]
        dates.reverse()
        
        teams = ['LAL', 'GSW', 'BOS', 'MIA', 'DEN', 'PHX', 'MIL', 'DAL']
        
        # Player-specific stat profiles
        if "curry" in player_name.lower():
            base_pts, base_ast, base_reb = 28, 6, 5
        elif "lebron" in player_name.lower() or "james" in player_name.lower():
            base_pts, base_ast, base_reb = 25, 7, 8
        elif "doncic" in player_name.lower() or "luka" in player_name.lower():
            base_pts, base_ast, base_reb = 30, 9, 9
        else:
            base_pts, base_ast, base_reb = 20, 5, 7
        
        games = []
        for i in range(n_games):
            games.append({
                'date': dates[i],
                'opponent': np.random.choice(teams),
                'points': max(0, np.random.normal(base_pts, 6)),
                'assists': max(0, np.random.normal(base_ast, 2)),
                'rebounds': max(0, np.random.normal(base_reb, 2)),
                'steals': max(0, np.random.normal(1.2, 0.8)),
                'blocks': max(0, np.random.normal(0.6, 0.5)),
                '3pm': max(0, np.random.normal(3, 1.5)),
                'minutes': np.random.uniform(28, 38)
            })
        
        return pd.DataFrame(games)
    
    def _calculate_trend(self, values: np.ndarray, recent_n: int = 5) -> str:
        """Calculate trend direction"""
        if len(values) < recent_n * 2:
            return "insufficient_data"
        
        recent = values[-recent_n:]
        previous = values[-recent_n*2:-recent_n]
        
        recent_avg = np.mean(recent)
        previous_avg = np.mean(previous)
        
        diff_pct = ((recent_avg - previous_avg) / (previous_avg + 0.01)) * 100
        
        if diff_pct > 10:
            return "📈 Trending Up"
        elif diff_pct < -10:
            return "📉 Trending Down"
        else:
            return "➡️  Stable"


# Common player IDs for quick reference
COMMON_PLAYERS = {
    "LeBron James": "jamesle01",
    "Stephen Curry": "curryst01",
    "Kevin Durant": "duranke01",
    "Giannis Antetokounmpo": "antetgi01",
    "Luka Doncic": "doncilu01",
    "Nikola Jokic": "jokicni01",
    "Joel Embiid": "embiijo01",
    "Jayson Tatum": "tatumja01",
    "Damian Lillard": "lillada01",
    "Anthony Davis": "davisan02",
}


def print_prediction_report(result: Dict):
    """Pretty print prediction results"""
    if 'error' in result:
        print(f"❌ {result['error']}")
        return
    
    print("\n" + "="*70)
    print(f"🏀 PREDICTION REPORT: {result['player']}")
    print("="*70)
    print(f"\n📊 Stat: {result['stat'].upper()}")
    print(f"🎯 Target: {result['threshold']}+")
    print(f"📁 Source: {result['data_source']}")
    
    if 'opponent_filter' in result:
        print(f"🏟️  vs {result['opponent_filter']}")
    if 'time_filter' in result:
        print(f"📅 {result['time_filter']}")
    
    print(f"\n{'='*70}")
    print(f"✅ PROBABILITY: {result['probability']}%")
    print(f"📈 CONFIDENCE: {result['confidence']}%")
    print(f"{'='*70}")
    
    print(f"\n📊 Statistics:")
    print(f"  Games: {result['games_analyzed']}")
    print(f"  Average: {result['average']}")
    print(f"  Median: {result['median']}")
    print(f"  Range: {result['min']} - {result['max']}")
    print(f"  Hit/Miss: {result['times_hit']}/{result['times_missed']}")
    print(f"  Trend: {result['trend']}")
    print("="*70)


def main():
    """Example usage with real or sample data"""
    
    print("="*70)
    print("🏀 INTEGRATED BASKETBALL STATS PREDICTOR")
    print("="*70)
    
    # Initialize (automatically detects if library is available)
    api = IntegratedPlayerStatsAPI(prefer_real_data=True)
    
    # Example 1: Basic prediction
    print("\n📊 Example 1: LeBron James - Will he score 25+ points?")
    result = api.predict_stat(
        player_name="LeBron James",
        stat="points",
        threshold=25,
        last_n_games=10,
        season=2024,
        player_id="jamesle01"  # Optional: speeds up lookup
    )
    print_prediction_report(result)
    
    # Example 2: Opponent-specific
    print("\n📊 Example 2: Stephen Curry vs Lakers")
    result = api.predict_stat(
        player_name="Stephen Curry",
        stat="3pm",
        threshold=5,
        opponent="LAL",
        season=2024,
        player_id="curryst01"
    )
    print_prediction_report(result)
    
    # Example 3: Multiple stats
    print("\n📊 Example 3: Multi-stat analysis")
    stats = [
        ('points', 25),
        ('assists', 7),
        ('rebounds', 8)
    ]
    
    print("\nLeBron James - Last 10 Games:")
    for stat, threshold in stats:
        result = api.predict_stat(
            "LeBron James",
            stat,
            threshold,
            last_n_games=10,
            player_id="jamesle01"
        )
        if 'error' not in result:
            print(f"  {stat.upper():>10} {threshold}+: {result['probability']:>5.1f}% ({result['average']:.1f} avg)")
    
    print("\n" + "="*70)
    print("✅ Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
