#!/usr/bin/env python3
"""
Basketball Predictor API - Easy-to-use wrapper
Simplified interface for getting player predictions
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Union


class PlayerStatsAPI:
    """
    Simple API wrapper for basketball stats prediction
    
    Usage:
        api = PlayerStatsAPI()
        result = api.predict_stat("LeBron James", "points", 25, opponent="GSW")
    """
    
    def __init__(self, use_real_data: bool = False):
        """
        Initialize the API
        
        Args:
            use_real_data: If True, uses basketball-reference-scraper library
                          If False, uses sample data for testing
        """
        self.use_real_data = use_real_data
        self.cache = {}
        
        if use_real_data:
            try:
                from basketball_reference_web_scraper import client
                self.client = client
            except ImportError:
                print("⚠️  basketball-reference-scraper not installed")
                print("Install with: pip install basketball-reference-scraper --break-system-packages")
                self.use_real_data = False
    
    def predict_stat(self,
                    player_name: str,
                    stat: str,
                    threshold: float,
                    opponent: Optional[str] = None,
                    last_n_games: Optional[int] = None,
                    season: int = 2024) -> Dict:
        """
        Get prediction for a player stat
        
        Args:
            player_name: Full player name (e.g., "Stephen Curry")
            stat: Stat to predict ('points', 'assists', 'rebounds', 'steals', 'blocks', '3pm')
            threshold: Value to predict probability of hitting (e.g., 25 for 25+ points)
            opponent: Optional - specific opponent to analyze against
            last_n_games: Optional - only analyze last N games (e.g., 10)
            season: NBA season year (default: 2024)
            
        Returns:
            Dictionary with probability, confidence, and detailed stats
            
        Example:
            >>> api = PlayerStatsAPI()
            >>> result = api.predict_stat("LeBron James", "points", 25, last_n_games=10)
            >>> print(f"Probability: {result['probability']}%")
        """
        # Get player data
        games_df = self._get_player_games(player_name, season)
        
        if games_df.empty:
            return {'error': f'No data found for {player_name}'}
        
        # Filter by opponent if specified
        if opponent:
            games_df = games_df[games_df['opponent'].str.contains(opponent, case=False, na=False)]
            if games_df.empty:
                return {'error': f'No games found against {opponent}'}
        
        # Filter to last N games if specified
        if last_n_games:
            games_df = games_df.sort_values('date', ascending=False).head(last_n_games)
        
        # Calculate probability
        stat_values = games_df[stat].dropna().values
        
        if len(stat_values) == 0:
            return {'error': f'No {stat} data available'}
        
        # Calculate metrics
        hits = np.sum(stat_values >= threshold)
        probability = (hits / len(stat_values)) * 100
        
        mean = np.mean(stat_values)
        std_dev = np.std(stat_values)
        median = np.median(stat_values)
        
        # Hit rate for different thresholds
        hit_rates = self._calculate_hit_rates(stat_values)
        
        # Recent trend
        trend = self._calculate_trend(stat_values)
        
        # Confidence score
        consistency = max(0, 1 - (std_dev / (mean + 0.01)))
        sample_confidence = min(len(stat_values) / 20, 1.0)
        confidence = ((consistency + sample_confidence) / 2) * 100
        
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
            'times_missed': int(len(stat_values) - hits)
        }
        
        if opponent:
            result['opponent_filter'] = opponent
        
        if last_n_games:
            result['time_filter'] = f'Last {last_n_games} games'
        
        return result
    
    def compare_opponents(self,
                         player_name: str,
                         stat: str,
                         threshold: float,
                         opponents: List[str],
                         season: int = 2024) -> pd.DataFrame:
        """
        Compare player performance against multiple opponents
        
        Args:
            player_name: Player's full name
            stat: Stat to analyze
            threshold: Target threshold
            opponents: List of opponent abbreviations (e.g., ['LAL', 'GSW', 'BOS'])
            season: Season year
            
        Returns:
            DataFrame with comparison across opponents
        """
        results = []
        
        for opponent in opponents:
            result = self.predict_stat(
                player_name, stat, threshold, 
                opponent=opponent, season=season
            )
            
            if 'error' not in result:
                results.append({
                    'opponent': opponent,
                    'probability': result['probability'],
                    'games': result['games_analyzed'],
                    'average': result['average'],
                    'trend': result['trend']
                })
        
        return pd.DataFrame(results).sort_values('probability', ascending=False)
    
    def trend_analysis(self,
                      player_name: str,
                      stat: str,
                      season: int = 2024,
                      window_sizes: List[int] = [5, 10, 15, 20]) -> pd.DataFrame:
        """
        Analyze how probability changes over different time windows
        
        Args:
            player_name: Player's full name
            stat: Stat to analyze
            season: Season year
            window_sizes: List of game window sizes to analyze
            
        Returns:
            DataFrame showing trends across different windows
        """
        games_df = self._get_player_games(player_name, season)
        
        if games_df.empty:
            return pd.DataFrame()
        
        # Calculate average for each window
        results = []
        stat_values = games_df[stat].dropna().values
        
        for window in window_sizes:
            if len(stat_values) >= window:
                recent = stat_values[-window:]
                results.append({
                    'window': f'Last {window} games',
                    'average': round(np.mean(recent), 2),
                    'median': round(np.median(recent), 2),
                    'std_dev': round(np.std(recent), 2),
                    'min': round(np.min(recent), 2),
                    'max': round(np.max(recent), 2)
                })
        
        return pd.DataFrame(results)
    
    def _get_player_games(self, player_name: str, season: int) -> pd.DataFrame:
        """Fetch or generate player game data"""
        
        cache_key = f"{player_name}_{season}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if self.use_real_data:
            # TODO: Implement actual data fetching from basketball-reference
            # This requires proper player ID lookup and game log fetching
            df = pd.DataFrame()
        else:
            # Use sample data
            df = self._generate_sample_data(player_name, season)
        
        self.cache[cache_key] = df
        return df
    
    def _generate_sample_data(self, player_name: str, season: int) -> pd.DataFrame:
        """Generate realistic sample data for testing"""
        from datetime import timedelta
        
        np.random.seed(hash(player_name) % 2**32)
        
        n_games = 30
        end_date = datetime.now()
        dates = [(end_date - timedelta(days=i*3)).strftime('%Y-%m-%d') 
                 for i in range(n_games)]
        dates.reverse()
        
        teams = ['LAL', 'GSW', 'BOS', 'MIA', 'DEN', 'PHX', 'MIL', 'DAL', 
                 'BKN', 'PHI', 'CLE', 'ATL']
        
        games = []
        for i in range(n_games):
            opponent = np.random.choice(teams)
            
            # Different players have different stat profiles
            if "curry" in player_name.lower():
                base_pts, base_ast, base_reb = 28, 6, 5
            elif "lebron" in player_name.lower():
                base_pts, base_ast, base_reb = 25, 7, 8
            elif "doncic" in player_name.lower():
                base_pts, base_ast, base_reb = 30, 9, 9
            else:
                base_pts, base_ast, base_reb = 20, 5, 7
            
            # Add variance
            games.append({
                'date': dates[i],
                'opponent': opponent,
                'points': max(0, np.random.normal(base_pts, 6)),
                'assists': max(0, np.random.normal(base_ast, 2)),
                'rebounds': max(0, np.random.normal(base_reb, 2)),
                'steals': max(0, np.random.normal(1.2, 0.8)),
                'blocks': max(0, np.random.normal(0.6, 0.5)),
                '3pm': max(0, np.random.normal(3, 1.5)),
                'minutes': np.random.uniform(28, 38)
            })
        
        return pd.DataFrame(games)
    
    def _calculate_hit_rates(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate hit rates for common thresholds"""
        mean = np.mean(values)
        
        # Dynamic thresholds based on average
        thresholds = [
            mean * 0.7,
            mean * 0.85,
            mean,
            mean * 1.15,
            mean * 1.3
        ]
        
        hit_rates = {}
        for threshold in thresholds:
            rate = (np.sum(values >= threshold) / len(values)) * 100
            hit_rates[f'{threshold:.1f}+'] = round(rate, 1)
        
        return hit_rates
    
    def _calculate_trend(self, values: np.ndarray, recent_n: int = 5) -> str:
        """Determine if values are trending up, down, or stable"""
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


def print_prediction_report(result: Dict):
    """Pretty print a prediction result"""
    if 'error' in result:
        print(f"❌ {result['error']}")
        return
    
    print("\n" + "="*70)
    print(f"🏀 PREDICTION REPORT: {result['player']}")
    print("="*70)
    
    print(f"\n📊 Stat: {result['stat'].upper()}")
    print(f"🎯 Target: {result['threshold']}+")
    
    if 'opponent_filter' in result:
        print(f"🏟️  Opponent: {result['opponent_filter']}")
    
    if 'time_filter' in result:
        print(f"📅 Time Period: {result['time_filter']}")
    
    print(f"\n{'='*70}")
    print(f"✅ PROBABILITY: {result['probability']}%")
    print(f"📈 CONFIDENCE: {result['confidence']}%")
    print(f"{'='*70}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"  • Games Analyzed: {result['games_analyzed']}")
    print(f"  • Average: {result['average']}")
    print(f"  • Median: {result['median']}")
    print(f"  • Std Dev: {result['std_dev']}")
    print(f"  • Range: {result['min']} - {result['max']}")
    print(f"  • Hit: {result['times_hit']} times")
    print(f"  • Miss: {result['times_missed']} times")
    print(f"  • Trend: {result['trend']}")
    
    print(f"\n📊 Hit Rates at Different Thresholds:")
    for threshold, rate in result['hit_rates'].items():
        bars = '█' * int(rate / 5)
        print(f"  {threshold:>6}: {rate:>5.1f}% {bars}")
    
    print("\n" + "="*70)


def main():
    """Example usage"""
    
    print("🏀 Basketball Stats Prediction API")
    print("="*70)
    print("\nNote: Using sample data for demonstration")
    print("Install basketball-reference-scraper for real data\n")
    
    # Initialize API
    api = PlayerStatsAPI(use_real_data=False)
    
    # Example 1: Simple prediction
    print("\n" + "="*70)
    print("EXAMPLE 1: Will LeBron James score 25+ points in next game?")
    print("="*70)
    
    result = api.predict_stat(
        player_name="LeBron James",
        stat="points",
        threshold=25,
        last_n_games=10
    )
    
    print_prediction_report(result)
    
    # Example 2: Opponent-specific prediction
    print("\n" + "="*70)
    print("EXAMPLE 2: Stephen Curry vs Golden State Warriors")
    print("="*70)
    
    result = api.predict_stat(
        player_name="Stephen Curry",
        stat="3pm",
        threshold=5,
        opponent="GSW"
    )
    
    print_prediction_report(result)
    
    # Example 3: Compare multiple opponents
    print("\n" + "="*70)
    print("EXAMPLE 3: Luka Doncic Points vs Different Teams")
    print("="*70)
    
    comparison = api.compare_opponents(
        player_name="Luka Doncic",
        stat="points",
        threshold=30,
        opponents=['LAL', 'GSW', 'BOS', 'MIA', 'DEN']
    )
    
    print("\n📊 Opponent Comparison:")
    print(comparison.to_string(index=False))
    
    # Example 4: Trend analysis
    print("\n" + "="*70)
    print("EXAMPLE 4: Trend Analysis - How performance changes over time")
    print("="*70)
    
    trend = api.trend_analysis(
        player_name="LeBron James",
        stat="points",
        window_sizes=[5, 10, 15, 20]
    )
    
    print("\n📈 Performance Trends:")
    print(trend.to_string(index=False))
    
    # Example 5: Multiple stats
    print("\n" + "="*70)
    print("EXAMPLE 5: Multi-Stat Analysis")
    print("="*70)
    
    stats_to_check = [
        ('points', 25),
        ('assists', 7),
        ('rebounds', 8)
    ]
    
    print("\n🎯 Probability Summary for LeBron James:")
    for stat, threshold in stats_to_check:
        result = api.predict_stat("LeBron James", stat, threshold, last_n_games=10)
        if 'error' not in result:
            print(f"  {stat.upper():>10} >= {threshold:>2}: {result['probability']:>5.1f}% ({result['average']:.1f} avg)")
    
    print("\n" + "="*70)
    print("✅ Complete! Use this API to make informed predictions.")
    print("="*70)


if __name__ == "__main__":
    main()
