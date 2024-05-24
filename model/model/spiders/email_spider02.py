import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy import Request
import re
import datetime
import os
from multiprocessing import Process, Queue

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
        '*.ameslab.gov', 'ameslab.gov', '*.anl.gov', 'anl.gov', '*.arm.gov',
        'arm.gov', '*.battelle.org', 'battelle.org', '*.bnl.gov', 'bnl.gov',
        '*.caes.org', 'caes.org', '*.caesenergy.org', 'caesenergy.org',
        '*.casl.gov', 'casl.gov', '*.cymanii.org', 'cymanii.org', '*.doe.gov',
        'doe.gov', '*.e3sm.org', 'e3sm.org', '*.energy.gov', 'energy.gov',
        '*.fnal.gov', 'fnal.gov', '*.hanford.gov', 'hanford.gov', '*.inl.gov',
        'inl.gov', '*.jcesr.org', 'jcesr.org', '*.jlab.org', 'jlab.org',
        '*.labpartnering.org', 'labpartnering.org', '*.lanl.gov', 'lanl.gov',
        '*.lbl.gov', 'lbl.gov', '*.llnl.gov', 'llnl.gov', '*.nationallabs.org',
        'nationallabs.org', '*.nersc.gov', 'nersc.gov'
        '*.netl.doe.gov', 'netl.doe.gov', '*.nrel.gov', 'nrel.gov',
        '*.orau.gov', 'orau.gov', '*.ornl.gov', 'ornl.gov', '*.osti.gov',
        'osti.gov', '*.osti.gov', 'osti.gov', '*.pnl.gov', 'pnl.gov',
        '*.pnnl.gov', 'pnnl.gov', '*.pppl.gov', 'pppl.gov', '*.sandia.gov',
        'sandia.gov', '*.slac.stanford.edu', 'slac.stanford.edu',
        '*.srnl.doe.gov', 'srnl.doe.gov', '*.srs.gov', 'srs.gov',
        '*.uchicagoargonnellc.org', 'uchicagoargonnellc.org',
        '*.ut-battelle.org', 'ut-battelle.org'
    ]

    # Plutting start method above init so that allowed_domains and urls are close in proximity.
    # Generally, the start urls will be the http version of the allowed domains, although not always.
    def start_requests(self):
        urls = [
             'https://www.energy.gov',
             'https://www.ameslab.gov/',
             'https://www.anl.gov/',
             'https://www.bnl.gov/',
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
        
        tasks = []
        yeild_q = Queue()
        for url in urls:
            p = Process(target=self._start_request_task, args=(url, yeild_q))
            tasks.append(p)
        
        for t in tasks:
            t.start()

        with open(self.url_id_filename, "a+") as url_id_file:
            with open(self.paths_filename, "a+") as paths_file:
                with open(self.repos_filename, "a+") as repos_file:
                    while EmailSpider._tasks_alive(tasks) or not self.url_id_file_q.empty() or not self.paths_file_q.empty() or not self.repos_file_q.empty():
                        if not self.url_id_file_q.empty():
                            try:
                                value = self.url_id_file_q.get(timeout=1)
                                url_id_file.write(str(value) + "\n")
                            except:
                                pass
                        if not self.paths_file_q.empty():
                            try:
                                value = self.paths_file_q.get(timeout=1)
                                paths_file.write(str(value) + "\n")
                            except:
                                pass
                        if not self.repos_file_q.empty():
                            try:
                                value = self.repos_file_q.get(timeout=1)
                                repos_file.write(str(value) + "\n")
                            except:
                                pass

        for t in tasks:
            t.join()

        
    def _write_to_file_multi_thread(self, tasks, filename, queue):
        with open(filename, "a+") as file:
            while EmailSpider._tasks_alive(tasks) or not queue.empty():
                try:
                    value = queue.get(timeout=1)
                    file.write(str(value) + "\n")
                except:
                    pass
            
    @staticmethod
    def _tasks_alive(tasks):
        for t in tasks:
            if t.is_alive():
                return True
        return False

    def _start_request_task(self, url, yeild_q):
        source_url_id = self.get_id_from_page_url(url)
        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(depth=0, source_id=source_url_id))

    def __init__(self):

        # Set up link extraction
        self.link_extractor = LinkExtractor()
        self.repo_regex = r"(\S*github\.com\S*)|(\S*gitlab\.com\S*)|(\S*github\.io\S*)"  # Finds URLS with github, gitlab, etc. in the text.

        # Set up url 'hashing'
        self.url_ids = dict()

        # Set up output file names
        filename = '{date:%Y-%m-%d-%H-%M-%S}'.format(date=datetime.datetime.now())
        os.mkdir("data/" + filename)
        self.url_id_filename = "data/" + filename + "/url_id.csv"  # A CSV file with two columns: the page URL, and a unique ID
        self.paths_filename = "data/" + filename + "/paths.csv" # A CSV file with two columns: source URL ID, target URL ID
        self.repos_filename = "data/" + filename + "/repos.csv" # A CSV file with two columns: page URL ID, scraped repository url
        self.internal_log = filename + ".log"

        # Set up multithreading write queues
        self.url_id_file_q = Queue()
        self.paths_file_q = Queue()
        self.repos_file_q = Queue()
        

    def get_id_from_page_url(self, page_url):
        if page_url in self.url_ids.keys():
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
            self.paths_file_q.put(str(source_id) + "," + str(resolved_source_id))

        # Get all repositories from the webpage
        repo_list = re.findall(self.repo_regex, response.text)

        # Add the found repositories to the repos file, linked to the resolved page id
        for repo_url in repo_list:
            repo_url = str(repo_url).strip().lower()
            self.repos_file_q.put(str(resolved_source_id) + "," + repo_url)

        # Look at all the other links on the page; add them to queue to traverse. Add links to edge list.
        if depth >= 0:
            extracted_links = self.link_extractor.extract_links(response)
            with open(self.internal_log, "a+") as f:
                f.write("Depth: " + str(depth) + "; Num Links from this page: " + str(len(extracted_links)) +  "; Number in queue: " + str(len(self.crawler.engine.slot.scheduler)))
            for link in extracted_links:
                target_id = self.get_id_from_page_url(link.url)
                self.paths_file_q.put(str(resolved_source_id) + "," + str(target_id))
                yield Request(link.url, callback=self.parse, cb_kwargs=dict(depth=depth+1, source_id=target_id))
