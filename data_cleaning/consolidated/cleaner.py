def overlap(set_a, set_b):
    return len(set_a.intersection(set_b)) / min(len(set_a), len(set_b)) if min(len(set_a), len(set_b)) > 0 else 0


def sorensen_dice(set_a, set_b):
    return (2* len(set_a.intersection(set_b))) / (len(set_a) + len(set_b)) if len(set_a) + len(set_b) > 0 else 0


def clean_line(line):
    line = line.strip()
    line = line.replace("https://github.com/", "")
    line = line.replace("http://github.com/", "")
    line = line[:-4] if line.endswith(".git") else line
    return line


repos_by_source = dict()  # Key = source, value = set(repo)

file_prefix = "data_cleaning/consolidated/data/"

with open(file_prefix + "bigquery.txt") as f:
    repos_by_source["bigquery"] = set()
    for line in f:
        line = clean_line(line)
        repos_by_source["bigquery"].add(line)

with open(file_prefix + "manual.txt") as f:
    repos_by_source["manual"] = set()
    for line in f:
        line = clean_line(line)
        repos_by_source["manual"].add(line)

with open(file_prefix + "spack.txt") as f:
    repos_by_source["spack"] = set()
    for line in f:
        line = clean_line(line)
        repos_by_source["spack"].add(line)

with open(file_prefix + "webscraping.txt") as f:
    repos_by_source["webscraping"] = set()
    for line in f:
        line = clean_line(line)
        repos_by_source["webscraping"].add(line)


print("Printing raw results")
domains_dict = repos_by_source
unique_repos = set()
for key, value in domains_dict.items():
    print(key, len(value), flush=True, sep="\t")
    unique_repos.update(value)

print("Printing intersections")
domains = sorted(repos_by_source.keys())
for i, d in enumerate(domains):
    for j, e in enumerate(domains):
        if i < j:
            print(d, e, len(domains_dict[d]), len(domains_dict[e]), len(domains_dict[d].intersection(domains_dict[e])), overlap(domains_dict[d], domains_dict[e]), sorensen_dice(domains_dict[d], domains_dict[e]), flush=True, sep="\t")
            #print(d, e, "Sorensen-Dice", sorensen_dice(domains_dict[d], domains_dict[e]))

with open("data_cleaning/consolidated/unique_repos.txt", "w") as f:
    for r in sorted(unique_repos):
        f.write(r + "\n")
