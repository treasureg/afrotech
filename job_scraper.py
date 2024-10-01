import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_jobs():
    # Example: Scraping jobs from a hypothetical job board
    base_url = "https://example-job-board.com"
    response = requests.get(f"{base_url}/jobs")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    for job_element in soup.find_all('div', class_='job-listing'):
        title = job_element.find('h2', class_='job-title').text.strip()
        company = job_element.find('span', class_='company-name').text.strip()
        description = job_element.find('div', class_='job-description').text.strip()
        url = urljoin(base_url, job_element.find('a', class_='job-link')['href'])
        
        jobs.append({
            'title': title,
            'company': company,
            'description': description,
            'url': url
        })
    
    return jobs
