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