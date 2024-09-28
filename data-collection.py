import requests
import pandas as pd
import time

# Vladimir Guerrero Jr.'s player ID
player_id = 665489

# Fetch home run data for the 2023 season
def fetch_home_run_data(player_id):
    print("Fetching home run data...")  # Debugging
    api_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=gameLog&season=2023"
    
    try:
        response = requests.get(api_url, timeout=10)  # Add timeout
    except requests.Timeout:
        print("API request timed out.")
        return None
    
    print("API response received.")  # Debugging
    
    if response.status_code == 200:
        print("Processing data...")  # Debugging
        # Parse the JSON data
        data = response.json()
        games = data['stats'][0]['splits']
        
        home_runs = []
        for game in games:
            if game['stat']['homeRuns'] > 0:  # Games where Vlad hit home runs
                print(f"Processing home run from {game['date']}...")  # Debugging
                # Fetch game details from the live feed
                game_link = game['game']['link']
                game_data = fetch_game_details(game_link)

                hr_data = {
                    'date': game['date'],
                    'opponent': game_data.get('opponent', 'Unknown'),
                    'home_runs': game['stat']['homeRuns'],
                    'exit_velocity': game_data.get('launchSpeed', 'N/A'),
                    'launch_angle': game_data.get('launchAngle', 'N/A'),
                    'distance': game_data.get('totalDistance', 'N/A'),
                    'game_link': game_link
                }
                home_runs.append(hr_data)
                time.sleep(1)  # Avoid hitting the API rate limit

        print("Home run data processed.")  # Debugging
        hr_df = pd.DataFrame(home_runs)
        return hr_df
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

# Function to fetch detailed game data
def fetch_game_details(game_link):
    print(f"Fetching game details from {game_link}...")  # Debugging
    api_url = f"https://statsapi.mlb.com{game_link}"
    
    try:
        response = requests.get(api_url, timeout=10)  # Add timeout
    except requests.Timeout:
        print("Game detail request timed out.")
        return {}
    
    if response.status_code == 200:
        print("Game details received.")  # Debugging
        game_data = response.json()
        detailed_data = {
            'opponent': 'Unknown',
            'launchSpeed': 'N/A',
            'launchAngle': 'N/A',
            'totalDistance': 'N/A'
        }

        # Extracting opponent team name
        detailed_data['opponent'] = game_data['gameData']['teams']['away']['teamName'] if game_data['gameData']['teams']['home']['id'] == player_id else game_data['gameData']['teams']['home']['teamName']

        # Loop through play events to find Vlad's home runs
        for play in game_data['liveData']['plays']['allPlays']:
            # Ensure that we are targeting Vlad's home runs
            if 'batter' in play['matchup'] and play['matchup']['batter']['id'] == player_id:
                if play['result'].get('event') == 'Home Run':
                    print("Found a home run!")  # Debugging
                    # Extract home run details from `hitData`
                    if 'hitData' in play:
                        detailed_data['launchSpeed'] = play['hitData'].get('launchSpeed', 'N/A')
                        detailed_data['launchAngle'] = play['hitData'].get('launchAngle', 'N/A')
                        detailed_data['totalDistance'] = play['hitData'].get('totalDistance', 'N/A')
        
        return detailed_data
    else:
        print(f"Failed to retrieve game details for {game_link}")
        return {}

# Fetch and save the data
hr_df = fetch_home_run_data(player_id)
if hr_df is not None:
    print(hr_df.head())  # Display the first few home runs

    # Save to CSV for easy access later
    hr_df.to_csv('vladdy_hr_2023.csv', index=False)
else:
    print("No data to save.")
