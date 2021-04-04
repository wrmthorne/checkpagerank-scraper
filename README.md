# checkpagerank-scraper
Web scraper for collecting scores from checkpagerank.net/

## Installing Required Modules
```bash
pip install -r requirements.txt
```

## Using the scraper
Supply a domain of the form domain.tld (e.g. amazon.co.uk), (optionally) whether you want the scraped html file to be saved and (optionally) whether you want the results of the scrape output to a json file. Scraped html files are stored in a generated directory html_outputs and json results are stored in json_outputs.

IMPORTANT: Requests should be made no more frequently than every 30 seconds. You will not get any results back from checkpagerank.net and too many requests, too frequently may mean your IP is blacklisted (not tested).

### Full Run
```python
import checkpagerank as cpr

domain = 'amazon.co.uk'

try:
    scores = cpr.get_scores(domain, output=True, json=True)
    print(scores)
    # {'domain': domain, 'last_checked': [date], 'google_pagerank': [score], ...}

except ValueError as e:
    print(e)
    
except RuntimeError as e:
    print(e)
```

### Just Get Page
```python
import checkpagerank as cpr

domain = 'amazon.co.uk'

status_code, content = cpr.get_page(domain)
```

## Batch Processing
Batches of URLs can be provided using the Batch object to scrape many domains at a time. An array of URLs can be provided and each will be scraped with a random delay of 34-60 seconds (to help disguise the scraper). 

```python
from checkpagerank import Batch

domains = ['amazon.co.uk', 'wikipedia.org', 'google.com'] 
b = Batch(domains)
results = b.process()
# {'urls': [urls], 'success': [{scores}], 'failure': [urls]}
```
A range of arguments are provided for a batch:
* fixed_delay: A set interval between requests. Minimum 30 seconds, recommended 34+ seconds
* fld: Converts the provided urls into first-level domain format (e.g. amazon.co.uk) and strips out invalid and duplicate domains
* incremental_dump: Dumps the contents of the scrape to a json file after each success. Recommended for large batches in case of program/system failure. JSON files are stored in json_outputs/batch_#
```python
from checkpagerank import Batch

domains = ['amazon.co.uk', 'wikipedia.org', 'google.com'] 
b = Batch(domains, fixed_delay=34, fld=True, incremental_dump=True)

results = b.process()
print(results)
# {'urls': [urls], 'success': [{scores}], 'failure': [urls]}
```
A number of methods are provided for additional functionality:
* format_urls: Method for formatting urls
* set_fixed_delay: Method for setting the fixed interval delay
* toggle_incremental_dump: Method for setting/unsetting incremental dump
* json_output: Manually dump all the successfull scrapes to json_outputs/batch_# - Will conflict with incremental dump
```python
from checkpagerank import Batch

domains = ['amazon.co.uk', 'wikipedia.org', 'google.com'] 
b = Batch(domains)

b.format_urls()
b.set_fixed_delay = 34
b.toggle_incrementald_dump

results = b.process()
print(results)
# {'urls': [urls], 'success': [{scores}], 'failure': [urls]}

b.json_output # Will conflict with incremental dump
```