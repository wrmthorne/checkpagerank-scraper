'''
Scrapes scores shown on checkpagerank.net for a given domain.

Domains supplied should be first-level domains without protocol, sub-domain
and path(e.g. amazon.co.uk). Setting output to true will write the html content
of a scrape to html_outputs. 30 seconds must be left between each scrape attempt.
'''
import os, requests, time, json
from datetime import date
from bs4 import BeautifulSoup


def output_html(soup):
    '''
    Outputs soup contents to html file in 'html_outputs' directory

        Parameters:
            soup (bytes): soup object as output from BeautifulSoup to write to file
    '''
    # Check to see which indices of file exist and add new increment
    i = 1
    while os.path.isfile('html_outputs/output_{}.html'.format(i)):
        i += 1
    filename = 'html_outputs/output_{}.html'.format(i)

    # Create directory if it doesnt exist and write to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write(str(soup))


def output_json(scores):
    '''
    Outputs scraped scores to json file in 'json_outputs' directory

        Parameters:
            scores (dict): dict of scraped scores
    '''
    # Check to see whether a version of the file exists and increment if it does
    formatted_domain = scores['domain'].split('.')[0] # Gets just domain without tld
    if not os.path.isfile('json_outputs/{}.json'.format(formatted_domain)):
        filename = 'json_outputs/{}.json'.format(formatted_domain)
    else:
        i = 1
        while os.path.isfile('json_outputs/{}_{}.json'.format(formatted_domain, i)):
            i += 1
        filename = 'json_outputs/{}_{}.json'.format(formatted_domain, i)

    # Create directory if it doesnt exist and write to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w+') as f:
        json.dump(scores, f)


def get_page(domain):
    '''
    Retrieves the html for checkpagerank with the query results for the given domain

        Parameters:
            domain (str): first-level domain (fld) e.g. amazon.co.uk

        Returns:
            r.content (bytes): HTML content returned from checkpagerank.net
    '''
    url = 'https://checkpagerank.net/check-page-rank.php'
    headers = {'referrer': 'https://www.google.com/'}
    payload = {'name': str(domain)}

    r = requests.post(url, headers=headers, data=payload)

    return (r.status_code, r.content)


def get_scores(domain, output=False, json=False):
    '''
    Parses the HTML from checkpagerank.net with the domain query and extracts the different scores

        Parameters:
            domain (str): web-domain and top-level domain(s) e.g. amazon.co.uk
            output (bool, optional): Outputs the html content to an html file
            json (bool, optional): Outputs scraped scores to json file

        Returns:
            scores (dict): Data scraped from checkpagerank.net

        Raises:
            RuntimeError: Error while contacting checkpagerank.net
            ValueError: No results found on page, likely because you made more than one request in 30s
    '''
    status_code, content = get_page(domain)
    if not status_code == 200:
        raise RuntimeError('Error while contacting checkpagerank.net: {}'.format(status_code))

    soup = BeautifulSoup(content, 'html.parser')
    if (output):
        output_html(soup)

    results_container = soup.find(id='html-2-pdfwrapper')
    if results_container == None:
        raise ValueError('No results found on page, likely because you made more than one request in 30s')

    scores = {}
    results = results_container.text.strip().replace('\t', '').split('\n')[2:-1]

    scores['domain'] = domain
    scores['last_checked'] = results[0].split(': ')[1]
        
    for field in results[1:]:
        key, value = field.split(': ')
        key = key.lower().replace(' ', '_')
        scores[key] = value

    if json:
        output_json(scores)

    return(scores)


if __name__ == '__main__':
    # Example usage
    domain = 'amazon.co.uk'
    try:
        scores = get_scores(domain, output=True, json=True)
        print(scores)
        
    except ValueError as e:
        print(e)

    except RuntimeError as e:
        print(e)