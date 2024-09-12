import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from github import Github
from datetime import datetime, timedelta
import requests
import json
import pytz

# Font properties
prop = {'family': 'sans-serif', 'weight': 'black', 'size': 20}

# GitHub credentials
github_token = os.getenv("GH_TOKEN")
github_username = "FiendsXYZ"
webhook_url = os.getenv("DISCORD_WEBHOOK")

# Set up timezone
perth_tz = pytz.timezone('Australia/Perth')

# Discord webhook function
def send_discord_message(content, embeds=None):
    data = {"content": content, "embeds": embeds}
    response = requests.post(webhook_url, json=data)
    print(f"Discord webhook response: {response.status_code}")

# Send initial message
send_discord_message("🔄 Updating GitHub stats...")

# GitHub API
g = Github(github_token)
user = g.get_user()

# Fetch all repositories (including private ones)
repos = list(user.get_repos())
language_count = {}

total_stars = 0
total_forks = 0
total_watchers = 0
total_size = 0
languages_used = set()

# Time periods for commit counts
time_periods = {
    '24h': timedelta(hours=24),
    '7d': timedelta(days=7),
    '30d': timedelta(days=30),
    '365d': timedelta(days=365)
}
commit_counts = {period: 0 for period in time_periods.keys()}
commit_counts['total'] = 0

now = datetime.now(pytz.UTC).astimezone(perth_tz)

for repo in repos:
    if repo.language:
        language_count[repo.language] = language_count.get(repo.language, 0) + 1
        languages_used.add(repo.language)
    total_stars += repo.stargazers_count
    total_forks += repo.forks_count
    total_watchers += repo.watchers_count
    total_size += repo.size

    # Count commits for different time periods
    for commit in repo.get_commits(since=now - timedelta(days=365)):
        commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(perth_tz)
        commit_counts['total'] += 1
        for period, delta in time_periods.items():
            if now - commit_date <= delta:
                commit_counts[period] += 1

# Sort languages by count
sorted_languages = sorted(language_count.keys(), key=lambda lang: language_count[lang], reverse=True)
sorted_counts = [language_count[lang] for lang in sorted_languages]

# Create pie chart
fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor('#333333')

gradient = LinearSegmentedColormap.from_list('green', ['#017501', '#00de00'], N=len(sorted_languages))
colors = [gradient(i / len(sorted_languages)) for i in range(len(sorted_languages))]

wedges, texts, autotexts = ax.pie(
    sorted_counts,
    labels=[label.upper() for label in sorted_languages],
    autopct='%1.1f%%',
    startangle=270,
    textprops={'fontproperties': prop, 'color': 'white'}, 
    colors=colors
)

plt.axis('equal')
chart_path = os.path.join(os.getcwd(), "chart.png")
plt.savefig(chart_path, bbox_inches='tight', facecolor=fig.get_facecolor())

# Additional stats
total_repos = len(repos)
most_starred = max(repos, key=lambda r: r.stargazers_count)

# Calculate average repo size
avg_repo_size = total_size / total_repos if total_repos > 0 else 0

# Update README
with open('README.md', 'w') as f:
    f.write(f"# {github_username}'s GitHub Stats\n\n")
    f.write(f"![Language Distribution](chart.png)\n\n")
    f.write(f"## Quick Stats\n")
    f.write(f"- Total Repositories: {total_repos}\n")
    f.write(f"- Total Stars Earned: {total_stars}\n")
    f.write(f"- Total Forks: {total_forks}\n")
    f.write(f"- Total Watchers: {total_watchers}\n")
    f.write(f"- Languages Used: {len(languages_used)}\n")
    f.write(f"- Average Repository Size: {avg_repo_size:.2f} KB\n")
    f.write(f"- Most Starred Repository: {most_starred.stargazers_count} stars\n\n")
    f.write(f"## Commit Activity\n")
    f.write(f"- Last 24 hours: {commit_counts['24h']} commits\n")
    f.write(f"- Last 7 days: {commit_counts['7d']} commits\n")
    f.write(f"- Last 30 days: {commit_counts['30d']} commits\n")
    f.write(f"- Last 365 days: {commit_counts['365d']} commits\n")

# Send final message with stats
perth_now = datetime.now(pytz.timezone('Australia/Perth'))
date_str = perth_now.strftime("%d %B %Y")
time_str = perth_now.strftime("%I:%M%p")
short_date_str = perth_now.strftime("%d %b %y")

embeds = [
    {
        "title": "📊 GitHub Stats Update",
        "color": 3066993,
        "fields": [
            {"name": "📁 Total Repositories", "value": total_repos, "inline": True},
            {"name": "⭐ Total Stars", "value": total_stars, "inline": True},
            {"name": "🔠 Languages Used", "value": len(languages_used), "inline": True},
            {"name": "📅 Commits (24h)", "value": commit_counts['24h'], "inline": True},
            {"name": "📅 Commits (7d)", "value": commit_counts['7d'], "inline": True},
            {"name": "📅 Commits (30d)", "value": commit_counts['30d'], "inline": True},
        ],
        "footer": {"text": f"Updated at: {date_str} {time_str} (+8)"}
    }
]

send_discord_message(f"✅ **[{short_date_str}]** Chart updated successfully!", embeds=embeds)

print("README updated successfully!")