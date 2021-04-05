'''
Scrapes scores shown on checkpagerank.net for a given domain.

Domains supplied should be first-level domains without protocol, sub-domain
and path(e.g. amazon.co.uk). Setting output to true will write the html content
of a scrape to html_outputs. 30 seconds must be left between each scrape attempt.
'''
import os, requests, time, json, random, asyncio, datetime, threading
from bs4 import BeautifulSoup
from tld import get_fld


def output_html(soup, path='.'):
    '''
    Outputs soup contents to html file in 'html_outputs' directory

        Parameters:
            soup (bytes): soup object as output from BeautifulSoup to write to file
            path (str, optional): path of where to create/use the html_outputs directory
    '''
    # Check to see which indices of file exist and add new increment
    if path.strip().endswith('/'):
        path = path.strip()[:-1]

    i = 1
    while os.path.isfile(f'html_outputs/output_{i}.html'):
        i += 1
    filename = f'html_outputs/output_{i}.html'

    # Create directory if it doesnt exist and write to file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write(str(soup))


def output_json(scores, path='.'):
    '''
    Outputs scraped scores to json file in 'json_outputs' directory

        Parameters:
            scores (dict): dict of scraped scores
            path (str, optional): path of where to create/use the json_outputs directory
    '''
    # Check to see whether a version of the file exists and increment if it does
    formatted_domain = scores['domain'].strip().split('.')[0] # Gets just domain without tld
    if path.strip().endswith('/'):
        path = path.strip()[:-1]
        
    if not os.path.isfile(f'{path}/json_outputs/{formatted_domain}.json'):
        filename = 'json_outputs/{formatted_domain}.json'
    else:
        i = 1
        while os.path.isfile(f'json_outputs/{formatted_domain}_{i}.json'):
            i += 1
        filename = f'json_outputs/{formatted_domain}_{i}.json'

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


def convert_to_fld(url):
    '''Converts url to first-level domain (fld)'''
    # Checks to see if the url is already in fld format
    if get_fld(f'https://{url}', fail_silently=True):
        return url
    try:
        return get_fld(url)
    except:
        print('{} is an invalid url'.format(url))


def get_scores(domain, output=False, json=False, fld=False):
    '''
    Parses the HTML from checkpagerank.net with the domain query and extracts the different scores

        Parameters:
            domain (str): web-domain and top-level domain(s) e.g. amazon.co.uk
            output (bool, optional): Outputs the html content to an html file
            json (bool, optional): Outputs scraped scores to json file
            fld (bool, optional): Coverts provided URL to fld if not already 

        Returns:
            scores (dict): Data scraped from checkpagerank.net

        Raises:
            RuntimeError: Error while contacting checkpagerank.net
            ValueError: No results found on page, likely because you made more than one request in 30s
    '''
    status_code, content = get_page(domain)
    if not status_code == 200:
        raise RuntimeError(f'Error while contacting checkpagerank.net: {status_code}')

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

    return scores


class Batch:
    def __init__(self, urls: [str], fixed_delay=False, fld=False, incremental_dump=False):
        print(f'Provided number of urls: {len(urls)}')
        self.urls = list(set(urls)) # Remove duplicates
        if fld:
            self.format_urls()

        if not fixed_delay == False and fixed_delay < 30:
            raise ValueError('Delay must be more than 30 seconds')
        else:
            self.fixed_delay = fixed_delay
        
        self.incremental_dump = incremental_dump
        self.failures = []
        self.successes = []

    def format_urls(self):
        '''Reformat URLs in first-level (fld) domain format'''
        self.urls = list(set([convert_to_fld(url) for url in self.urls]))
        print(f'Formatted number of urls: {len(self.urls)}')

    def set_fixed_delay(self, delay: int):
        '''Force each request to be made after a set delay'''
        if delay < 30:
            raise ValueError('Delay must be more than 30 seconds')
        self.fixed_delay = int(delay)

    def toggle_incremental_dump(self):
        '''Toggles whether the class should dump scraped results as they are collected'''
        self.incremental_dump = not self.incremental_dump

    def json_output(self):
        '''Writes all successes to json'''
        [self.__dump_json(s) for s in self.successes]

    def __dump_json(self, scores, path='./json_outputs'):
        '''Writes scores to JSON files in a batch directory'''
        name = scores['domain']
        if path.strip().endswith('/'):
            path = path.strip()[:-1]
            
        i = 1
        while os.path.isfile(f'{path}/batch_{i}/{name}.json'):
            i += 1
        filename = f'{path}/batch_{i}/{name}.json'

        # Create directory if it doesnt exist and write to file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w+') as f:
            json.dump(scores, f)

    def __make_request(self, url: str):
        '''Handles a single batch process and sorts the results'''
        try:
            print(f'Starting: {url}')
            start = time.time()
            scores = get_scores(url)
            print(f'SUCCESS: {url} ({time.time() - start}s)')

            self.successes.append(scores)
            if self.incremental_dump:
                self.__dump_json(scores)

        except ValueError as e:
            print(f'FAILURE: {url} ({e})')
            self.failures.append(url)
            
        except RuntimeError as e:
            print(f'FAILURE: {url} ({e})')
            self.failures.append(url)

    def process(self):
        '''Handles the processing of each item in the batch.

            Returns:
                results (dict): Results dict for urls, success, and failures

            Raises:
                ValueError: No URLs to Process
        '''
        no_urls = len(self.urls) # Number of urls to process
        if no_urls == 0:
            raise ValueError("No URLs to Process")

        if not self.fixed_delay:
            delays = [random.randrange(34, 60, 1) for i in range(len(self.urls) - 1)]
        else:
            delays = [self.fixed_delay for i in range(len(self.urls) - 1)]

        batch_start = time.time()
        print('===================================')
        print(f'Starting batch: {len(self.urls)} items')
        print(f'Estimated Runtime: {datetime.timedelta(seconds=sum(delays) + 30)}')
        print('===================================')
        threads = []
        while self.urls:
            url = self.urls.pop(0)
            t = threading.Thread(target=self.__make_request, args=(url,))
            threads.append(t)

        for i in range(len(threads)):
            if i % 5 == 0:
                print(f'Estimated time remaining: {datetime.timedelta(seconds=sum(delays) + 30)}')
            threads[i].start()
            if delays:
                time.sleep(delays.pop(0))

        # Ensures that all threads are complete
        [thread.join() for thread in threads]

        batch_duration = datetime.timedelta(seconds=time.time() - batch_start)
        print('===================================')
        print(f'Batch Complete: {batch_duration}')
        print(f'{no_urls} Processed, {len(self.successes)} Successes, {len(self.failures)} Failures')
        print('===================================')

        return {'urls': self.urls, 'success': self.successes, 'failure': self.failures}


if __name__ == '__main__':
    # Example usage
    '''domain = 'amazon.co.uk'
    try:
        scores = get_scores(domain, output=True, json=True)
        print(scores)
        
    except ValueError as e:
        print(e)

    except RuntimeError as e:
        print(e)'''

    # Batch Processing
    domains = ['amazon.co.uk', 'wikipedia.org', 'google.com'] 
    b = Batch(domains, incremental_dump=True)
    print(b.process())