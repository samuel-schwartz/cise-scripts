import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
import re
import datetime

class EmailSpider(scrapy.Spider):
    # Scrapy has many settings as static, class level variables. These are set below

    name = "NatLabSpider"
    custom_settings = { # These settings will have scrapy do a breadth first search instead of a depth first search.
        'DEPTH_PRIORITY': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue'
    }

    """
    Focusing on the 17 national laboritories:

    Ames Laboratory
    Argonne National Laboratory
    Brookhaven National Laboratory
    Fermi National Accelerator Laboratory
    Idaho National Laboratory
    Lawrence Berkley National Laboratory
    Lawrence Livermore National Laboratory
    Los Alamos National Laboratory
    National Energy Technology Laboratory
    National Renewable Energy Laboratory
    Oak Ridge National Laboratory
    Pacific Northwest National Laboratory
    Princeton Plasma Physicis Laboratory
    SLAC National Accelerator Laboratory
    Sandia National Laboratory
    Savannah River National Laboratory
    Thomas Jeferson National Accelerator Facility
    """

    allowed_domains = [
        '*.orau.gov', 'orau.gov', 'energy.gov', 'ameslab.gov', 'anl.gov',
        'bnl.govworld', 'fnal.gov', 'inl.gov', 'lbl.gov', 'llnl.gov',
        'lanl.gov', 'netl.doe.gov', 'nrel.gov', 'ornl.gov', 'pnnl.gov',
        'pppl.gov', 'slac.stanford.edu', 'sandia.gov', 'srnl.doe.gov',
        'jlab.org', '*.energy.gov', '*.ameslab.gov', '*.anl.gov',
        '*.bnl.govworld', '*.fnal.gov', '*.inl.gov', '*.lbl.gov', '*.llnl.gov',
        '*.lanl.gov', '*.netl.doe.gov', '*.nrel.gov', '*.ornl.gov',
        '*.pnnl.gov', '*.pppl.gov', '*.slac.stanford.edu', '*.sandia.gov',
        '*.srnl.doe.gov', '*.jlab.org'
    ]

    # Plutting start method above init so that allowed_domains and urls are close in proximity.
    # Generally, the start urls will be the http version of the allowed domains, although not always.
    def start_requests(self):
        urls = [
             'https://www.energy.gov',
             'https://www.ameslab.gov/',
             'https://www.anl.gov/',
             'https://www.bnl.gov/world/',
             'https://www.fnal.gov/',
             'https://inl.gov/',
             'https://www.lbl.gov/',
             'https://www.llnl.gov/',
             'https://lanl.gov/',
             'https://netl.doe.gov/',
             'https://www.nrel.gov/',
             'https://www.ornl.gov/',
             'https://www.pnnl.gov/',
             'https://www.pppl.gov/',
             'https://www6.slac.stanford.edu/',
             'https://www.sandia.gov/',
             'https://srnl.doe.gov/',
             'https://www.jlab.org/'
            ]
        for url in urls:
            source_url_id = self.get_id_from_page_url(url)
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(depth=0, source_id=source_url_id))

    def __init__(self):
        self.link_extractor = LinkExtractor()
        self.repo_regex = r"(\S*github\.com\S*)|(\S*gitlab\.com\S*)|(\S*github\.io\S*)"  # Finds URLS with github, gitlab, etc. in the text.

        self.url_ids = dict()

        filename = '-{date:%Y-%m-%d-%H-%M-%S}.csv'.format(date=datetime.datetime.now())
        self.url_id_file = open("data/url_id" + filename, "w")  # A CSV file with two columns: the page URL, and a unique ID
        self.paths_file = open("data/paths" + filename, "w")  # A CSV file with two columns: source URL ID, target URL ID
        self.repos_file = open("data/repos" + filename, "w")  # A CSV file with two columns: page URL ID, scraped repository url

    def get_id_from_page_url(self, page_url):
        if page_url in self.url_ids:
            return self.url_ids[page_url]
        else:
            value = len(self.url_ids.keys())
            self.url_ids[page_url] = value
            print(page_url, ",", str(value), file=self.url_id_file, flush=True)
            return self.url_ids[page_url]

    def parse(self, response, depth, source_id):

        # Add an additional link if the server gives a redirect
        resolved_source_id = self.get_id_from_page_url(response.url)
        if source_id != resolved_source_id:
            print(str(source_id), ",", str(resolved_source_id), file=self.paths_file, flush=True)

        # Get all repositories from the webpage
        repo_list = re.findall(self.repo_regex, response.text)

        # Add the found repositories to the repos file, linked to the resolved page id
        for repo_url in repo_list:
            repo_url = str(repo_url).strip().lower()
            print(str(resolved_source_id), ",", repo_url, file=self.repos_file, flush=True)

        # Look at all the other links on the page; add them to queue to traverse. Add links to edge list.
        if depth >= 0:
            extracted_links = self.link_extractor.extract_links(response)
            print("Depth:", depth, "Num Links", len(extracted_links))
            for link in extracted_links:
                target_id = self.get_id_from_page_url(link.url)
                print(str(resolved_source_id), ",", str(target_id), file=self.paths_file, flush=True)
                yield Request(link.url, callback=self.parse, cb_kwargs=dict(depth=depth+1, source_id=target_id))
