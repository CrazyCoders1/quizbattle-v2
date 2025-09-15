from flask import Flask, jsonify
import os

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def root():
        return jsonify({
            'name': 'QuizBattle API',
            'version': '1.0.0',
            'status': 'running - minimal mode'
        }), 200
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'mode': 'minimal'
        }), 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
