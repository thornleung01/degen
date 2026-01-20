# Using Basketball Predictor with Claude Code

## 🤖 Complete Guide for Claude Code Integration

Claude Code is a command-line AI coding assistant. Here's how to use your Basketball Predictor with it.

---

## Method 1: Start a New Project with Claude Code

### Step 1: Set Up Your Project

```bash
# Create a project directory
mkdir nba-predictor
cd nba-predictor

# Copy all your files
cp /path/to/downloads/*.py .
cp /path/to/downloads/*.md .
cp /path/to/downloads/requirements.txt .

# Install dependencies
pip install -r requirements.txt --break-system-packages
```

### Step 2: Start Claude Code

```bash
# Start Claude Code in your project directory
claude code
```

### Step 3: Give Claude Code Context

When Claude Code starts, paste this message:

```
I have a basketball stats prediction tool that integrates with Basketball Reference API. 

Key files:
- integrated_api.py: Main API (uses real Basketball Reference data)
- basketball_integration.py: Data fetcher module
- examples.py: Real-world usage examples

The tool can:
1. Predict probability of players hitting stat thresholds (e.g., 25+ points)
2. Analyze performance vs specific opponents
3. Track trends over last N games
4. Compare multiple players
5. Generate betting/fantasy recommendations

Please help me [YOUR TASK HERE]

Relevant docs are in README.md and INTEGRATION_GUIDE.md
```

---

## Method 2: Ask Claude Code to Extend the Tool

### Common Tasks for Claude Code

#### Task 1: Add New Features

```bash
claude code
```

Then ask:
```
Using the Basketball Predictor in this directory:

Add a feature that analyzes a player's home vs away splits and 
calculates separate probabilities for each. The function should:

1. Take player_name, stat, threshold, season
2. Fetch their game logs
3. Separate into home/away games
4. Calculate probability for each
5. Return comparison

Use the existing integrated_api.py structure.
```

#### Task 2: Create Custom Analysis Scripts

```
Create a script called "tonights_props.py" that:

1. Takes a list of props (player, stat, line) from command line or config file
2. Uses integrated_api.py to analyze each prop
3. Generates recommendations (OVER/UNDER) based on 55% probability threshold
4. Outputs a formatted report with:
   - Player name
   - Prop details
   - Probability %
   - Confidence score
   - Trend
   - Recommendation
5. Saves results to CSV

The script should be production-ready and handle errors gracefully.
```

#### Task 3: Build a Web Interface

```
Using the Basketball Predictor API (integrated_api.py), create a simple 
Flask web app that:

1. Has a form with fields: player name, stat, threshold, # of games
2. Calls the prediction API
3. Displays results in a nice HTML page with:
   - Probability gauge/chart
   - Recent game stats table
   - Trend indicator
   - Confidence score
4. Includes CSS styling

Keep it simple and functional.
```

#### Task 4: Add Database Caching

```
Modify basketball_integration.py to add SQLite database caching:

1. Store fetched game logs in a local SQLite database
2. Check database first before calling Basketball Reference API
3. Only fetch new games since last update
4. Add a --force-refresh flag to bypass cache
5. Respect the 3-second rate limiting

Maintain backward compatibility with existing code.
```

#### Task 5: Create CLI Tool

```
Create a command-line tool "nba-predict" that uses the Basketball Predictor:

Usage examples:
  nba-predict lebron-james points 25 --last 10
  nba-predict "Stephen Curry" 3pm 5 --opponent LAL
  nba-predict luka-doncic --multi points:30,assists:8,rebounds:9

Features:
- Parse player names flexibly
- Support multiple stats at once
- Pretty formatted output
- Color-coded recommendations
- Save to file option

Use click or argparse for argument parsing.
```

---

## Method 3: Provide Full Context Files

### Create a Context File for Claude Code

Create `CLAUDE_CONTEXT.md`:

```markdown
# Basketball Stats Predictor - Context for Claude Code

## Project Overview
NBA player performance prediction tool that uses Basketball Reference data to calculate probabilities of hitting stat thresholds.

## Architecture

### Core Components
1. **integrated_api.py** - Main API class
   - IntegratedPlayerStatsAPI: Main interface
   - Automatically fetches real data from Basketball Reference
   - Falls back to sample data if library unavailable

2. **basketball_integration.py** - Data fetching
   - RealDataFetcher: Handles Basketball Reference API
   - Player search and ID lookup
   - Game log retrieval with rate limiting

3. **basketball_predictor.py** - Statistics engine
   - BasketballStatsPredictor: Probability calculations
   - Trend analysis
   - Confidence scoring

### Key Functions

#### predict_stat()
```python
api.predict_stat(
    player_name: str,
    stat: str,  # 'points', 'assists', 'rebounds', etc.
    threshold: float,
    opponent: Optional[str] = None,
    last_n_games: Optional[int] = None,
    season: int = 2024,
    player_id: Optional[str] = None
) -> Dict
```

Returns:
- probability: % chance of hitting threshold
- confidence: reliability score
- average, median, std_dev: statistics
- trend: up/down/stable
- sample_size: games analyzed

## Available Stats
- points
- assists
- rebounds
- steals
- blocks
- 3pm (three-pointers made)

## Player ID Format
Basketball Reference uses format: last5first2##
Examples:
- LeBron James: jamesle01
- Stephen Curry: curryst01

## Rate Limits
Basketball Reference: 20 requests/minute (3-second delays built in)

## Dependencies
- pandas: Data manipulation
- numpy: Statistical calculations
- basketball-reference-scraper: API access

## Common Patterns

### Basic Prediction
```python
from integrated_api import IntegratedPlayerStatsAPI
api = IntegratedPlayerStatsAPI()
result = api.predict_stat("LeBron James", "points", 25, last_n_games=10)
```

### Opponent Analysis
```python
result = api.predict_stat("Stephen Curry", "3pm", 5, opponent="LAL")
```

### Multi-Stat Analysis
```python
stats = [('points', 25), ('assists', 7), ('rebounds', 8)]
for stat, threshold in stats:
    result = api.predict_stat(player, stat, threshold)
```

## Extension Points
- Add more statistical methods in basketball_predictor.py
- Implement new data sources in basketball_integration.py
- Create visualization functions
- Add database caching
- Build web/CLI interfaces

## Error Handling
All API calls return dicts with 'error' key on failure:
```python
if 'error' in result:
    print(f"Error: {result['error']}")
```
```

Save this file in your project directory.

---

## Method 4: Interactive Development with Claude Code

### Start an Interactive Session

```bash
cd nba-predictor
claude code --interactive
```

### Example Conversation Flow

**You:**
```
I want to build a feature that analyzes a player's performance 
in clutch situations (4th quarter, close games). Can you help me 
extend the basketball_integration.py to filter for these games?
```

**Claude Code will:**
1. Read your files
2. Understand the structure
3. Propose a solution
4. Write the code
5. Test it
6. Iterate based on your feedback

**You can then say:**
```
Great! Now add a function to the integrated_api.py that uses this 
clutch game filtering to calculate clutch-specific probabilities.
```

**Claude Code will:**
1. Integrate with existing API
2. Maintain consistent interfaces
3. Add appropriate error handling
4. Update with new functionality

---

## Method 5: Specific Request Templates

### Template 1: Add Data Source
```
I want to add [DATA SOURCE NAME] as an alternative to Basketball Reference.

Requirements:
1. Create a new fetcher class in basketball_integration.py
2. Follow the same interface as RealDataFetcher
3. Make it selectable via a parameter in IntegratedPlayerStatsAPI
4. Add documentation in INTEGRATION_GUIDE.md

The API endpoint is [URL] and returns [FORMAT].
Authentication: [METHOD]
```

### Template 2: Optimize Performance
```
The tool is slow when analyzing many players. Please optimize:

1. Add connection pooling for API requests
2. Implement parallel fetching for multiple players
3. Add Redis caching option (in addition to in-memory)
4. Profile the code and identify bottlenecks

Maintain backward compatibility and update documentation.
```

### Template 3: Add Testing
```
Create a comprehensive test suite for the Basketball Predictor:

1. Unit tests for prediction calculations
2. Integration tests for API calls (with mocking)
3. Test edge cases (missing data, invalid inputs)
4. Add pytest configuration
5. Create tests/README.md with instructions

Use pytest and include fixtures for sample data.
```

### Template 4: Build Dashboard
```
Create an interactive dashboard using Streamlit:

1. Sidebar: Select player, stat, threshold, time period
2. Main panel: 
   - Probability gauge
   - Trend chart over time
   - Recent games table
   - Hit rate visualization
3. Comparison mode: Compare 2-3 players side-by-side
4. Export results to PDF

Use the existing integrated_api.py - don't modify core files.
```

---

## Best Practices for Claude Code

### 1. Be Specific About Scope
❌ "Make this better"
✅ "Add error handling for network timeouts in basketball_integration.py"

### 2. Reference Existing Code
❌ "Create a new feature"
✅ "Using the pattern in integrated_api.predict_stat(), add a similar method for team statistics"

### 3. Specify Constraints
```
Add this feature BUT:
- Don't modify existing function signatures
- Maintain the current return format
- Keep backward compatibility
- Add docstrings in the same style
```

### 4. Request Documentation
```
After implementing this feature:
1. Update the README.md usage section
2. Add an example to examples.py
3. Update INTEGRATION_GUIDE.md if it affects the API
```

### 5. Ask for Testing
```
Also create a test script that demonstrates:
- Normal usage
- Edge cases
- Error scenarios
Make it runnable with: python test_new_feature.py
```

---

## Common Claude Code Requests

### Quick Fixes
```
Fix the bug in integrated_api.py line 145 where it fails when 
opponent is None. Add proper None checking.
```

### New Features
```
Add a function to calculate rolling averages over different 
window sizes (3, 5, 10 games) and plot them with matplotlib.
```

### Refactoring
```
Refactor basketball_integration.py to separate concerns:
- One class for API communication
- One class for data transformation
- One class for caching
Maintain the same external interface.
```

### Documentation
```
The INTEGRATION_GUIDE.md is outdated. Update it to reflect 
the new caching feature we just added. Include examples.
```

---

## Project Structure for Claude Code

Organize your project like this:

```
nba-predictor/
├── README.md                      # Main documentation
├── CLAUDE_CONTEXT.md             # Context for Claude Code
├── requirements.txt               # Dependencies
├── integrated_api.py             # Main API
├── basketball_integration.py     # Data fetching
├── basketball_predictor.py       # Statistics
├── examples.py                    # Usage examples
├── config.py                      # Configuration (NEW)
├── tests/                         # Test suite (NEW)
│   ├── test_api.py
│   ├── test_integration.py
│   └── test_predictions.py
├── scripts/                       # Utility scripts (NEW)
│   ├── analyze_props.py
│   ├── compare_players.py
│   └── export_data.py
└── docs/                          # Documentation
    ├── INTEGRATION_GUIDE.md
    ├── QUICKSTART.md
    └── API_REFERENCE.md
```

---

## Example: Complete Claude Code Session

```bash
cd nba-predictor
claude code
```

**Initial message:**
```
I'm working on an NBA prediction tool. Files are in current directory.

Project context:
- integrated_api.py: Main prediction API
- Uses Basketball Reference for real data
- Can analyze player performance and calculate probabilities

I need help with 3 tasks:

1. Create a config.py file for managing:
   - API keys (future use)
   - Rate limiting settings
   - Cache settings
   - Default parameters

2. Add a compare_players.py script that:
   - Takes 2+ player names
   - Compares their probability for same stat/threshold
   - Shows side-by-side stats
   - Recommends who to start/bet on

3. Update examples.py to include the new comparison feature

Let's start with task 1. Please create a well-structured config.py.
```

Claude Code will then:
1. Read your files
2. Understand the structure
3. Create config.py
4. Wait for your approval
5. Move to next task

**You continue:**
```
Good! Now let's do task 2. The comparison script should 
use the config.py settings and format output nicely.
```

And so on...

---

## Pro Tips

1. **Keep context files updated** - Update CLAUDE_CONTEXT.md as project grows

2. **Use relative references** - "Using the pattern in integrated_api.py line 50..."

3. **Request iterative changes** - Break big tasks into steps

4. **Ask for explanations** - "Explain how this new caching system works"

5. **Validate before moving on** - "Let's test this before adding more features"

---

## Summary

**To use with Claude Code:**

1. Copy all files to a project directory
2. Create CLAUDE_CONTEXT.md (or use the one above)
3. Start: `claude code`
4. Give clear, specific instructions
5. Reference existing files and patterns
6. Iterate based on results

Claude Code excels at:
- Adding new features to existing code
- Refactoring and optimization
- Creating test suites
- Building interfaces (CLI, web, etc.)
- Documentation updates

**You're ready to supercharge your Basketball Predictor with Claude Code! 🚀**
