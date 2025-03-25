import asyncio
import aiohttp
import csv
import os
import requests
from .secrets import API_KEY

API_URL = "https://www.thebluealliance.com/api/v3"
OUTPUT_FILE = "team_awards.csv"


async def fetch_json(session, url):
    """Fetch JSON data from TBA API."""
    headers = {"X-TBA-Auth-Key": API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error {response.status} for {url}")
            return None


async def get_team_awards(session, team_key):
    """Fetch awards history for a given team."""
    awards = []
    for year in range(1992, 2025):  # FRC started in 1992, update for current year
        url = f"{API_URL}/team/{team_key}/awards/{year}"
        print(f"Fetching {team_key} awards for {year}...")
        data = await fetch_json(session, url)

        if data:
            for award in data:
                print(f"  Found '{award['name']}' in {year} at {award['event_key']}")
                awards.append([team_key, award["name"], year, award["event_key"]])

    return awards


async def save_awards_incrementally():
    """Fetch all teams, process awards in parallel, and save to CSV."""
    teams = await get_all_teams()
    processed_teams = load_processed_teams()

    # Open CSV in append mode
    with open(OUTPUT_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        # Write headers if the file is empty
        if os.stat(OUTPUT_FILE).st_size == 0:
            writer.writerow(["team", "award_name", "year", "event"])
            file.flush()

        async with aiohttp.ClientSession() as session:
            for team in teams:
                team_key = team["key"]
                team_name = team.get("nickname", team_key)

                if team_key in processed_teams:
                    print(f"Skipping {team_name} ({team_key}), already processed.")
                    continue

                print(f"Processing {team_name} ({team_key})...")

                # Fetch awards in parallel for this team
                awards = await get_team_awards(session, team_key)

                if awards:
                    writer.writerows(awards)
                    file.flush()  # Ensure data is written immediately

                # Update processed set
                processed_teams.add(team_key)


async def get_all_teams():
    """Fetch all teams from TBA API."""
    teams = []
    async with aiohttp.ClientSession() as session:
        for page in range(13, 100):  # Fetch in pages
            url = f"{API_URL}/teams/{page}"
            data = await fetch_json(session, url)
            if not data:
                break
            startNum = int(data[0]["key"].lstrip('frc'))
            teams.extend(data)
            print(f"Fetched {len(data)} teams from page {page}")
            #if startNum > 6000:
            #    
            #    

    return teams


def load_processed_teams():
    """Load already processed teams from the CSV file."""
    if not os.path.exists(OUTPUT_FILE):
        return set()

    with open(OUTPUT_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header
        return {row[0] for row in reader}

def get_total_teams():
    """Count the total number of teams using TBA API."""
    total_teams = 0
    page = 0
    headers = {"X-TBA-Auth-Key": API_KEY}

    while True:
        url = f"{API_URL}/teams/{page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code}")
            break

        teams = response.json()
        if not teams:
            # No more data, end pagination
            break

        total_teams += len(teams)
        print(f"Fetched {len(teams)} teams from page {page}, total so far: {total_teams}")

        page += 1

    return total_teams

if __name__ == "__main__":
    print("TotalTeams: ", get_total_teams())
    #asyncio.run(save_awards_incrementally())
