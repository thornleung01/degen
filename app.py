#!/usr/bin/env python3
"""
Basketball Stats Prediction Web Application
Flask backend for the basketball prediction tool
"""

from flask import Flask, render_template, request, jsonify
from integrated_api import IntegratedPlayerStatsAPI, COMMON_PLAYERS
import traceback

app = Flask(__name__)

# Initialize the API once at startup
api = IntegratedPlayerStatsAPI(prefer_real_data=True)

# Extended player list for autocomplete
PLAYER_LIST = list(COMMON_PLAYERS.keys()) + [
    "Ja Morant",
    "Devin Booker",
    "Trae Young",
    "Donovan Mitchell",
    "Kyrie Irving",
    "James Harden",
    "Paul George",
    "Kawhi Leonard",
    "Jimmy Butler",
    "Bam Adebayo",
    "Tyrese Haliburton",
    "De'Aaron Fox",
    "Shai Gilgeous-Alexander",
    "Anthony Edwards",
    "Karl-Anthony Towns",
    "Zion Williamson",
    "Brandon Ingram",
    "Pascal Siakam",
    "Scottie Barnes",
    "Cade Cunningham",
    "LaMelo Ball",
    "Darius Garland",
    "Evan Mobley",
    "Jaren Jackson Jr",
    "Desmond Bane",
    "Tyler Herro",
    "Jalen Brunson",
    "Julius Randle",
    "RJ Barrett",
    "Mikal Bridges",
    "Deandre Ayton",
    "Chris Paul",
    "Bradley Beal",
    "Lauri Markkanen",
    "Paolo Banchero",
    "Franz Wagner",
    "Victor Wembanyama",
]

# Stat type mappings
STAT_TYPES = {
    'points': 'Points',
    'assists': 'Assists',
    'rebounds': 'Rebounds',
    'steals': 'Steals',
    'blocks': 'Blocks',
    '3pm': '3-Pointers Made'
}


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html',
                         stat_types=STAT_TYPES,
                         players=PLAYER_LIST)


@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle prediction requests

    Expects JSON or form data with:
    - player: Player name
    - stat: Stat type (points, assists, rebounds, steals, blocks, 3pm)
    - threshold: Target threshold value
    - games: Number of games to analyze (optional)
    - opponent: Opponent filter (optional)
    """
    try:
        # Get data from request (support both JSON and form data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        # Validate required fields
        player = data.get('player', '').strip()
        stat = data.get('stat', '').strip()
        threshold = data.get('threshold')

        if not player:
            return jsonify({'error': 'Player name is required'}), 400
        if not stat:
            return jsonify({'error': 'Stat type is required'}), 400
        if threshold is None or threshold == '':
            return jsonify({'error': 'Threshold value is required'}), 400

        try:
            threshold = float(threshold)
        except ValueError:
            return jsonify({'error': 'Threshold must be a valid number'}), 400

        # Parse optional fields
        games = data.get('games', '')
        last_n_games = None
        if games and games != 'full':
            try:
                last_n_games = int(games)
            except ValueError:
                pass

        opponent = data.get('opponent', '').strip() or None

        # Get player ID if available for faster lookup
        player_id = COMMON_PLAYERS.get(player)

        # Call the prediction API
        result = api.predict_stat(
            player_name=player,
            stat=stat,
            threshold=threshold,
            opponent=opponent,
            last_n_games=last_n_games,
            player_id=player_id
        )

        # Add recommendation based on probability
        if 'error' not in result:
            prob = result['probability']
            if prob >= 55:
                result['recommendation'] = 'BET OVER'
                result['recommendation_class'] = 'success'
            elif prob <= 45:
                result['recommendation'] = 'BET UNDER'
                result['recommendation_class'] = 'danger'
            else:
                result['recommendation'] = 'TOSS UP'
                result['recommendation_class'] = 'warning'

            # Add color class for probability display
            if prob >= 60:
                result['prob_class'] = 'success'
            elif prob >= 40:
                result['prob_class'] = 'warning'
            else:
                result['prob_class'] = 'danger'

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': f'An error occurred: {str(e)}',
            'details': traceback.format_exc()
        }), 500


@app.route('/search', methods=['GET'])
def search_players():
    """
    Search for players by name for autocomplete

    Query params:
    - q: Search query
    """
    query = request.args.get('q', '').strip().lower()

    if not query:
        return jsonify([])

    # Filter players that match the query
    matches = [
        player for player in PLAYER_LIST
        if query in player.lower()
    ]

    # Sort by relevance (starts with query first, then contains)
    matches.sort(key=lambda x: (
        0 if x.lower().startswith(query) else 1,
        x.lower().find(query),
        x
    ))

    # Limit results
    return jsonify(matches[:10])


@app.route('/players', methods=['GET'])
def get_all_players():
    """Return all available players for initial load"""
    return jsonify(sorted(PLAYER_LIST))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_mode': 'real_data' if api.use_real_data else 'sample_data'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Basketball Stats Prediction Web App")
    print("=" * 60)
    print(f"API Mode: {'Real Data' if api.use_real_data else 'Sample Data'}")
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
