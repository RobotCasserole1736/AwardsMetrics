import csv
from collections import Counter

def top_imagery_awards(filename: str, top_n: int = 30, search_term: str = 'imagery') -> None:
    award_counter = Counter()

    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if search_term in row['award_name'].lower():
                award_counter[row['team']] += 1

    # Get the top N teams
    top_teams = award_counter.most_common(top_n)

    # Print the results
    for team, count in top_teams:
        print(f"{team}: {count}")

# Example usage
top_imagery_awards('team_awards.csv', top_n=50, search_term='Engineering Inspiration')