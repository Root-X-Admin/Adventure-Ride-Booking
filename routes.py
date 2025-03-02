from flask import Blueprint, render_template, request
from models import Activity

# Define Blueprint
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template('index.html')

@app_routes.route('/activities')
def activity_listing():
    # Get filter parameters
    activity_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    price_range = request.args.get('price')
    location = request.args.get('location')

    query = Activity.query  # Start query

    # Apply filters
    if activity_type:
        query = query.filter(Activity.type == activity_type)
    if difficulty:
        query = query.filter(Activity.difficulty == difficulty)
    if price_range:
        min_price, max_price = map(int, price_range.split('-'))
        query = query.filter(Activity.price.between(min_price, max_price))
    if location:
        query = query.filter(Activity.location.contains(location))

    activities = query.all()  # Fetch filtered results
    print("Fetched activities:", activities)  # Debugging line

    return render_template('activities.html', activities=activities)

@app_routes.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)  # Fetch activity from database
    return render_template('activity_detail.html', activity=activity)