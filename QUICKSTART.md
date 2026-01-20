# 🏀 Basketball Stats Predictor - Quick Start Guide

## What You Got

A complete Python tool for predicting NBA player performance probabilities using Basketball Reference data!

## Files Included

1. **basketball_api.py** - Main API with easy-to-use interface
2. **basketball_predictor.py** - Core prediction engine with advanced statistics
3. **examples.py** - 7 real-world usage scenarios
4. **README.md** - Comprehensive documentation
5. **requirements.txt** - Dependencies list
6. **QUICKSTART.md** - This file!

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install pandas numpy --break-system-packages

# Optional: For real Basketball Reference data
pip install basketball-reference-scraper --break-system-packages

# Optional: For advanced statistics
pip install scipy --break-system-packages
```

### Step 2: Run Your First Prediction
```bash
python3 basketball_api.py
```

This will show you example predictions with sample data!

### Step 3: Try Real-World Scenarios
```bash
python3 examples.py
```

See 7 different use cases including betting props, fantasy basketball, and matchup analysis.

## Most Common Use Cases

### 1. Will Player Score Over X Points?
```python
from basketball_api import PlayerStatsAPI

api = PlayerStatsAPI()
result = api.predict_stat(
    player_name="LeBron James",
    stat="points",
    threshold=25,
    last_n_games=10
)

print(f"Probability: {result['probability']}%")
```

### 2. Check Against Specific Opponent
```python
result = api.predict_stat(
    player_name="Stephen Curry",
    stat="3pm",
    threshold=5,
    opponent="LAL"
)
```

### 3. Compare Multiple Teams
```python
comparison = api.compare_opponents(
    player_name="Luka Doncic",
    stat="points",
    threshold=30,
    opponents=['LAL', 'GSW', 'BOS']
)

print(comparison)
```

## Understanding Your Results

### Probability
The % chance the player hits the threshold based on past games.
- **70%+**: Very likely
- **50-70%**: Moderate chance
- **Below 50%**: Unlikely

### Confidence Score
How reliable the prediction is.
- **70%+**: High confidence (consistent performance, good sample size)
- **50-70%**: Medium confidence
- **Below 50%**: Low confidence (inconsistent or small sample)

### Trend
Recent performance direction:
- **📈 Trending Up**: Hot streak (10%+ better recently)
- **📉 Trending Down**: Cold streak (10%+ worse recently)
- **➡️ Stable**: Consistent performance

## Pro Tips

1. **More games = Better predictions**
   - Use 10+ games for reliable predictions
   - Full season data is most accurate

2. **Check the trend**
   - A player trending up is more likely to exceed average
   - Consider recent form over season averages

3. **Matchups matter**
   - Always check head-to-head history
   - Some players perform better against certain teams

4. **Look at confidence**
   - Don't bet on low confidence predictions
   - High variance players are harder to predict

5. **Combine with other factors**
   - Injuries, rest days, back-to-backs
   - Home vs away
   - Pace of opponent

## Real Data vs Sample Data

By default, the tool uses **sample data** for demonstration.

To use **real Basketball Reference data**:
1. Install: `pip install basketball-reference-scraper --break-system-packages`
2. Enable in code: `api = PlayerStatsAPI(use_real_data=True)`

## Example Workflows

### Sports Betting Props
```python
# Analyze tonight's props
props = [
    ("LeBron James", "points", 25.5),
    ("Stephen Curry", "3pm", 4.5),
    ("Luka Doncic", "assists", 8.5)
]

for player, stat, line in props:
    result = api.predict_stat(player, stat, line, last_n_games=10)
    rec = "OVER" if result['probability'] >= 55 else "UNDER"
    print(f"{player} {stat} {line}: {rec} ({result['probability']}%)")
```

### Fantasy Basketball
```python
# Who should I start?
players = ["LeBron James", "Kevin Durant"]

for player in players:
    result = api.predict_stat(player, "points", 25, last_n_games=10)
    print(f"{player}: {result['average']} avg (trend: {result['trend']})")
```

### Find Best Matchups
```python
# Which opponent is easiest for this player?
teams = ['LAL', 'GSW', 'BOS', 'MIA', 'DEN']
comparison = api.compare_opponents("Luka Doncic", "points", 30, teams)
print("Best matchups:")
print(comparison.head(3))
```

## Common Issues

### "No module named 'pandas'"
```bash
pip install pandas numpy --break-system-packages
```

### "No data found for player"
- Check spelling of player name
- Verify season year is correct
- Try with sample data first to test functionality

### Want more features?
The code is fully customizable! Check the documentation in README.md for:
- Custom statistical methods
- Advanced filtering
- Visualization options
- ML integration possibilities

## Next Steps

1. ✅ Run the demo: `python3 basketball_api.py`
2. ✅ Try examples: `python3 examples.py`
3. ✅ Read full docs: Check `README.md`
4. ✅ Customize for your needs
5. ✅ Install real data source for production use

## Get Help

1. Check `README.md` for detailed documentation
2. Look at `examples.py` for more use cases
3. Review the code comments in the .py files

## What This Tool Does

✅ Calculates probability of hitting stat thresholds
✅ Analyzes recent form (last N games)
✅ Compares performance vs specific opponents
✅ Detects hot/cold streaks
✅ Provides confidence scores
✅ Shows historical hit rates
✅ Tracks trends over time

## What This Tool Doesn't Do

❌ Account for injuries or rest
❌ Consider game pace or defensive matchups
❌ Predict exact stat values
❌ Guarantee outcomes (use responsibly!)

---

**Ready to make data-driven basketball predictions! 🏀📊**

Have fun and bet responsibly!
