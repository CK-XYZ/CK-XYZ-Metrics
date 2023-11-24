import os
import requests
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
import sys
import json
from github import Github


prop = {'family': 'sans-serif', 'weight': 'black', 'size': 20}

github_username = "FiendsXYZ"
github_token = os.getenv("GH_TOKEN")

api_url = f"https://api.github.com/user/repos"


headers = {
    "username": github_username,
    "Authorization": f"token {github_token}"
}


response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    repos = response.json()
    language_count = {}
    
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    msg_content = "Updating GH chart..."
    data = {"content": msg_content}
    response = requests.post(webhook_url, json=data)
    print(f"Discord webhook response: {response.status_code}")

    for repo in repos:
        if repo['language']:
            if repo['language'] in language_count:
                language_count[repo['language']] += 1
            else:
                language_count[repo['language']] = 1

    languages = list(language_count.keys())
    counts = list(language_count.values())
    sorted_languages = sorted(language_count.keys(), key=lambda lang: language_count[lang])
    sorted_counts = [language_count[lang] for lang in sorted_languages]
    
    for lang in sorted_languages:
        print(f"{lang}: {language_count[lang]}")

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#333333')

<<<<<<< HEAD
"""
readme_content += "\n## Top Languages by  Commits\n"

for lang in sorted_languages:
    readme_content += f"- {lang}: {language_commits[lang]} commits\n"

with open('README.md', 'w') as f:
    f.write(readme_content)

# Send Discord Notification
data = {"content": "Chart and README updated!"}
requests.post(webhook_url, json=data)
=======
 
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
    data = {"content": "Chart updated!"}
    response = requests.post(webhook_url, json=data)
    print(f"Discord webhook response: {response.status_code}")

else:
    print(f"Failed to fetch repositories. Status code: {response.status_code}")
    data = {"content": "Chart failed to update!"}
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    response = requests.post(webhook_url, json=data)
>>>>>>> parent of 474b487 (0.0.0.2.5)
