from flask import Blueprint, jsonify
import os
import re

dbtest_bp = Blueprint('dbtest', __name__)

@dbtest_bp.route('/check', methods=['GET'])
def check_database_url():
    """Check DATABASE_URL format and show masked version for debugging"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            return jsonify({
                'error': 'DATABASE_URL not set',
                'status': 'missing',
                'help': 'Set DATABASE_URL environment variable in Render'
            }), 500
        
        # Parse the URL to show structure without exposing password
        try:
            # postgresql://username:password@host:port/database
            pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
            match = re.match(pattern, database_url)
            
            if match:
                username, password, host, port, database = match.groups()
                masked_url = f"postgresql://{username}:{'*' * len(password)}@{host}:{port}/{database}"
                
                return jsonify({
                    'status': 'url_found',
                    'format': 'valid',
                    'masked_url': masked_url,
                    'components': {
                        'username': username,
                        'host': host,
                        'port': port,
                        'database': database,
                        'password_length': len(password)
                    },
                    'help': 'DATABASE_URL format looks correct. Check password in Neon dashboard.'
                }), 200
            else:
                return jsonify({
                    'error': 'Invalid DATABASE_URL format',
                    'status': 'invalid_format',
                    'expected': 'postgresql://username:password@host:port/database',
                    'received_prefix': database_url[:20] + '...' if len(database_url) > 20 else database_url,
                    'help': 'Check your Neon connection string format'
                }), 400
                
        except Exception as parse_error:
            return jsonify({
                'error': 'Failed to parse DATABASE_URL',
                'status': 'parse_error',
                'details': str(parse_error),
                'help': 'DATABASE_URL might be malformed'
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Unexpected error checking DATABASE_URL',
            'details': str(e),
            'status': 'error'
        }), 500