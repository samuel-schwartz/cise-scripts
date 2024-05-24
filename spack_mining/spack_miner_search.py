import os
import re


def overlap(set_a, set_b):
    return len(set_a.intersection(set_b)) / min(len(set_a), len(set_b)) if min(len(set_a), len(set_b)) > 0 else 0

def sorensen_dice(set_a, set_b):
    return (2* len(set_a.intersection(set_b))) / (len(set_a) + len(set_b)) if len(set_a) + len(set_b) > 0 else 0



class Package:
    def __init__(self, name) -> None:
        self.name = name # Package name
        self.homepage = "" # Homeepage

        self.url = "" # Tarball location

        # Location of the version control system (usually will have only one)
        self.git = "" # Git VCS
        self.hg = "" # Mercurial (hg) VCS
        self.svn = "" # Subversion VCS
        self.cvs = "" # CSV VCS
        self.go = "" # Go VCS

        # Search query hits

        self.search_query_findings = set()

        # Dependencies
        self.depends_on = set()

    def gov_source(self):
        return ".gov" in self.homepage or ".gov" in self.url
    
    def edu_source(self):
        return ".edu" in self.homepage or ".edu" in self.url

    def __str__(self) -> str:
        return str(self.name) + "\t" + str(self.homepage) + "\t" + str(self.url) + "\t" + str([_ for _ in self.depends_on])

search_queries = ["Ames National Laboratory",
                "Ames",
                "Ames Lab",
                "ameslab.org",
                "Argonne National Laboratory",
                "Argonne",
                "anl",
                "anl.gov",
                "Brookhaven",
                "Brookhaven National Laboratory",
                "BNL",
                "bnl.gov",
                "Fermi National Accelerator Laboratory",
                "Fermi",
                "FNAL",
                "fnal.gov",
                "Idaho",
                "INL",
                "Idaho National Laboratory",
                "inl.gov",
                "Lawrence Berkeley National Laboratory",
                "LBNL",
                "Lawrence Berkeley",
                "lbl.gov",
                "Lawrence Livermore National Laboratory",
                "Lawrence Livermore",
                "LLNL",
                "llnl.gov",
                "Los Alamos National Laboratory",
                "Los Alamos",
                "LANL",
                "lanl.gov",
                "National Energy Technology Laboratory",
                "NETL",
                "netl.doe.gov",
                "National Renewable Energy Laboratory",
                "NREL",
                "nrel.gov",
                "Oak Ridge National Laboratory",
                "Oak Ridge",
                "ORNL",
                "ornl.gov",
                "Pacific Northwest",
                "Pacific Northwest National Laboratory",
                "pnnl.gov",
                "PNNL",
                "Princeton Plasma Physics Laboratory",
                "PPPL",
                "pppl.gov",
                "SLAC National Accelerator Laboratory",
                "SLAC",
                "SLAC NAL",
                "slac.stanford.edu",
                "Sandia",
                "SNL",
                "Sandia National Laboratory",
                "sandia.gov",
                "Savannah River National Laboratory",
                "Savannah River",
                "SRNL",
                "srnl.doe.gov",
                "Thomas Jefferson National Accelerator Laboratory",
                "TJNAL",
                "Jefferson Laboratory",
                "jlab.org",
                "Energy",
                "DOE",
                "doe.gov",
                "energy.gov",
                "Department of Energy"]

search_queries_all_repos = dict() # Key = search query, value = set(repos)

for sq in search_queries:
    search_queries_all_repos[sq] = set()

def process_package(filename, package_name):
    p = Package(package_name)
    with open(filename, "r+") as f:
        lines = f.readlines()
        text_lower = ""
        for line in lines:
            if "copyright" not in line.lower() and "github.com/llnl/spack" not in line.lower():
                text_lower += line.lower() + "\n"
            line = line.strip()
            if "homepage =" in line:
                p.homepage = line.split("=")[1].strip()
            elif "url =" in line:
                p.url = line.split("=")[1].strip()
            elif "git =" in line:
                p.git = line.split("=")[1].strip()
            elif "hg =" in line:
                p.hg = line.split("=")[1].strip()
            elif "svn =" in line:
                p.svn = line.split("=")[1].strip()
            elif "cvs =" in line:
                p.cvs = line.split("=")[1].strip()
            elif "go =" in line:
                p.go = line.split("=")[1].strip()
            elif "depends_on(" in line and "#" != line[0] and "'" != line[0] and '"' != line[0]: # Make sure it doesn't start with a comment or string
                dep_on = line
                dep_on = dep_on[len("depends_on("):].split(",")[0] # Remove qualifiers (e.g., depends on X "when" Y)
                dep_on = dep_on.split("+")[0].split("~")[0] # Remove special options from dependency
                dep_on = dep_on.split(" ")[0]
                dep_on = dep_on.split(".")[0]
                dep_on = dep_on.split("[")[0]
                dep_on = dep_on.split("]")[0]
                dep_on = dep_on.split(":")[0]
                dep_on = dep_on.split("^")[0]
                dep_on = dep_on.split("*")[0]
                dep_on = dep_on.split("=")[0]
                dep_on = dep_on.split("&")[0]
                dep_on = dep_on.split("@")[0] # Remove version information from dependency
                dep_on = dep_on.replace("'", "").replace('"', '').replace("(", "").replace(")", "") # Remove errent quotes and parens
                dep_on = dep_on.strip()
                if dep_on != "" and "%" not in dep_on:
                    p.depends_on.add(dep_on)
        
        for sq in search_queries:
            if re.search("(^|[^A-Za-z])" + sq.lower() + "($|[^A-Za-z])", text_lower):
                p.search_query_findings.add(sq)
                if "://github.com/" in p.git:
                    search_queries_all_repos[sq].add(p.git)
    return p

def run():
    spack_dir_root = "spack_mining/spack/var/spack/repos/builtin/packages/"
    results = os.listdir(spack_dir_root)
    packages = dict() # Key = package name, value = package object
    for i, r in enumerate(results):
        if i % 100 == 0:
            print("Working on ", i, "of", len(results), round((100 * i) / len(results), 2))
        filename = spack_dir_root + "/" + r + "/package.py"
        p = process_package(filename, r)
        packages[r] = p

    print()
    print()
    print()


    print("Repos per query")
    for sq in search_queries:
        print(sq, "\t", len(search_queries_all_repos[sq]))

    print("Interactions")

    for i, d in enumerate(search_queries):
        for j, e in enumerate(search_queries):
            if i <= j and d in search_queries_all_repos.keys() and e in search_queries_all_repos.keys() and len(search_queries_all_repos[d].intersection(search_queries_all_repos[e])) > 0:
                print(d, e, 
                            len(search_queries_all_repos[d]), 
                            len(search_queries_all_repos[e]), 
                            len(search_queries_all_repos[d].intersection(search_queries_all_repos[e])), 
                            overlap(search_queries_all_repos[d], search_queries_all_repos[e]), 
                            sorensen_dice(search_queries_all_repos[d], search_queries_all_repos[e]), flush=True, sep="\t")
    
    unique_repos = set()
    for sq in search_queries:
        print(sq)
        for package_name, package in packages.items():
            if sq in package.search_query_findings and "://github.com/" in package.git:
                unique_repos.add(package.git.replace('"', '').strip())

    with open("data_cleaning/consolidated/data/spack.txt", "w") as f:
        for r in sorted(unique_repos):
            f.write(r + "\n")

"""
    for sq in search_queries:
        print(sq)
        for package_name, package in packages.items():
            if sq in package.search_query_findings and "://github.com/" in package.git:
                print("\t" + package_name + "\t" + package.git.replace('"', ''))

"""

run()