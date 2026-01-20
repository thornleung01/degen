#!/usr/bin/env python3
"""
Real-world usage examples for the Basketball Stats Prediction Tool
Common scenarios for sports betting, fantasy, and analysis
"""

from basketball_api import PlayerStatsAPI, print_prediction_report


def betting_scenario():
    """Example: Sports betting prop analysis"""
    print("\n" + "="*70)
    print("SCENARIO 1: SPORTS BETTING PROP ANALYSIS")
    print("="*70)
    print("\nTonight's Props to Analyze:")
    print("- LeBron James Over 25.5 Points")
    print("- Stephen Curry Over 4.5 Three-Pointers")
    print("- Luka Doncic Over 28.5 Points")
    
    api = PlayerStatsAPI()
    
    props = [
        ("LeBron James", "points", 25.5),
        ("Stephen Curry", "3pm", 4.5),
        ("Luka Doncic", "points", 28.5)
    ]
    
    print("\n📊 Analysis (based on last 10 games):\n")
    
    for player, stat, line in props:
        result = api.predict_stat(player, stat, line, last_n_games=10)
        
        if 'error' not in result:
            recommendation = "✅ OVER" if result['probability'] >= 55 else "❌ UNDER"
            confidence_level = "HIGH" if result['confidence'] >= 70 else "MEDIUM" if result['confidence'] >= 50 else "LOW"
            
            print(f"{player} - {stat.upper()} O/U {line}")
            print(f"  Probability: {result['probability']}%")
            print(f"  Average: {result['average']}")
            print(f"  Trend: {result['trend']}")
            print(f"  Confidence: {confidence_level} ({result['confidence']}%)")
            print(f"  → Recommendation: {recommendation}\n")


def fantasy_scenario():
    """Example: Fantasy basketball lineup decisions"""
    print("\n" + "="*70)
    print("SCENARIO 2: FANTASY BASKETBALL - WHO TO START?")
    print("="*70)
    print("\nYou need to choose between two players for your lineup:")
    
    api = PlayerStatsAPI()
    
    players = [
        ("LeBron James", "points"),
        ("Luka Doncic", "points")
    ]
    
    print("\n📊 Comparison (last 10 games):\n")
    
    for player, stat in players:
        result = api.predict_stat(player, stat, 25, last_n_games=10)
        
        if 'error' not in result:
            print(f"{player}:")
            print(f"  Average: {result['average']} {stat}")
            print(f"  Consistency: {100 - result['std_dev']:.1f}%")
            print(f"  Trend: {result['trend']}")
            print(f"  Ceiling: {result['max']}")
            print(f"  Floor: {result['min']}\n")


def matchup_scenario():
    """Example: Analyzing player vs specific opponent"""
    print("\n" + "="*70)
    print("SCENARIO 3: MATCHUP ANALYSIS")
    print("="*70)
    print("\nStephen Curry faces the Lakers tonight.")
    print("How does he historically perform against them?")
    
    api = PlayerStatsAPI()
    
    result = api.predict_stat(
        "Stephen Curry",
        "points",
        25,
        opponent="LAL"
    )
    
    print_prediction_report(result)


def hot_streak_scenario():
    """Example: Detecting hot/cold streaks"""
    print("\n" + "="*70)
    print("SCENARIO 4: HOT STREAK DETECTION")
    print("="*70)
    print("\nIs LeBron James on a hot streak?")
    
    api = PlayerStatsAPI()
    
    # Compare different time windows
    windows = [3, 5, 10]
    
    print("\n📈 Recent Performance Analysis:\n")
    
    for window in windows:
        result = api.predict_stat(
            "LeBron James",
            "points",
            25,
            last_n_games=window
        )
        
        if 'error' not in result:
            print(f"Last {window} games:")
            print(f"  Average: {result['average']} pts")
            print(f"  Hit rate (25+): {result['probability']}%")
            print(f"  Trend: {result['trend']}\n")


def multi_stat_parlay():
    """Example: Multi-stat same game parlay"""
    print("\n" + "="*70)
    print("SCENARIO 5: SAME GAME PARLAY")
    print("="*70)
    print("\nAnalyzing a 3-leg parlay for LeBron James:")
    print("- 25+ Points")
    print("- 7+ Assists")
    print("- 8+ Rebounds")
    
    api = PlayerStatsAPI()
    
    legs = [
        ("points", 25),
        ("assists", 7),
        ("rebounds", 8)
    ]
    
    print("\n📊 Individual Leg Analysis:\n")
    
    probabilities = []
    for stat, threshold in legs:
        result = api.predict_stat(
            "LeBron James",
            stat,
            threshold,
            last_n_games=10
        )
        
        if 'error' not in result:
            prob = result['probability']
            probabilities.append(prob / 100)
            
            print(f"{stat.upper()} {threshold}+:")
            print(f"  Probability: {prob}%")
            print(f"  Average: {result['average']}")
            print(f"  Trend: {result['trend']}\n")
    
    # Calculate parlay probability (independent events)
    parlay_prob = 1
    for p in probabilities:
        parlay_prob *= p
    parlay_prob *= 100
    
    print(f"{'='*70}")
    print(f"🎯 COMBINED PARLAY PROBABILITY: {parlay_prob:.1f}%")
    print(f"{'='*70}")
    
    if parlay_prob >= 30:
        print("✅ This parlay has reasonable odds!")
    elif parlay_prob >= 15:
        print("⚠️  This parlay is risky but possible")
    else:
        print("❌ This parlay is very unlikely to hit")


def opponent_comparison():
    """Example: Finding best matchups"""
    print("\n" + "="*70)
    print("SCENARIO 6: FINDING FAVORABLE MATCHUPS")
    print("="*70)
    print("\nWhich teams does Luka Doncic score most against?")
    
    api = PlayerStatsAPI()
    
    teams = ['LAL', 'GSW', 'BOS', 'MIA', 'DEN', 'PHX']
    
    comparison = api.compare_opponents(
        "Luka Doncic",
        "points",
        30,
        teams
    )
    
    print("\n📊 Scoring 30+ Points by Opponent:\n")
    print(comparison.to_string(index=False))
    
    print("\n💡 Insights:")
    best_matchup = comparison.iloc[0]
    worst_matchup = comparison.iloc[-1]
    
    print(f"  • Best Matchup: {best_matchup['opponent']} ({best_matchup['probability']}% chance)")
    print(f"  • Worst Matchup: {worst_matchup['opponent']} ({worst_matchup['probability']}% chance)")


def live_game_decision():
    """Example: In-game betting decision"""
    print("\n" + "="*70)
    print("SCENARIO 7: LIVE BETTING DECISION")
    print("="*70)
    print("\nIt's halftime, and LeBron has 10 points.")
    print("Live bet: Will he finish with 25+ points?")
    
    api = PlayerStatsAPI()
    
    # Analyze his typical second half performance
    result = api.predict_stat(
        "LeBron James",
        "points",
        25,
        last_n_games=10
    )
    
    if 'error' not in result:
        print(f"\n📊 Analysis:")
        print(f"  • Average per game: {result['average']} pts")
        print(f"  • Current: 10 pts at halftime")
        print(f"  • Needs: 15 more pts in 2nd half")
        
        # Rough estimate: assume ~55% of points in 2nd half typically
        estimated_2nd_half = result['average'] * 0.55
        
        print(f"  • Typical 2nd half: ~{estimated_2nd_half:.1f} pts")
        print(f"\n💡 Decision:")
        
        if estimated_2nd_half >= 15:
            print("  ✅ He typically scores enough in the 2nd half. Consider the OVER.")
        else:
            print("  ❌ He'd need an above-average 2nd half. Consider the UNDER.")


def main():
    """Run all scenarios"""
    
    print("="*70)
    print("🏀 BASKETBALL PREDICTION TOOL - REAL-WORLD SCENARIOS")
    print("="*70)
    print("\nNote: Using sample data for demonstration")
    print("Install basketball-reference-scraper for real data")
    
    scenarios = [
        ("Betting Props", betting_scenario),
        ("Fantasy Lineup", fantasy_scenario),
        ("Matchup Analysis", matchup_scenario),
        ("Hot Streak Detection", hot_streak_scenario),
        ("Same Game Parlay", multi_stat_parlay),
        ("Opponent Comparison", opponent_comparison),
        ("Live Betting", live_game_decision)
    ]
    
    print("\n📋 Available Scenarios:")
    for i, (name, _) in enumerate(scenarios, 1):
        print(f"  {i}. {name}")
    
    print("\n" + "="*70)
    print("Running all scenarios...")
    print("="*70)
    
    for name, func in scenarios:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    print("\n" + "="*70)
    print("✅ All scenarios complete!")
    print("="*70)
    print("\n💡 Next Steps:")
    print("  1. Install real data: pip install basketball-reference-scraper --break-system-packages")
    print("  2. Modify scenarios for your use case")
    print("  3. Add your own custom analysis")
    print("  4. Integrate with live data feeds")


if __name__ == "__main__":
    main()
