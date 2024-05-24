# Set up class definition 
class Repo:
    def __init__(self, name) -> None:
        self.name = name
        self.ids = set()
        self.urls = set()
        self.domains = set()

def overlap(set_a, set_b):
    return len(set_a.intersection(set_b)) / min(len(set_a), len(set_b)) if min(len(set_a), len(set_b)) > 0 else 0

def sorensen_dice(set_a, set_b):
    return (2* len(set_a.intersection(set_b))) / (len(set_a) + len(set_b)) if len(set_a) + len(set_b) > 0 else 0

# Set up container for repos
repos = set()

file_prefix = "data_cleaning/web_scraping/data/"


print("Adding Repos", flush=True)
# Add unique repos
with open(file_prefix + "list_unique_repos3.txt", "r") as f:
    for line in f:
        repos.add(Repo(line.strip()))

print("Getting Repo IDs", flush=True)
# Add all of the repo ids, including subids (e.g., both 1 and 2 in [1, github.com/org/repo] and [2, github.com/org/repo/issue])
with open(file_prefix + "repos.csv", "r") as f:
    for line in f:
        for r in repos:
            if r.name in line:
                r.ids.add(int(line.split(",")[0]))


print("Getting Urls", flush=True)
with open(file_prefix + "url_id.csv", "r") as f:
    ff = f.readlines()
    for id, line in enumerate(ff):
        line = line.strip()
        if id % 10000 == 0:
            print(round(100 * id / len(ff), 2), id, len(ff), flush=True)

        comps = line.split(",")
        id = int(comps[-1])
        url = comps[0] if len(comps) == 2 else ','.join(comps)
        for r in repos:
            if id in r.ids:
                r.urls.add(url)

print("Aggregating URLs by domain")
domains = ["ameslab.gov", "anl.gov", "bnl.gov", "energy.gov", "fnal.gov", "inl.gov", "jlab.org", "lanl.gov", "lbl.gov", "llnl.gov", "netl.doe.gov", "nrel.gov", "ornl.gov", "pnnl.gov", "pppl.gov", "sandia.gov", "slac.stanford.edu", "srnl.doe.gov"]

domains_dict = dict() # Key = domain, value = set() of repos
for d in domains:
    domains_dict[d] = set()


cleaned_repos = set()

for r in repos:
    for u in r.urls:
        for d in domains:
            if d in u:
                if d == "anl.gov":
                    if "lanl.gov" not in u:
                        domains_dict[d].add(r.name)
                        cleaned_repos.add(r.name)
                else:
                    domains_dict[d].add(r.name)
                    cleaned_repos.add(r.name)

print("Printing raw results")
for key, value in domains_dict.items():
    print(key, len(value), flush=True)

print("Printing intersections")
for i, d in enumerate(domains):
    for j, e in enumerate(domains):
        if i <= j:
            print(d, e, len(domains_dict[d]), len(domains_dict[e]), len(domains_dict[d].intersection(domains_dict[e])), overlap(domains_dict[d], domains_dict[e]), sorensen_dice(domains_dict[d], domains_dict[e]), flush=True)
            #print(d, e, "Sorensen-Dice", sorensen_dice(domains_dict[d], domains_dict[e]))

with open("data_cleaning/consolidated/data/webscraping.txt", "w") as f:
    for r in sorted(cleaned_repos):
        f.write(str(r) + "\n")