import sqlite3, uuid, json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            game_type TEXT NOT NULL,
            variant TEXT,
            players TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'active',
            data TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            round_number INTEGER,
            player_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            bid TEXT,
            made_bid BOOLEAN,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_game_variants(game_type):
    variants_map = {
        'bridge': [
            {'id': 'draw', 'name': 'Draw Bridge', 'description': 'Two-player with card drawing phase'},
            {'id': 'draw_discard', 'name': 'Draw and Discard', 'description': 'Choose to take or discard from stock'},
            {'id': 'double_dummy', 'name': 'Double Dummy', 'description': 'Four hands, two dummies exposed'},
            {'id': 'single_dummy', 'name': 'Single Dummy', 'description': 'One dummy exposed before bidding'},
            {'id': 'memory', 'name': 'Memory Bridge', 'description': 'No replacement cards, memory challenge'}
        ],
        'rummy': [
            {'id': 'basic', 'name': 'Basic Rummy', 'description': 'Classic rummy rules'},
            {'id': 'gin', 'name': 'Gin Rummy', 'description': 'Two-player gin rummy'},
            {'id': 'oklahoma', 'name': 'Oklahoma Rummy', 'description': 'Gin rummy with wild card'}
        ],
        'canasta': [
            {'id': 'classic', 'name': 'Classic Canasta', 'description': 'Traditional four-player partnership'}
        ]
    }
    return variants_map.get(game_type, [{'id': 'basic', 'name': 'Standard', 'description': 'Standard rules'}])

def get_game_config(game_type, variant):
    configs = {
        'bridge': {
            'draw': {
                'name': 'Draw Bridge',
                'rules_url': 'https://www.pagat.com/auctionwhist/honeymoon.html#draw',
                'quick_tips': [
                    'First 13 tricks at no trump - no need to follow suit',
                    'Winner draws first card, loser draws second',
                    'After drawing phase, bid like contract bridge',
                    'Final contract played with normal bridge rules',
                    'Scoring follows rubber bridge rules'
                ],
                'scoring_info': [
                    'Overtricks: 20 points each (30 in NT)',
                    'Game: 100+ points below line',
                    'Small slam: 500 points (750 vulnerable)',
                    'Grand slam: 1000 points (1500 vulnerable)'
                ]
            }
        }
    }
    return configs.get(game_type, {}).get(variant, {})

@app.template_filter('from_json')
def from_json(value):
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_type>')
def select_variant(game_type):
    variants = get_game_variants(game_type)
    if len(variants) == 1:
        return redirect(url_for('setup_game', game_type=game_type, variant=variants[0]['id']))
    return render_template('variants.html', game_type=game_type, variants=variants)

@app.route('/setup/<game_type>/<variant>')
def setup_game(game_type, variant):
    return render_template('setup.html', game_type=game_type, variant=variant)

@app.route('/play/<game_type>/<variant>')
def play_game(game_type, variant):
    game_id = request.args.get('game_id')
    if not game_id:
        game_id = str(uuid.uuid4())
        players = request.args.getlist('players')
        
        conn = sqlite3.connect('card_games.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (id, game_type, variant, players, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (game_id, game_type, variant, json.dumps(players), json.dumps({})))
        conn.commit()
        conn.close()
    
    return render_template('game.html', 
                         game_type=game_type, 
                         variant=variant, 
                         game_id=game_id,
                         game_config=get_game_config(game_type, variant))

@app.route('/api/score', methods=['POST'])
def add_score():
    data = request.json
    game_id = data['game_id']
    
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scores (game_id, round_number, player_name, score, bid, made_bid, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (game_id, data.get('round_number', 1), data['player'], 
          data['score'], data.get('bid'), data.get('made_bid'), data.get('notes')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/scores/<game_id>')
def get_scores(game_id):
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT round_number, player_name, score, bid, made_bid, notes, timestamp
        FROM scores WHERE game_id = ? ORDER BY round_number, timestamp
    ''', (game_id,))
    
    scores = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'round': s[0], 'player': s[1], 'score': s[2], 
        'bid': s[3], 'made_bid': s[4], 'notes': s[5], 'timestamp': s[6]
    } for s in scores])

@app.route('/api/recent-games')
def get_recent_games():
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, game_type, variant, players, created_at, status
        FROM games 
        ORDER BY created_at DESC 
        LIMIT 5
    ''')
    
    games = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': g[0], 'game_type': g[1], 'variant': g[2], 
        'players': json.loads(g[3]) if g[3] else [], 
        'created_at': g[4], 'status': g[5]
    } for g in games])

@app.route('/api/game/<game_id>')
def get_game_details(game_id):
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, game_type, variant, players, created_at, completed_at, status, data
        FROM games WHERE id = ?
    ''', (game_id,))
    
    game = cursor.fetchone()
    
    if not game:
        conn.close()
        return jsonify({'error': 'Game not found'}), 404
    
    cursor.execute('''
        SELECT round_number, player_name, score, bid, made_bid, notes, timestamp
        FROM scores WHERE game_id = ? ORDER BY round_number, timestamp
    ''', (game_id,))
    
    scores = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'game': {
            'id': game[0], 'game_type': game[1], 'variant': game[2],
            'players': json.loads(game[3]) if game[3] else [],
            'created_at': game[4], 'completed_at': game[5],
            'status': game[6], 'data': json.loads(game[7]) if game[7] else {}
        },
        'scores': [{
            'round': s[0], 'player': s[1], 'score': s[2],
            'bid': s[3], 'made_bid': s[4], 'notes': s[5], 'timestamp': s[6]
        } for s in scores]
    })

@app.route('/history')
def game_history():
    conn = sqlite3.connect('card_games.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, game_type, variant, players, created_at, completed_at, status
        FROM games ORDER BY created_at DESC
    ''')
    
    games = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', games=games)

if __name__ == '__main__':
    app.secret_key = 'your-secret-key-change-this'
    init_db()
    app.run(debug=True, host='0.0.0.0', port=2283)