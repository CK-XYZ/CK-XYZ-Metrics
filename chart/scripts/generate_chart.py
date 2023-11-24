from github import Github
import os
import requests
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# GitHub Credentials and Variables
github_username = "FiendsXYZ"
github_token = os.getenv("GH_TOKEN")
webhook_url = os.getenv("DISCORD_WEBHOOK")

# Initialize Variables
commit_count = {
    '24hr': 0,
    '7d': 0,
    '30d': 0,
    '90d': 0,
    '180d': 0,
    '365d': 0
}
language_commits = {}
g = Github(github_token)
user = g.get_user(github_username)

# Fetch Repositories
repos = user.get_repos()

# Loop through each repo
for repo in repos:
    # Loop through each commit in the repo
    commits = repo.get_commits()
    for commit in commits:
        # TODO: Add your time filtering logic here to update commit_count
        
        # Update language commits
        if repo.language:
            language_commits[repo.language] = language_commits.get(repo.language, 0) + 1

# Generate Chart
prop = {'family': 'sans-serif', 'weight': 'black', 'size': 20}
languages = list(language_commits.keys())
counts = list(language_commits.values())
sorted_languages = sorted(language_commits.keys(), key=lambda x: language_commits[x], reverse=True)[:5]
sorted_counts = [language_commits[x] for x in sorted_languages]

fig, ax = plt.subplots(figsize=(10, 8))
fig.patch.set_facecolor('#333333')
gradient = LinearSegmentedColormap.from_list('custom', ['#017501', '#00de00'], N=len(sorted_languages))
colors = [gradient(i / len(sorted_languages)) for i in range(len(sorted_languages))]

ax.pie(sorted_counts, labels=sorted_languages, autopct='%1.1f%%', startangle=270, colors=colors, textprops={'color': 'white', 'weight': 'bold', 'size': 16})
plt.axis('equal')
plt.savefig('chart.png', bbox_inches='tight', facecolor=fig.get_facecolor())

# Update README
readme_content = f"""<p align="center">
  <img src="chart.png" alt="Lang Chart" width="65%">
</p>

## Commits

| Time Period | Commits |
|-------------|---------|
"""

for period, count in commit_count.items():
    readme_content += f"| {period} | {count} |\n"

readme_content += "\n## Top Languages by Commits\n"

for lang in sorted_languages:
    readme_content += f"- {lang}: {language_commits[lang]} commits\n"

with open('README.md', 'w') as f:
    f.write(readme_content)

# Send Discord Notification
data = {"content": "Chart and README updated!"}
requests.post(webhook_url, json=data)
