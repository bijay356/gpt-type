import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

# 1. Get GitHub token from Git Credential Manager
p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
stdout, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
token = ''
username = 'bijay356'
for line in stdout.splitlines():
    if line.startswith('password='):
        token = line.split('=', 1)[1]
    elif line.startswith('username='):
        username = line.split('=', 1)[1]

if not token:
    print('ERROR: No GitHub token found in git credentials')
    sys.exit(1)

print(f'Authenticated as GitHub user: {username}')

headers = {
    'Authorization': f'token {token}',
    'User-Agent': 'GPT-TYPE-Uploader',
    'Accept': 'application/vnd.github.v3+json'
}

repo_name = 'gpt-type'

# 2. Check if repo exists, create if not
repo_url = f'https://api.github.com/repos/{username}/{repo_name}'
req = urllib.request.Request(repo_url, headers=headers)
repo_exists = False
try:
    with urllib.request.urlopen(req) as resp:
        repo_exists = True
        print(f'Repository {username}/{repo_name} already exists.')
except urllib.error.HTTPError as e:
    if e.code == 404:
        repo_exists = False
    else:
        print(f'Error checking repo: {e}')

if not repo_exists:
    print(f'Creating repository {username}/{repo_name}...')
    create_url = 'https://api.github.com/user/repos'
    payload = {
        'name': repo_name,
        'description': 'GPT-TYPE: 123+ Languages Typing Speed Test, Typeshala & Ramayan Archery Battle for Windows',
        'private': False,
        'auto_init': True
    }
    req = urllib.request.Request(create_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print('Repository created successfully:', data.get('html_url'))
    except Exception as e:
        print('Error creating repo:', e)
        sys.exit(1)

# 3. Check or Create Release v2.0.0
releases_url = f'https://api.github.com/repos/{username}/{repo_name}/releases'
req = urllib.request.Request(releases_url, headers=headers)
release = None
try:
    with urllib.request.urlopen(req) as resp:
        releases = json.loads(resp.read().decode('utf-8'))
        for r in releases:
            if r.get('tag_name') == 'v2.0.0':
                release = r
                break
except Exception as e:
    print('Error listing releases:', e)

if not release:
    print('Creating Release v2.0.0...')
    release_payload = {
        'tag_name': 'v2.0.0',
        'target_commitish': 'main',
        'name': 'GPT-TYPE v2.0.0 for Windows',
        'body': (
            '# GPT-TYPE v2.0.0 (Official Windows Release)\n\n'
            'Modern 123+ Languages Typing Speed Test, Authentic Nepali Typeshala, and 5-Level Ramayan Archery Battle.\n\n'
            '### Features:\n'
            '- **123+ Languages & Scripts** with native Unicode fonts\n'
            '- **Authentic Nepali Typeshala** with legacy Preeti font & dual-hand keyboard guides\n'
            '- **5-Level Ramayan Archery Battle** (Shurpanakha, Khardushan, Kumbhakaran, Meghnad, Raavan)\n'
            '- **Visual WPM & Error Timeline Chart** (spline cubic bezier graph)\n'
            '- **Consistency % Score** (pace standard deviation)\n'
            '- **Procedural Mechanical Switch Sound Synthesizer** (0ms latency)\n'
            '- **7 Pro Themes** (Dark Slate, Light, Cyberpunk, Matrix, Dracula, Nord, Sepia)\n'
            '- **100% Offline Standalone** - zero internet connection required after download!\n\n'
            '### Downloads:\n'
            '- **`GPT-TYPE-Setup.exe`** (Recommended for most users - 1-Click Installer)\n'
            '- **`GPT-TYPE.exe`** (Portable Edition - runs without installation)\n'
            '- **`GPT-TYPE-Windows.zip`** (Combined ZIP package)\n'
        ),
        'draft': False,
        'prerelease': False
    }
    req = urllib.request.Request(releases_url, data=json.dumps(release_payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode('utf-8'))
            print('Created release successfully:', release.get('html_url'))
    except Exception as e:
        print('Error creating release:', e)
        sys.exit(1)

release_id = release['id']
upload_url_template = release['upload_url'].split('{')[0]
print(f'Release ID: {release_id}')
print(f'Upload Base URL: {upload_url_template}')

# 4. Upload Assets
assets_to_upload = [
    ('GPT-TYPE-Setup.exe', r'f:\blogger web\GPT-TYPE-Downloads\GPT-TYPE-Setup.exe', 'application/vnd.microsoft.portable-executable'),
    ('GPT-TYPE.exe', r'f:\blogger web\GPT-TYPE-Downloads\GPT-TYPE.exe', 'application/vnd.microsoft.portable-executable'),
    ('GPT-TYPE-Windows.zip', r'f:\blogger web\GPT-TYPE-Downloads\GPT-TYPE-Windows.zip', 'application/zip')
]

existing_assets = {a['name']: a['id'] for a in release.get('assets', [])}

for name, filepath, content_type in assets_to_upload:
    if not os.path.exists(filepath):
        print(f'File not found: {filepath}')
        continue
    
    # If asset already exists in release, delete it first to overwrite
    if name in existing_assets:
        print(f'Deleting old asset {name} (ID: {existing_assets[name]})...')
        del_url = f'https://api.github.com/repos/{username}/{repo_name}/releases/assets/{existing_assets[name]}'
        del_req = urllib.request.Request(del_url, headers=headers, method='DELETE')
        try:
            with urllib.request.urlopen(del_req) as resp:
                print('Deleted old asset.')
        except Exception as e:
            print('Error deleting asset:', e)

    print(f'Uploading {name} ({os.path.getsize(filepath)} bytes)...')
    upload_url = f'{upload_url_template}?name={name}'
    with open(filepath, 'rb') as f:
        file_bytes = f.read()

    upload_headers = {
        'Authorization': f'token {token}',
        'User-Agent': 'GPT-TYPE-Uploader',
        'Content-Type': content_type,
        'Content-Length': str(len(file_bytes))
    }

    req = urllib.request.Request(upload_url, data=file_bytes, headers=upload_headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            asset_data = json.loads(resp.read().decode('utf-8'))
            download_url = asset_data.get('browser_download_url')
            print(f'SUCCESS! {name} uploaded:')
            print(f'  --> Direct Download URL: {download_url}')
    except Exception as e:
        print(f'Error uploading {name}:', e)

print('\n================ ALL DONE ================')
print(f'GitHub Release Page: https://github.com/{username}/{repo_name}/releases/tag/v2.0.0')
