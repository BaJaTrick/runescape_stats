from flask import Flask, render_template, request, session, redirect, url_for
import requests
import json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Load skills from JSON file
with open('skills.json') as f:
    skills = json.load(f)

# Load predefined quests from JSON file
with open('quests.json') as f:
    predefined_quests = json.load(f)

API_URL = "https://secure.runescape.com/m=hiscore/index_lite.ws?player="
QUESTS_API_URL = "https://apps.runescape.com/runemetrics/quests?user="

def parse_skills_data(raw_data):
    parsed_data = {skill: {'rank': -1, 'level': -1, 'xp': -1} for skill in skills}
    lines = raw_data.strip().splitlines()
    
    for index, line in enumerate(lines[:len(skills)]):
        rank, level, xp = line.split(',')
        parsed_data[skills[index]] = {
            'rank': int(rank),
            'level': int(level),
            'xp': int(xp)
        }

    return parsed_data

def parse_quests_data(username):
    response = requests.get(f'{QUESTS_API_URL}{username}')
    quests_data = response.json()
    
    user_quests = []
    total_completed = 0
    total_quest_points = 0

    for quest in quests_data.get('quests', []):
        for q in predefined_quests:
            if q['name'].lower() == quest['title'].lower():
                completed = quest['status'].lower() == 'completed'
                q['completed'] = completed
                q['points'] = quest['questPoints']
                user_quests.append(q)

                if completed:
                    total_completed += 1
                    total_quest_points += quest['questPoints']

    return {
        'quests': user_quests,
        'total_completed': total_completed,
        'total_quest_points': total_quest_points
    }


# Register the custom filter
@app.template_filter('format_xp')
def format_xp(value):
    """Format XP with commas."""
    return "{:,}".format(value)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/skills', methods=['GET', 'POST'])
def show_skills():
    if request.method == 'POST':
        usernames = [u.strip() for u in request.form.getlist('usernames') if u.strip()]
        session['usernames'] = usernames  # Save usernames in session

        response_data = {}
        for username in usernames:
            response = requests.get(f'{API_URL}{username}')
            if response.status_code == 200:
                response_data[username] = parse_skills_data(response.text)
            else:
                # Handle case where the username does not return valid data
                response_data[username] = {skill: {'rank': -1, 'level': -1, 'xp': 0} for skill in skills}

        session['skills_data'] = response_data  # Save skills data to session

        # Calculate max XP per skill only for usernames that have data in response_data
        session['max_xp_per_skill'] = {
            skill: max([response_data[u][skill]['xp'] for u in usernames if u in response_data and skill in response_data[u]]) for skill in skills
        }

    elif 'skills_data' in session:
        response_data = session['skills_data']
        usernames = session.get('usernames', [])
    else:
        return redirect(url_for('index'))

    return render_template('index.html', response_data=response_data, usernames=usernames, max_xp_per_skill=session.get('max_xp_per_skill', {}), skills=skills, tab='skills')

@app.route('/quests')
def show_quests():
    usernames = session.get('usernames', [])

    quest_data = {}
    for username in usernames:
        quest_data[username] = parse_quests_data(username)

    session['quests_data'] = quest_data  # Save quests data to session

    return render_template('quests.html', quest_data=quest_data, usernames=usernames, quests=predefined_quests)



if __name__ == '__main__':
    app.run(debug=True)
