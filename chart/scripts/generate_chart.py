import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
from github import Github
from datetime import datetime, timedelta
import requests
import json
import pytz

# Font properties for the chart
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
language_bytes = {}

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
    
    # Fetch languages by bytes
    try:
        langs = repo.get_languages()
        for lang, bytes_count in langs.items():
            language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
    except:
        # Handle repositories where language stats can't be accessed
        continue

    total_stars += repo.stargazers_count
    total_forks += repo.forks_count
    total_watchers += repo.watchers_count
    total_size += repo.size

    # Count commits for different time periods
    try:
        for commit in repo.get_commits(since=now - timedelta(days=365)):
            commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(perth_tz)
            commit_counts['total'] += 1
            for period, delta in time_periods.items():
                if now - commit_date <= delta:
                    commit_counts[period] += 1
    except:
        # Handle repositories where commits can't be accessed
        continue

# Sort languages by count
sorted_languages = sorted(language_count.keys(), key=lambda lang: language_count[lang], reverse=True)
sorted_counts = [language_count[lang] for lang in sorted_languages]

# Create pie chart for language distribution
fig, ax = plt.subplots(figsize=(8, 5))
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
most_starred = max(repos, key=lambda r: r.stargazers_count) if repos else None
most_forked = max(repos, key=lambda r: r.forks_count) if repos else None
most_watched = max(repos, key=lambda r: r.watchers_count) if repos else None

# Calculate average repo size in MB
avg_repo_size = total_size / total_repos / 1024 if total_repos > 0 else 0

# Calculate Top Languages by Lines of Code
# Assuming average 50 bytes per line (this is an approximation)
avg_bytes_per_line = 50
language_loc = {lang: bytes_count // avg_bytes_per_line for lang, bytes_count in language_bytes.items()}
sorted_loc = sorted(language_loc.items(), key=lambda item: item[1], reverse=True)
top_languages_loc = sorted_loc[:10]  # Top 10 languages

# Update README with improved formatting
with open('README.md', 'w') as f:
    f.write(f"# {github_username}'s GitHub Stats\n\n")
    f.write(f"![Language Distribution](chart.png)\n\n")
    f.write(f"## 📊 Quick Stats\n\n")
    f.write(f"- **Total Repositories**: {total_repos}\n")
    f.write(f"- **Total Stars Earned**: {total_stars}\n")
    f.write(f"- **Total Forks**: {total_forks}\n")
    f.write(f"- **Total Watchers**: {total_watchers}\n")
    f.write(f"- **Languages Used**: {len(languages_used)}\n")
    f.write(f"- **Average Repository Size**: {avg_repo_size:.2f} MB\n")
    #if most_starred:
        #f.write(f"- **Most Starred Repository**: [{most_starred.name}]({most_starred.html_url}) with {most_starred.stargazers_count} ⭐\n")
    #if most_forked:
        #f.write(f"- **Most Forked Repository**: [{most_forked.name}]({most_forked.html_url}) with {most_forked.forks_count} 🍴\n")
    #if most_watched:
        #f.write(f"- **Most Watched Repository**: [{most_watched.name}]({most_watched.html_url}) with {most_watched.watchers_count} 👀\n")
    f.write(f"\n## 📈 Commit Activity\n\n")
    f.write(f"- **Last 24 hours**: {commit_counts['24h']} commits\n")
    f.write(f"- **Last 7 days**: {commit_counts['7d']} commits\n")
    f.write(f"- **Last 30 days**: {commit_counts['30d']} commits\n")
    f.write(f"- **Last 365 days**: {commit_counts['365d']} commits\n")
    f.write(f"\n## 📝 Top Languages by Lines of Code\n\n")
    for lang, loc in top_languages_loc:
        f.write(f"- **{lang}**: {loc} LOC\n")

# Send final message with enhanced Discord embed
perth_now = datetime.now(perth_tz)
date_str = perth_now.strftime("%d %B %Y")
time_str = perth_now.strftime("%I:%M %p")
short_date_str = perth_now.strftime("%d %b %y")

# Prepare Top Languages by LOC for Discord Embed
top_languages_loc_str = "\n".join([f"**{lang}**: {loc} LOC" for lang, loc in top_languages_loc])

embeds = [
    {
        "title": "📊 GitHub Stats Update",
        "color": 3066993,
        "thumbnail": {"url": f"https://github.com/{github_username}.png"},
        "fields": [
            {"name": "**Total Repositories**", "value": f"{total_repos}", "inline": True},
            {"name": "**Total Stars**", "value": f"{total_stars}", "inline": True},
            {"name": "**Total Forks**", "value": f"{total_forks}", "inline": True},
            {"name": "**Total Watchers**", "value": f"{total_watchers}", "inline": True},
            {"name": "**Languages Used**", "value": f"{len(languages_used)}", "inline": True},
            {"name": "**Average Repo Size**", "value": f"{avg_repo_size:.2f} MB", "inline": True},
            #{"name": "**Most Starred Repo**", "value": most_starred.name if most_starred else "N/A", "inline": True},
            #{"name": "**Most Forked Repo**", "value": most_forked.name if most_forked else "N/A", "inline": True},
            #{"name": "**Most Watched Repo**", "value": most_watched.name if most_watched else "N/A", "inline": True},
            {"name": "**Commits (24h)**", "value": f"{commit_counts['24h']}", "inline": True},
            {"name": "**Commits (7d)**", "value": f"{commit_counts['7d']}", "inline": True},
            {"name": "**Commits (30d)**", "value": f"{commit_counts['30d']}", "inline": True},
            {"name": "**Commits (365d)**", "value": f"{commit_counts['365d']}", "inline": True},
            {"name": "\u200B", "value": "\u200B"},  # Blank field for spacing
            {"name": "**Top Languages by Lines of Code**", "value": top_languages_loc_str, "inline": False},
        ],
        "footer": {"text": f"Updated on {date_str} at {time_str} (Perth Time)"}
    }
]

send_discord_message(f"✅ **[{short_date_str}]** GitHub stats updated successfully!", embeds=embeds)

print("README updated successfully!")
