# Basketball Reference Integration Guide

## 🎯 Complete Guide to Using Real NBA Data

This guide shows you exactly how to integrate the basketball-reference-scraper library with your prediction tool to get **real, live NBA data**.

---

## Step 1: Install the Library

```bash
pip install basketball-reference-scraper --break-system-packages
```

This library scrapes data from [Basketball Reference](https://www.basketball-reference.com), the most comprehensive NBA statistics site.

---

## Step 2: Understand Basketball Reference Player IDs

Every player on Basketball Reference has a unique ID. For example:
- **LeBron James** → `jamesle01`
- **Stephen Curry** → `curryst01`
- **Luka Doncic** → `doncilu01`

You can find a player's ID from their Basketball Reference URL:
```
https://www.basketball-reference.com/players/j/jamesle01.html
                                                  └─────┬─────┘
                                                  Player ID
```

---

## Step 3: Three Ways to Get Data

### Method 1: Use the Integrated API (Easiest)

The `integrated_api.py` file automatically handles everything:

```python
from integrated_api import IntegratedPlayerStatsAPI

# Initialize - automatically uses real data if library is installed
api = IntegratedPlayerStatsAPI()

# Make predictions - it handles player ID lookup automatically
result = api.predict_stat(
    player_name="LeBron James",
    stat="points",
    threshold=25,
    last_n_games=10,
    season=2024
)

print(f"Probability: {result['probability']}%")
print(f"Data source: {result['data_source']}")
```

**Benefits:**
- ✅ Automatic fallback to sample data if library not installed
- ✅ Handles player ID lookup automatically
- ✅ Built-in rate limiting
- ✅ Standardizes column names

### Method 2: Use the Data Fetcher (More Control)

The `basketball_integration.py` file gives you direct access:

```python
from basketball_integration import RealDataFetcher

fetcher = RealDataFetcher()

# Method A: Search and fetch by name
games_df = fetcher.get_player_data_by_name(
    player_name="LeBron James",
    season=2024
)

# Method B: Fetch directly with player ID (faster)
games_df = fetcher.get_player_game_logs(
    player_identifier="jamesle01",
    season=2024
)

# Now use the DataFrame with your analysis
print(games_df[['date', 'opponent', 'points', 'assists', 'rebounds']].head())
```

### Method 3: Use Basketball Reference Client Directly (Most Control)

```python
from basketball_reference_web_scraper import client

# Get player game logs
games = client.regular_season_player_box_scores(
    player_identifier="jamesle01",
    season_end_year=2024
)

# Convert to DataFrame for analysis
import pandas as pd
df = pd.DataFrame(games)
```

---

## Step 4: Common Use Cases

### A. Get Last 10 Games for a Player

```python
from integrated_api import IntegratedPlayerStatsAPI

api = IntegratedPlayerStatsAPI()

result = api.predict_stat(
    player_name="Stephen Curry",
    stat="3pm",
    threshold=5,
    last_n_games=10,
    season=2024
)

print(f"In last 10 games:")
print(f"  Probability of 5+ threes: {result['probability']}%")
print(f"  Average: {result['average']} 3PM")
```

### B. Analyze Performance vs Specific Team

```python
result = api.predict_stat(
    player_name="Luka Doncic",
    stat="points",
    threshold=30,
    opponent="LAL",  # vs Lakers
    season=2024
)

print(f"vs Lakers: {result['probability']}% to score 30+")
```

### C. Get Full Season Data

```python
from basketball_integration import RealDataFetcher

fetcher = RealDataFetcher()

# Get all games for the season
full_season = fetcher.get_player_game_logs(
    player_identifier="jamesle01",
    season=2024
)

# Analyze
print(f"Total games: {len(full_season)}")
print(f"Season average: {full_season['points'].mean():.1f} PPG")
print(f"Best game: {full_season['points'].max():.0f} points")
```

### D. Compare Multiple Players

```python
from integrated_api import IntegratedPlayerStatsAPI

api = IntegratedPlayerStatsAPI()

players = [
    ("LeBron James", "jamesle01"),
    ("Kevin Durant", "duranke01"),
    ("Giannis Antetokounmpo", "antetgi01")
]

print("25+ Point Probability (Last 10 Games):\n")

for name, player_id in players:
    result = api.predict_stat(
        player_name=name,
        stat="points",
        threshold=25,
        last_n_games=10,
        player_id=player_id  # Speeds up lookup
    )
    
    if 'error' not in result:
        print(f"{name:25} {result['probability']:>5.1f}% ({result['average']:.1f} avg)")
```

---

## Step 5: Finding Player IDs

### Quick Reference of Common Players

```python
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
    "Trae Young": "youngtr01",
    "Ja Morant": "moranja01",
    "Donovan Mitchell": "mitchdo01",
    "Zion Williamson": "willizi01",
}
```

### Search for Any Player

```python
from basketball_reference_web_scraper import client

# Search for a player
results = client.search(term="Kawhi Leonard")

for player in results:
    print(f"{player['name']}: {player['identifier']}")
```

### Programmatic ID Generation (Rough Guess)

Basketball Reference IDs follow the pattern: `last5first2##`
- First 5 letters of last name
- First 2 letters of first name
- Number (usually 01)

```python
def guess_player_id(name):
    parts = name.lower().split()
    last = parts[-1][:5]
    first = parts[0][:2]
    return f"{last}{first}01"

print(guess_player_id("LeBron James"))  # "jamesle01" ✓
print(guess_player_id("Stephen Curry"))  # "curryst01" ✓
```

---

## Step 6: Available Data Fields

When you fetch game logs, you get these columns:

**Scoring:**
- `points` - Total points scored
- `made_field_goals` / `attempted_field_goals` - FG made/attempted
- `made_three_point_field_goals` - 3-pointers made (becomes `3pm`)
- `made_free_throws` / `attempted_free_throws` - FT made/attempted

**Rebounds & Assists:**
- `offensive_rebounds` - Offensive rebounds
- `defensive_rebounds` - Defensive rebounds  
- `assists` - Total assists

**Defense:**
- `steals` - Total steals
- `blocks` - Total blocks

**Other:**
- `turnovers` - Total turnovers
- `personal_fouls` - Personal fouls
- `seconds_played` - Playing time in seconds
- `date` - Game date
- `opponent` - Opponent team
- `location` - HOME or AWAY
- `outcome` - WIN or LOSS

---

## Step 7: Rate Limiting

Basketball Reference limits requests to **20 per minute**.

The integrated tools handle this automatically with 3-second delays:

```python
import time

# Built into the tools
time.sleep(3)  # Wait between API calls
```

If you make your own requests, add delays:

```python
from basketball_reference_web_scraper import client
import time

for season in [2022, 2023, 2024]:
    games = client.regular_season_player_box_scores(
        player_identifier="jamesle01",
        season_end_year=season
    )
    
    # Process games...
    
    time.sleep(3)  # Rate limiting
```

---

## Step 8: Error Handling

Always handle potential errors:

```python
from integrated_api import IntegratedPlayerStatsAPI

api = IntegratedPlayerStatsAPI()

result = api.predict_stat(
    player_name="Unknown Player",
    stat="points",
    threshold=25
)

if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"Probability: {result['probability']}%")
```

Common errors:
- Player not found
- No games in season
- Stat not available
- Network issues

---

## Step 9: Complete Working Example

Here's a complete script ready to run:

```python
#!/usr/bin/env python3
"""
Complete working example with real Basketball Reference data
"""

from integrated_api import IntegratedPlayerStatsAPI, print_prediction_report

def main():
    # Initialize API (uses real data if available)
    api = IntegratedPlayerStatsAPI()
    
    print("🏀 NBA Stats Predictor - Live Data\n")
    
    # Example 1: Tonight's betting props
    print("="*60)
    print("TONIGHT'S PROPS")
    print("="*60)
    
    props = [
        ("LeBron James", "jamesle01", "points", 25),
        ("Stephen Curry", "curryst01", "3pm", 5),
        ("Luka Doncic", "doncilu01", "assists", 8),
    ]
    
    for name, player_id, stat, threshold in props:
        result = api.predict_stat(
            player_name=name,
            player_id=player_id,
            stat=stat,
            threshold=threshold,
            last_n_games=10
        )
        
        if 'error' not in result:
            recommendation = "OVER" if result['probability'] >= 55 else "UNDER"
            print(f"\n{name} - {stat.upper()} {threshold}+")
            print(f"  Probability: {result['probability']}%")
            print(f"  Average: {result['average']}")
            print(f"  Recommendation: {recommendation}")
    
    # Example 2: Detailed analysis
    print("\n" + "="*60)
    print("DETAILED ANALYSIS")
    print("="*60)
    
    result = api.predict_stat(
        player_name="LeBron James",
        player_id="jamesle01",
        stat="points",
        threshold=25,
        last_n_games=10
    )
    
    print_prediction_report(result)

if __name__ == "__main__":
    main()
```

Save as `my_analysis.py` and run:
```bash
python3 my_analysis.py
```

---

## Step 10: Troubleshooting

### Issue: "No module named 'basketball_reference_web_scraper'"

**Solution:**
```bash
pip install basketball-reference-scraper --break-system-packages
```

### Issue: "No data found for player"

**Solutions:**
1. Check player name spelling
2. Verify they played in that season
3. Try with player ID directly
4. Check if they were active in the NBA

### Issue: "Too many requests"

**Solution:**
You hit the rate limit. Wait 60 seconds or add more delays:
```python
time.sleep(5)  # Increase delay between requests
```

### Issue: Player ID not working

**Solution:**
Search for the correct ID:
```python
from basketball_reference_web_scraper import client

results = client.search(term="Player Name")
print(results[0]['identifier'])
```

---

## Pro Tips

1. **Cache data locally** - Save game logs to CSV to avoid repeated API calls:
```python
games_df.to_csv('lebron_2024.csv', index=False)
games_df = pd.read_csv('lebron_2024.csv')
```

2. **Use player IDs** - Always pass `player_id` parameter to skip search step

3. **Batch requests** - Get all season data once, then analyze locally

4. **Season format** - Use season END year (2024 = 2023-24 season)

5. **Check for playoff data** separately using `playoff_player_box_scores`

---

## Next Steps

1. ✅ Install the library
2. ✅ Run `integrated_api.py` to test
3. ✅ Try predictions with real data
4. ✅ Build your own analysis scripts
5. ✅ Integrate with betting/fantasy workflows

---

**You're now ready to make predictions with real NBA data! 🏀📊**
