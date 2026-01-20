#!/usr/bin/env python3
"""
Basketball Reference Integration - Real Data Fetcher
Integrates with basketball-reference-scraper to get actual player stats
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import time


class RealDataFetcher:
    """
    Fetch real data from Basketball Reference
    Handles player identification and game log retrieval
    """
    
    def __init__(self):
        """Initialize with basketball-reference-scraper client"""
        try:
            from basketball_reference_web_scraper import client
            from basketball_reference_web_scraper.data import Team, OutputType
            self.client = client
            self.Team = Team
            self.OutputType = OutputType
            self.available = True
            print("✅ Basketball Reference scraper initialized")
        except ImportError:
            print("⚠️  basketball-reference-scraper not installed")
            print("Install with: pip install basketball-reference-scraper --break-system-packages")
            self.available = False
    
    def search_player(self, player_name: str) -> Optional[str]:
        """
        Search for a player and get their Basketball Reference ID
        
        Args:
            player_name: Player's full name (e.g., "LeBron James")
            
        Returns:
            Player identifier string (e.g., "jamesle01") or None
        """
        if not self.available:
            return None
        
        try:
            # Search for player
            results = self.client.search(term=player_name)
            
            if not results:
                print(f"❌ No results found for '{player_name}'")
                return None
            
            # Return the first match (usually most relevant)
            player_id = results[0]['identifier']
            print(f"✅ Found player: {results[0]['name']} (ID: {player_id})")
            return player_id
            
        except Exception as e:
            print(f"❌ Error searching for player: {e}")
            return None
    
    def get_player_game_logs(self, 
                            player_identifier: str, 
                            season: int,
                            playoffs: bool = False) -> pd.DataFrame:
        """
        Get game-by-game logs for a player
        
        Args:
            player_identifier: Basketball Reference player ID (e.g., "jamesle01")
            season: Season end year (e.g., 2024 for 2023-24 season)
            playoffs: If True, get playoff games instead of regular season
            
        Returns:
            DataFrame with game logs
        """
        if not self.available:
            return pd.DataFrame()
        
        try:
            print(f"📥 Fetching game logs for season {season}...")
            
            # Fetch game logs
            if playoffs:
                games = self.client.playoff_player_box_scores(
                    player_identifier=player_identifier,
                    season_end_year=season
                )
            else:
                games = self.client.regular_season_player_box_scores(
                    player_identifier=player_identifier,
                    season_end_year=season
                )
            
            if not games:
                print(f"❌ No game data found for season {season}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(games)
            
            # Standardize column names for our prediction tool
            column_mapping = {
                'date': 'date',
                'opponent': 'opponent',
                'made_field_goals': 'field_goals_made',
                'attempted_field_goals': 'field_goals_attempted',
                'made_three_point_field_goals': '3pm',
                'attempted_three_point_field_goals': '3pa',
                'made_free_throws': 'free_throws_made',
                'attempted_free_throws': 'free_throws_attempted',
                'offensive_rebounds': 'offensive_rebounds',
                'defensive_rebounds': 'defensive_rebounds',
                'assists': 'assists',
                'steals': 'steals',
                'blocks': 'blocks',
                'turnovers': 'turnovers',
                'personal_fouls': 'fouls',
                'points': 'points',
                'game_score': 'game_score',
                'seconds_played': 'seconds_played'
            }
            
            # Rename columns that exist
            df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
            
            # Calculate total rebounds if not present
            if 'rebounds' not in df.columns:
                if 'offensive_rebounds' in df.columns and 'defensive_rebounds' in df.columns:
                    df['rebounds'] = df['offensive_rebounds'] + df['defensive_rebounds']
            
            # Convert minutes from seconds if needed
            if 'seconds_played' in df.columns:
                df['minutes'] = df['seconds_played'] / 60
            
            # Format opponent names (remove 'Team.' prefix if present)
            if 'opponent' in df.columns:
                df['opponent'] = df['opponent'].apply(
                    lambda x: str(x).replace('Team.', '').replace('_', ' ').upper()
                )
            
            print(f"✅ Loaded {len(df)} games")
            
            # Respect rate limits (20 requests per minute)
            time.sleep(3)
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching game logs: {e}")
            return pd.DataFrame()
    
    def get_player_data_by_name(self, 
                                player_name: str, 
                                season: int,
                                playoffs: bool = False) -> pd.DataFrame:
        """
        Convenience method: Get player data by name (searches and fetches)
        
        Args:
            player_name: Player's full name
            season: Season end year
            playoffs: If True, get playoff games
            
        Returns:
            DataFrame with game logs
        """
        # Search for player ID
        player_id = self.search_player(player_name)
        
        if not player_id:
            return pd.DataFrame()
        
        # Get game logs
        return self.get_player_game_logs(player_id, season, playoffs)
    
    def get_season_averages(self, season: int) -> pd.DataFrame:
        """
        Get season totals/averages for all players
        
        Args:
            season: Season end year
            
        Returns:
            DataFrame with player season stats
        """
        if not self.available:
            return pd.DataFrame()
        
        try:
            print(f"📥 Fetching season totals for {season}...")
            
            players = self.client.players_season_totals(season_end_year=season)
            df = pd.DataFrame(players)
            
            print(f"✅ Loaded stats for {len(df)} players")
            
            time.sleep(3)  # Rate limiting
            
            return df
            
        except Exception as e:
            print(f"❌ Error fetching season totals: {e}")
            return pd.DataFrame()


def convert_player_name_to_id(name: str) -> str:
    """
    Helper to convert common player names to Basketball Reference IDs
    
    Args:
        name: Player's full name
        
    Returns:
        Best guess at player ID (format: last5first2##)
    """
    parts = name.lower().split()
    if len(parts) >= 2:
        last_name = parts[-1][:5]  # First 5 letters of last name
        first_name = parts[0][:2]  # First 2 letters of first name
        return f"{last_name}{first_name}01"
    return ""


# Example player IDs for quick reference
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
    "Kawhi Leonard": "leonaka01",
    "James Harden": "hardeja01",
    "Russell Westbrook": "westbru01",
    "Paul George": "georgpa01",
    "Jimmy Butler": "butleji01",
    "Devin Booker": "bookede01",
    "Kyrie Irving": "irvinky01",
    "Klay Thompson": "thompkl01",
    "Draymond Green": "greendr01",
    "Anthony Edwards": "edwaran01",
}


def example_usage():
    """Show how to use the real data fetcher"""
    
    print("="*70)
    print("🏀 BASKETBALL REFERENCE INTEGRATION EXAMPLE")
    print("="*70)
    
    # Initialize fetcher
    fetcher = RealDataFetcher()
    
    if not fetcher.available:
        print("\n❌ Cannot run example - library not installed")
        print("Install with: pip install basketball-reference-scraper --break-system-packages")
        return
    
    # Example 1: Get data by player name
    print("\n" + "="*70)
    print("EXAMPLE 1: Fetch LeBron James 2023-24 Season Data")
    print("="*70)
    
    player_name = "LeBron James"
    season = 2024  # 2023-24 season
    
    df = fetcher.get_player_data_by_name(player_name, season)
    
    if not df.empty:
        print(f"\n📊 Sample of game data:")
        print(df[['date', 'opponent', 'points', 'assists', 'rebounds']].head(10))
        
        print(f"\n📈 Season Summary:")
        print(f"  Games Played: {len(df)}")
        print(f"  Average Points: {df['points'].mean():.1f}")
        print(f"  Average Assists: {df['assists'].mean():.1f}")
        print(f"  Average Rebounds: {df['rebounds'].mean():.1f}")
    
    # Example 2: Use with prediction tool
    print("\n" + "="*70)
    print("EXAMPLE 2: Integrate with Prediction Tool")
    print("="*70)
    
    # Import our prediction tool
    from basketball_api import PlayerStatsAPI
    
    # Create a version that uses real data
    print("\n📊 Analyzing last 10 games...")
    
    if not df.empty:
        # Analyze last 10 games
        last_10 = df.sort_values('date', ascending=False).head(10)
        
        stat = 'points'
        threshold = 25
        
        stat_values = last_10[stat].values
        hits = np.sum(stat_values >= threshold)
        probability = (hits / len(stat_values)) * 100
        
        print(f"\n✅ Results for {player_name}:")
        print(f"  Stat: {stat} >= {threshold}")
        print(f"  Probability: {probability:.1f}%")
        print(f"  Average: {stat_values.mean():.1f}")
        print(f"  Hit {hits}/{len(stat_values)} times")
    
    # Example 3: Get season averages
    print("\n" + "="*70)
    print("EXAMPLE 3: Top Scorers in Season")
    print("="*70)
    
    season_stats = fetcher.get_season_averages(2024)
    
    if not season_stats.empty:
        # Calculate PPG (points per game)
        if 'games_played' in season_stats.columns and 'points' in season_stats.columns:
            season_stats['ppg'] = season_stats['points'] / season_stats['games_played']
            
            top_scorers = season_stats.nlargest(10, 'ppg')[['name', 'ppg', 'games_played']]
            print("\n🏆 Top 10 Scorers (PPG):")
            print(top_scorers.to_string(index=False))
    
    print("\n" + "="*70)
    print("✅ Integration Complete!")
    print("="*70)


if __name__ == "__main__":
    example_usage()
