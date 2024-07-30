from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


def extract_subdomains(html):
    soup = BeautifulSoup(html, 'html.parser')
    subdomains = []

    table = soup.find('table', class_='table table-striped text-white')
    if table:
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    subdomain = cells[0].text.strip()
                    last_seen = cells[1].text.strip()
                    subdomains.append({
                        'subdomain': subdomain,
                        'last_seen': last_seen
                    })

    return subdomains


@app.route('/api', methods=['GET'])
def get_subdomains():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({'error': 'Domain parameter is required'}), 400

    url = 'https://subdomainfinder.io/'
    headers = {
        'Host': 'subdomainfinder.io',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'en-US',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://subdomainfinder.io',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36',
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://subdomainfinder.io/',
        'Priority': 'u=0, i',
    }

    data = {
        'domain': domain,
        'scan': '',
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        subdomains = extract_subdomains(response.text)
        return jsonify(subdomains)
    else:
        return jsonify(
            {'error': f'Failed to fetch data: {response.status_code}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
