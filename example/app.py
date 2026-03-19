import asyncio
from pathlib import Path

from robyn import Headers, Response, Robyn

import chameleon_robyn

app = Robyn(__file__)

# --- Sample data (simulating a database) ---

EPISODES = [
    {'id': 1, 'title': 'Welcome to the Show', 'guest': 'Guido van Rossum', 'duration': '45 min'},
    {'id': 2, 'title': 'Async All the Things', 'guest': 'Andrew Godwin', 'duration': '52 min'},
    {'id': 3, 'title': 'Rust-Powered Python', 'guest': 'Samuel Colvin', 'duration': '38 min'},
    {'id': 4, 'title': 'The Robyn Framework', 'guest': 'Sanskar Jethi', 'duration': '41 min'},
    {'id': 5, 'title': 'Template Engines Compared', 'guest': 'Armin Ronacher', 'duration': '55 min'},
]

GUESTS = {
    'guido-van-rossum': {'name': 'Guido van Rossum', 'bio': 'Creator of Python', 'episodes': [1]},
    'andrew-godwin': {'name': 'Andrew Godwin', 'bio': 'Django Channels & async pioneer', 'episodes': [2]},
    'samuel-colvin': {'name': 'Samuel Colvin', 'bio': 'Creator of Pydantic', 'episodes': [3]},
    'sanskar-jethi': {'name': 'Sanskar Jethi', 'bio': 'Creator of Robyn', 'episodes': [4]},
    'armin-ronacher': {'name': 'Armin Ronacher', 'bio': 'Creator of Flask & Jinja2', 'episodes': [5]},
}


# --- Routes ---


@app.get('/')
@chameleon_robyn.template('home/index.pt')
async def index(request):
    await asyncio.sleep(0.001)  # Simulate async work
    return {
        'title': 'Chameleon + Robyn Demo',
        'episode_count': len(EPISODES),
        'guest_count': len(GUESTS),
    }


@app.get('/episodes')
@chameleon_robyn.template('episodes/list.pt')
def episode_list(request):
    return {
        'title': 'All Episodes',
        'episodes': EPISODES,
    }


@app.get('/episodes/:episode_id')
@chameleon_robyn.template('episodes/detail.pt')
async def episode_detail(request, episode_id: int):
    episode = next((ep for ep in EPISODES if ep['id'] == episode_id), None)
    if not episode:
        chameleon_robyn.not_found()
    return {
        'title': episode['title'],
        'episode': episode,
    }


@app.get('/guests')
@chameleon_robyn.template('guests/list.pt')
def guest_list(request):
    return {
        'title': 'Our Guests',
        'guests': GUESTS,
    }


@app.get('/guests/:slug')
@chameleon_robyn.template('guests/detail.pt')
def guest_detail(request, slug: str):
    guest = GUESTS.get(slug)
    if not guest:
        chameleon_robyn.not_found()
    return {
        'title': guest['name'],
        'guest': guest,
        'slug': slug,
    }


@app.get('/search')
@chameleon_robyn.template('search/results.pt')
def search(request):
    q = request.query_params.get('q', '')
    results = []
    if q:
        q_lower = q.lower()
        results = [ep for ep in EPISODES if q_lower in ep['title'].lower() or q_lower in ep['guest'].lower()]
    return {
        'title': f'Search: {q}' if q else 'Search',
        'query': q,
        'results': results,
    }


@app.get('/redirect-example')
@chameleon_robyn.template('home/index.pt')
def redirect_example(request):
    """Demonstrates Response pass-through — the decorator won't render a template."""
    return Response(
        status_code=302,
        description='',
        headers=Headers({'Location': '/episodes'}),
    )


@app.get('/xml/episodes')
@chameleon_robyn.template('episodes/feed.xml', content_type='application/xml', status_code=200)
def episodes_xml(request):
    return {'episodes': EPISODES}


# --- App setup ---


def configure():
    dev_mode = True
    template_folder = (Path(__file__).resolve().parent / 'templates').as_posix()
    chameleon_robyn.global_init(template_folder, auto_reload=dev_mode, restricted_namespace=False)


def main():
    configure()
    app.start(host='127.0.0.1', port=5555)


if __name__ == '__main__':
    main()
