"""
MoneyBuddy API - Simple hackathon-ready budget management API
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from dotenv import load_dotenv
from utils import create_app

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Simple configuration
    port = int(os.getenv('PORT', 420))
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    print("🚀 MoneyBuddy API starting...")
    print(f"   Port: {port}")
    print(f"   Debug: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
