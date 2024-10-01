import requests
from urllib.parse import urlencode

def search_jobs(query, location, limit=10):
    # This is a mock implementation. In a real-world scenario, you would use an actual job board API.
    base_url = "https://api.indeed.com/ads/apisearch?"
    params = {
        'publisher': 'YOUR_INDEED_PUBLISHER_ID',  # You would need to sign up for Indeed API to get this
        'q': query,
        'l': location,
        'format': 'json',
        'v': '2',
        'limit': limit
    }
    
    url = base_url + urlencode(params)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['results']
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []

# Mock function for demonstration purposes
def mock_search_jobs(query, location, limit=10):
    job_titles = [
        f'Senior {query} Developer',
        f'{query} Engineer',
        f'Junior {query} Programmer',
        f'{query} Architect',
        f'{query} Team Lead',
        f'{query} Consultant',
        f'Full Stack {query} Developer',
        f'{query} DevOps Engineer',
        f'{query} Data Scientist',
        f'{query} UI/UX Developer'
    ]
    companies = [
        'TechCorp', 'InnovateSoft', 'CodeMasters', 'DataDriven', 'CloudNine',
        'AI Solutions', 'CyberGuard', 'MobileTech', 'WebWizards', 'SmartSystems'
    ]
    return [
        {
            'jobtitle': job_titles[i],
            'company': companies[i],
            'city': location,
            'state': 'Various',
            'country': 'US',
            'snippet': f'We are looking for a talented {job_titles[i].lower()} to join our team...',
            'url': f'https://example.com/job{i+1}',
            'jobkey': f'job_id_{i+1}'
        } for i in range(limit)
    ]
