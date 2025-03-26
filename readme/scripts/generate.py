import os
from github import Github
from datetime import datetime, timedelta
import requests
import pytz

# GitHub credentials
github_token = os.getenv("GH_TOKEN")
github_username = "CK-XYZ"
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

# Fetch all repositories 
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
        continue

    total_stars += repo.stargazers_count
    total_forks += repo.forks_count
    total_watchers += repo.watchers_count
    total_size += repo.size

    # Count commits
    try:
        for commit in repo.get_commits(since=now - timedelta(days=365)):
            commit_date = commit.commit.author.date.replace(tzinfo=pytz.UTC).astimezone(perth_tz)
            commit_counts['total'] += 1
            for period, delta in time_periods.items():
                if now - commit_date <= delta:
                    commit_counts[period] += 1
    except:
        continue

# Additional stats
total_repos = len(repos)
most_starred = max(repos, key=lambda r: r.stargazers_count) if repos else None
most_forked = max(repos, key=lambda r: r.forks_count) if repos else None
most_watched = max(repos, key=lambda r: r.watchers_count) if repos else None

# Calculate average repo size in MB
avg_repo_size = total_size / total_repos / 1024 if total_repos > 0 else 0

# Calculate Top Languages by Lines of Code
avg_bytes_per_line = 50
language_loc = {lang: bytes_count // avg_bytes_per_line for lang, bytes_count in language_bytes.items()}
sorted_loc = sorted(language_loc.items(), key=lambda item: item[1], reverse=True)
top_languages_loc = sorted_loc[:6]  

# Update README
with open('README.md', 'w') as f:
    f.write(f"# {github_username}'s GitHub Stats\n\n")
    
    # Quick Stats Table
    f.write(f"## 📊 Quick Stats\n\n")
    f.write(f"| Metric               | Value       | Metric               | Value       |\n")
    f.write(f"|----------------------|-------------|----------------------|-------------|\n")
    f.write(f"| Total Repositories   | {total_repos} | Total Watchers       | {total_watchers} |\n")
    f.write(f"| Languages Used       | {len(languages_used)} | Average Repo Size    | {avg_repo_size:.2f} MB |\n")
    
    # Commit Activity Table
    f.write(f"\n## 📈 Commit Activity\n\n")
    f.write(f"| Time Period      | Commits      | Time Period      | Commits      |\n")
    f.write(f"|------------------|--------------|------------------|--------------|\n")
    f.write(f"| Last 24 Hours    | {commit_counts['24h']} | Last 7 Days      | {commit_counts['7d']} |\n")
    f.write(f"| Last 30 Days     | {commit_counts['30d']} | Last 365 Days    | {commit_counts['365d']} |\n")
    
    # Top Languages by Lines of Code Table
    f.write(f"\n## 📝 Top Languagese\n\n")
    f.write(f"| Language       | LOC        | Language       | LOC        |\n")
    f.write(f"|----------------|------------|----------------|------------|\n")
    for i in range(0, len(top_languages_loc), 2):
        lang1, loc1 = top_languages_loc[i]
        lang2, loc2 = top_languages_loc[i + 1] if i + 1 < len(top_languages_loc) else ("", "")
        f.write(f"| {lang1}       | {loc1} LOC  | {lang2}       | {loc2} LOC  |\n")
    
    f.write(f"\n## 📅 Last Updated\n\n")
    perth_now = datetime.now(perth_tz)
    date_str = perth_now.strftime("%d %B %Y")
    time_str = perth_now.strftime("%I:%M %p")
    f.write(f"Updated on **{date_str}** at **{time_str}** (+8)\n")

# Send Discord message with updated stats
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
            {"name": "**Commits (24h)**", "value": f"{commit_counts['24h']}", "inline": True},
            {"name": "**Commits (7d)**", "value": f"{commit_counts['7d']}", "inline": True},
            {"name": "**Commits (30d)**", "value": f"{commit_counts['30d']}", "inline": True},
            {"name": "**Commits (365d)**", "value": f"{commit_counts['365d']}", "inline": True},
            {"name": "\u200B", "value": "\u200B"}, 
            {"name": "**Top Languages by Lines of Code**", "value": top_languages_loc_str, "inline": False},
        ],
    }
]

send_discord_message(f"✅ **[{short_date_str}]** GitHub stats updated successfully!", embeds=embeds)

print("README updated successfully!")