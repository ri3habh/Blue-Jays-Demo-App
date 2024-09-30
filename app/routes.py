from flask import Blueprint, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

main = Blueprint('main', __name__)

# Load exit velocity data
def load_exit_velocity_data():
    return pd.read_csv('data/exit_velocity.csv').to_dict(orient='records')

# Load team summary data
def load_team_summary():
    return pd.read_csv('data/team_summary.csv').to_dict(orient='records')

# Load player stats data
def load_player_stats():
    return pd.read_csv('data/player_stats.csv').to_dict(orient='records')

# Load transactions data
def load_transactions():
    return pd.read_csv('data/transactions.csv').to_dict(orient='records')

# Home route
@main.route('/')
def index():
    # Load the team summary, player stats, and transactions data
    team_summary = load_team_summary()
    player_stats = load_player_stats()
    transactions = load_transactions()

    return render_template('index.html', team_summary=team_summary, player_stats=player_stats, transactions=transactions)

# Route for displaying exit velocity data in a table
@main.route('/exit-velocity')
def exit_velocity():
    exit_velocity_data = load_exit_velocity_data()
    return render_template('exit_velocity.html', data=exit_velocity_data)

# Route for visualizing Blue Jays hitters' exit velocity vs MLB (Scatter Plot)
@main.route('/exit-velocity-chart')
def exit_velocity_chart():
    df = pd.read_csv('data/exit_velocity.csv')

    players = df['last_name, first_name']
    avg_hit_speed = df['avg_hit_speed']
    avg_hr_distance = df['avg_hr_distance']

    # Create scatter plot
    fig, ax = plt.subplots()
    ax.scatter(avg_hit_speed, avg_hr_distance, color='blue')
    ax.set_xlabel('Average Exit Velocity (MPH)')
    ax.set_ylabel('Average Home Run Distance (Feet)')
    ax.set_title('Exit Velocity vs Home Run Distance')

    for i, player in enumerate(players):
        ax.text(avg_hit_speed[i], avg_hr_distance[i], player, fontsize=9)

    # Convert plot to image in base64 format
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()

    return render_template('exit_velocity_chart.html', chart_url=image_base64)

# Route for multiple radar charts comparing hitters
@main.route('/exit-velocity-radar')
def exit_velocity_radar():
    df = pd.read_csv('data/exit_velocity.csv')

    # List of Blue Jays hitters to compare in radar charts
    hitter_groups = [
        ['Guerrero Jr., Vladimir', 'Springer, George'],
        ['Schneider, Davis', 'Kirk, Alejandro'],
        ['Varsho, Daulton', 'Clement, Ernie'],
    ]

    radar_charts = []
    categories = ['avg_hit_speed', 'max_hit_speed', 'ev50', 'ev95plus', 'avg_hr_distance', 'brl_percent']
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    for hitters in hitter_groups:
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

        for hitter in hitters:
            player_data = df[df['last_name, first_name'] == hitter]
            if not player_data.empty:
                values = player_data[categories].values.flatten().tolist()
                values += values[:1]
                
                ax.fill(angles, values, alpha=0.25, label=hitter)
                ax.plot(angles, values, label=hitter)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        plt.title(f"Comparison: {' vs '.join(hitters)}")
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        # Save each radar chart to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        radar_charts.append(base64.b64encode(buf.getvalue()).decode('utf-8'))
        plt.close()

    return render_template('exit_velocity_radar.html', radar_charts=radar_charts)
