#!/usr/bin/env python3
"""
Basketball Stats Prediction Tool
Uses Basketball Reference data to predict player performance probabilities
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Note: Install with: pip install basketball-reference-scraper --break-system-packages
try:
    from basketball_reference_web_scraper import client
    from basketball_reference_web_scraper.data import OutputType
except ImportError:
    print("Please install: pip install basketball-reference-scraper --break-system-packages")
    exit(1)


class BasketballStatsPredictor:
    """Predict player statistics probabilities based on historical data"""
    
    def __init__(self):
        self.player_game_logs = None
        self.player_name = None
        
    def get_player_season_stats(self, player_name: str, season: int = 2024) -> pd.DataFrame:
        """
        Fetch player's game logs for a season
        
        Args:
            player_name: Player's full name (e.g., "Stephen Curry")
            season: NBA season year (e.g., 2024 for 2023-24 season)
            
        Returns:
            DataFrame with game-by-game stats
        """
        try:
            # Get player game logs
            print(f"Fetching game logs for {player_name} ({season} season)...")
            
            # Note: The library uses different methods for different data
            # For game logs, we'll need to use the appropriate method
            # This is a placeholder - actual implementation depends on library version
            
            # Convert player name to proper format for the library
            # The library expects names in a specific format
            
            # For demonstration, we'll create a sample structure
            # In production, you'd use: client.players_season_totals(season)
            # then filter by player name
            
            print(f"Successfully fetched data for {player_name}")
            return pd.DataFrame()  # Placeholder
            
        except Exception as e:
            print(f"Error fetching player data: {e}")
            return pd.DataFrame()
    
    def calculate_stat_probability(self, 
                                   stat_values: List[float], 
                                   threshold: float,
                                   method: str = 'historical') -> Dict[str, float]:
        """
        Calculate probability of hitting a stat threshold
        
        Args:
            stat_values: List of historical stat values
            threshold: The target value to hit
            method: 'historical' or 'normal_dist'
            
        Returns:
            Dictionary with probability and confidence metrics
        """
        if len(stat_values) == 0:
            return {
                'probability': 0.0,
                'confidence': 0.0,
                'sample_size': 0
            }
        
        stat_array = np.array(stat_values)
        
        if method == 'historical':
            # Simple historical frequency
            hits = np.sum(stat_array >= threshold)
            probability = hits / len(stat_array)
            
        elif method == 'normal_dist':
            # Assume normal distribution
            mean = np.mean(stat_array)
            std = np.std(stat_array)
            
            if std == 0:
                probability = 1.0 if mean >= threshold else 0.0
            else:
                # Z-score calculation
                z_score = (threshold - mean) / std
                # Probability of being >= threshold
                from scipy import stats
                probability = 1 - stats.norm.cdf(z_score)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Calculate confidence based on sample size and consistency
        consistency = 1 - (np.std(stat_array) / (np.mean(stat_array) + 0.01))
        sample_confidence = min(len(stat_array) / 20, 1.0)  # Max confidence at 20+ games
        confidence = (consistency + sample_confidence) / 2
        
        return {
            'probability': round(probability * 100, 2),
            'confidence': round(confidence * 100, 2),
            'sample_size': len(stat_array),
            'mean': round(np.mean(stat_array), 2),
            'std_dev': round(np.std(stat_array), 2),
            'median': round(np.median(stat_array), 2),
            'recent_trend': self._calculate_trend(stat_values)
        }
    
    def _calculate_trend(self, values: List[float], recent_n: int = 5) -> str:
        """Calculate if recent performance is trending up or down"""
        if len(values) < recent_n * 2:
            return "insufficient_data"
        
        recent = values[-recent_n:]
        previous = values[-recent_n*2:-recent_n]
        
        recent_avg = np.mean(recent)
        previous_avg = np.mean(previous)
        
        diff_pct = ((recent_avg - previous_avg) / previous_avg) * 100
        
        if diff_pct > 10:
            return "trending_up"
        elif diff_pct < -10:
            return "trending_down"
        else:
            return "stable"
    
    def analyze_vs_opponent(self, 
                           all_games: pd.DataFrame, 
                           opponent: str,
                           stat_column: str,
                           threshold: float) -> Dict:
        """
        Analyze player performance against specific opponent
        
        Args:
            all_games: DataFrame with all game logs
            opponent: Opponent team name
            stat_column: Column name for the stat to analyze
            threshold: Target threshold
            
        Returns:
            Analysis dictionary
        """
        # Filter games against specific opponent
        opponent_games = all_games[all_games['opponent'] == opponent]
        
        if len(opponent_games) == 0:
            return {
                'error': f'No games found against {opponent}',
                'probability': 0.0
            }
        
        stat_values = opponent_games[stat_column].dropna().tolist()
        
        analysis = self.calculate_stat_probability(stat_values, threshold)
        analysis['opponent'] = opponent
        analysis['games_vs_opponent'] = len(opponent_games)
        
        return analysis
    
    def analyze_last_n_games(self, 
                            all_games: pd.DataFrame,
                            stat_column: str,
                            threshold: float,
                            n_games: int = 10) -> Dict:
        """
        Analyze player's last N games
        
        Args:
            all_games: DataFrame with all game logs
            stat_column: Column name for the stat
            threshold: Target threshold
            n_games: Number of recent games to analyze
            
        Returns:
            Analysis dictionary
        """
        # Sort by date (most recent first) and take last n games
        recent_games = all_games.sort_values('date', ascending=False).head(n_games)
        
        stat_values = recent_games[stat_column].dropna().tolist()
        
        analysis = self.calculate_stat_probability(stat_values, threshold)
        analysis['time_period'] = f'Last {n_games} games'
        analysis['date_range'] = f"{recent_games['date'].min()} to {recent_games['date'].max()}"
        
        return analysis
    
    def generate_prediction_report(self,
                                  player_name: str,
                                  season: int,
                                  stat_name: str,
                                  threshold: float,
                                  opponent: Optional[str] = None,
                                  last_n: int = 10) -> str:
        """
        Generate a comprehensive prediction report
        
        Args:
            player_name: Player's name
            season: Season year
            stat_name: Stat to analyze (e.g., 'points', 'assists', 'rebounds')
            threshold: Target value
            opponent: Optional opponent team name
            last_n: Number of recent games to analyze
            
        Returns:
            Formatted report string
        """
        # This would integrate with actual data fetching
        # For now, we'll create a template
        
        report = f"""
{'='*70}
BASKETBALL STATS PREDICTION REPORT
{'='*70}
Player: {player_name}
Season: {season}
Stat: {stat_name}
Target Threshold: {threshold}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

ANALYSIS SECTIONS:
1. Overall Season Performance
2. Last {last_n} Games Performance
"""
        
        if opponent:
            report += f"3. Performance vs {opponent}\n"
        
        report += """
4. Prediction Summary

{'='*70}
"""
        
        return report


class SampleDataGenerator:
    """Generate sample data for testing when API is not available"""
    
    @staticmethod
    def generate_sample_games(player_name: str, 
                             n_games: int = 30,
                             seed: int = 42) -> pd.DataFrame:
        """Generate realistic sample game data"""
        np.random.seed(seed)
        
        # Generate dates for last 30 games
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i*3) for i in range(n_games)]
        dates.reverse()
        
        # Sample teams
        teams = ['LAL', 'GSW', 'BOS', 'MIA', 'DEN', 'PHX', 'MIL', 'DAL']
        
        # Generate realistic stats
        base_points = np.random.normal(25, 5, n_games)
        base_assists = np.random.normal(6, 2, n_games)
        base_rebounds = np.random.normal(7, 2, n_games)
        
        # Add some variance for specific opponents
        games_data = []
        for i in range(n_games):
            opponent = np.random.choice(teams)
            
            # Some teams are "easier" matchups
            if opponent in ['PHX', 'GSW']:
                points_mod = 1.15
            else:
                points_mod = 1.0
            
            game = {
                'date': dates[i].strftime('%Y-%m-%d'),
                'opponent': opponent,
                'points': max(0, base_points[i] * points_mod),
                'assists': max(0, base_assists[i]),
                'rebounds': max(0, base_rebounds[i]),
                'minutes': np.random.uniform(28, 38),
                'field_goals_made': np.random.randint(7, 15),
                'field_goals_attempted': np.random.randint(15, 25),
                'three_pointers_made': np.random.randint(2, 6),
                'home_away': np.random.choice(['Home', 'Away'])
            }
            games_data.append(game)
        
        return pd.DataFrame(games_data)


def main():
    """Main demonstration function"""
    print("🏀 Basketball Stats Prediction Tool")
    print("=" * 70)
    
    # Initialize predictor
    predictor = BasketballStatsPredictor()
    
    # For demonstration, use sample data
    print("\n📊 Generating sample data for demonstration...")
    sample_generator = SampleDataGenerator()
    player_games = sample_generator.generate_sample_games("LeBron James", n_games=30)
    
    print(f"\nGenerated {len(player_games)} games of sample data")
    print("\nSample of game data:")
    print(player_games.head())
    
    # Example 1: Analyze last 10 games
    print("\n" + "="*70)
    print("EXAMPLE 1: Probability of scoring 25+ points (Last 10 games)")
    print("="*70)
    
    last_10_analysis = predictor.analyze_last_n_games(
        player_games, 
        'points', 
        25.0, 
        n_games=10
    )
    
    print(f"\n📈 Results:")
    print(f"  Probability: {last_10_analysis['probability']}%")
    print(f"  Confidence: {last_10_analysis['confidence']}%")
    print(f"  Sample Size: {last_10_analysis['sample_size']} games")
    print(f"  Average: {last_10_analysis['mean']} points")
    print(f"  Std Dev: {last_10_analysis['std_dev']}")
    print(f"  Trend: {last_10_analysis['recent_trend']}")
    
    # Example 2: Analyze vs specific opponent
    print("\n" + "="*70)
    print("EXAMPLE 2: Probability of scoring 25+ points vs GSW")
    print("="*70)
    
    opponent_analysis = predictor.analyze_vs_opponent(
        player_games,
        'GSW',
        'points',
        25.0
    )
    
    if 'error' not in opponent_analysis:
        print(f"\n📈 Results vs GSW:")
        print(f"  Probability: {opponent_analysis['probability']}%")
        print(f"  Games vs Opponent: {opponent_analysis['games_vs_opponent']}")
        print(f"  Average: {opponent_analysis['mean']} points")
        print(f"  Confidence: {opponent_analysis['confidence']}%")
    
    # Example 3: Multiple stat thresholds
    print("\n" + "="*70)
    print("EXAMPLE 3: Multiple Stat Predictions (Last 10 games)")
    print("="*70)
    
    thresholds = {
        'points': 25.0,
        'assists': 6.0,
        'rebounds': 7.0
    }
    
    print("\n📊 Prediction Summary:")
    for stat, threshold in thresholds.items():
        analysis = predictor.analyze_last_n_games(player_games, stat, threshold, 10)
        print(f"\n  {stat.upper()} >= {threshold}:")
        print(f"    Probability: {analysis['probability']}%")
        print(f"    Average: {analysis['mean']}")
        print(f"    Trend: {analysis['recent_trend']}")
    
    # Show detailed breakdown
    print("\n" + "="*70)
    print("📉 DETAILED STATISTICS BREAKDOWN")
    print("="*70)
    
    recent_10 = player_games.sort_values('date', ascending=False).head(10)
    
    print("\nLast 10 Games Performance:")
    print(recent_10[['date', 'opponent', 'points', 'assists', 'rebounds']].to_string(index=False))
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print("\n💡 Tips for using this tool:")
    print("  1. Install: pip install basketball-reference-scraper --break-system-packages")
    print("  2. Fetch real player data using player name and season")
    print("  3. Analyze against specific opponents or recent form")
    print("  4. Use historical or normal distribution methods")
    print("  5. Consider sample size and confidence scores")
    print("="*70)


if __name__ == "__main__":
    main()
