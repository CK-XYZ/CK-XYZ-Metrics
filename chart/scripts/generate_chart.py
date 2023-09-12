import os
import requests
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap
import sys
import os
from github import Github


font_path = os.path.join(os.path.dirname(__file__), '../assets/roboto.ttf')
prop = {'family': 'Roboto', 'weight': 'black', 'size': 18}

github_username = "FiendsXYZ"
github_token = os.getenv("GH_TOKEN")

api_url = f"https://api.github.com/user/repos"


headers = {
    "username": github_username,
    "Authorization": f"token {github_token}"
}


response = requests.get(api_url, headers=headers)

print(response.status_code)


if response.status_code == 200:
    repos = response.json()
    language_count = {}

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
    plt.savefig('chart.png', bbox_inches='tight', facecolor=fig.get_facecolor())

else:
    print(f"Failed to fetch repositories. Status code: {response.status_code}")
