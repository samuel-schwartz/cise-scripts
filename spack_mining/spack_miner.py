import os

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

        # Dependencies
        self.depends_on = set()

    def gov_source(self):
        return ".gov" in self.homepage or ".gov" in self.url
    
    def edu_source(self):
        return ".edu" in self.homepage or ".edu" in self.url

    def __str__(self) -> str:
        return str(self.name) + "\t" + str(self.homepage) + "\t" + str(self.url) + "\t" + str([_ for _ in self.depends_on])

def process_package(filename, package_name):
    p = Package(package_name)
    with open(filename, "r+") as f:
        lines = f.readlines()
        for line in lines:
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
        
    return p

def write_dependency_dot_file(packages):
    """
    Writes a .dot file for graphing purposes. Edges indicate dependency
    """
    
    with open("spack_mining/dependency.dot", "w+") as f:

        f.write("digraph D {\n")
        for p in packages:
            if len(p.depends_on) > 0:
                p_name = p.name.replace("-", "_")
                f.write(p_name)
                if p.gov_source():
                    f.write("[shape=diamond]")
                elif p.edu_source():
                    f.write("[shape=square]")
                f.write("\n")

        for p in packages:
            p_name = p.name.replace("-", "_")
            for dep in p.depends_on:
                f.write(p_name + " -> " + dep.replace("-", "_") + "\n")

        f.write("}")

def run():
    spack_dir_root = "spack_mining/spack-packages/"
    results = os.listdir(spack_dir_root)
    packages = dict() # Key = package name, value = package object
    for i, r in enumerate(results):
        print("Working on ", i, "of", len(results), round((100 * i) / len(results), 2))
        filename = spack_dir_root + "/" + r + "/package.py"
        p = process_package(filename, r)
        packages[r] = p

    write_dependency_dot_file(packages.values())

    for p in packages.values():
        if p.gov_source() or p.edu_source():
            print(p.name, p.homepage, p.url)

