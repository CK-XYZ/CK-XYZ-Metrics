import os
import requests
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys
from github import Github

# Constants
prop = {'family': 'sans-serif', 'weight': 'black', 'size': 20}
github_username = "FiendsXYZ"
github_token = os.getenv("GH_TOKEN")
api_url = f"https://api.github.com/user/repos"
headers = {
    "username": github_username,
    "Authorization": f"token {github_token}"
}
webhook_url = os.getenv("DISCORD_WEBHOOK")

# Function to send webhook notifications
def send_webhook(content):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)
    print(f"Discord webhook response: {response.status_code}, Message: {content}")

# Fetching repositories
response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    repos = response.json()
    language_count = {}

    send_webhook("⏳ Updating GH chart...")

    for repo in repos:
        if repo['language']:
            if repo['language'] in language_count:
                language_count[repo['language']] += 1
            else:
                language_count[repo['language']] = 1

    if not language_count:
        send_webhook("🚫 No changes detected in repository languages.")
    else:
        languages = list(language_count.keys())
        counts = list(language_count.values())
        sorted_languages = sorted(language_count.keys(), key=lambda lang: language_count[lang])
        sorted_counts = [language_count[lang] for lang in sorted_languages]

        for lang in sorted_languages:
            print(f"{lang}: {language_count[lang]}")

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

        send_webhook("✅ Chart updated successfully! 📊")

else:
    print(f"Failed to fetch repositories. Status code: {response.status_code}")
    send_webhook("❌ Chart failed to update! Please check the logs.")
