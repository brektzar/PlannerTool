import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# MongoDB configuration
MONGODB_URI = (
    "mongodb+srv://mondoofsweden:2ahCdag8SItUVxbc@plannertolldb.dd28f.mongodb.net/?retryWrites=true&w=majority"
)
DB_NAME = os.getenv('DB_NAME') or 'planner_tool'

# Collections
GOALS_COLLECTION = 'goals'
TECHNICAL_NEEDS_COLLECTION = 'technical_needs'
BUGS_COLLECTION = 'bugs'
HISTORY_COLLECTION = 'history' 