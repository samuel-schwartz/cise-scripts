def overlap(set_a, set_b):
    return len(set_a.intersection(set_b)) / min(len(set_a), len(set_b)) if min(len(set_a), len(set_b)) > 0 else 0

def sorensen_dice(set_a, set_b):
    return (2* len(set_a.intersection(set_b))) / (len(set_a) + len(set_b)) if len(set_a) + len(set_b) > 0 else 0


# Set up container for repos
search_queries_search_finding_repos = dict() # Key = search query, value = set([search_findings repos])
search_queries_all_repos = dict() # Key = search query, value = set([all repos, both search findings and relevant organizations])
search_queries_info = dict() # Key = search query, value = # of web results
keys_list = list() # List of keys, in the order they appear
all_repos = set() # Set of all repos

file_prefix = "data_cleaning/manual_searching/data/"

print("Adding Repos", flush=True)
# Add unique repos
with open(file_prefix+"MildlyCleanedGitHubSearchResults.csv", "r") as f:
    current_search_query = ""

    for line in f.readlines()[1:]:
        # Do Cleaning
        line = line.strip()
        search_query, results_found, repo, find_type = line.split(",")
        search_query = search_query.strip()
        results_found = results_found.strip()
        repo = repo.strip()
        find_type = find_type.strip()

        # Determine if we need to switch repo type
        if search_query != "":
            current_search_query = search_query
            keys_list.append(current_search_query)
            search_queries_info[current_search_query] = [int(results_found), 0, 0, 0]
            continue

        # Add to sets
        if current_search_query not in search_queries_search_finding_repos.keys():
            search_queries_search_finding_repos[current_search_query] = set()

        if current_search_query not in search_queries_all_repos.keys():
            search_queries_all_repos[current_search_query] = set()

        # Add to appropreate sets
        if find_type == "Search Finding":
            search_queries_search_finding_repos[current_search_query].add(repo)
            search_queries_all_repos[current_search_query].add(repo)
            all_repos.add(repo)
            [web_results, search_finding, umbrella_finding, all_results] = search_queries_info[current_search_query]
            search_queries_info[current_search_query] = [web_results, search_finding+1, umbrella_finding, all_results+1]
        else:
            search_queries_all_repos[current_search_query].add(repo)
            all_repos.add(repo)
            [web_results, search_finding, umbrella_finding, all_results] = search_queries_info[current_search_query]
            search_queries_info[current_search_query] = [web_results, search_finding, umbrella_finding+1, all_results+1]

print("All Results", flush=True)
for key, val in search_queries_info.items():
    [web_results, search_finding, umbrella_finding, all_results] = val
    print(key, web_results, search_finding, umbrella_finding, all_results, flush=True, sep="\t")

print("Interactions -- Search Results and Umbrella Results", flush=True)
for i, d in enumerate(keys_list):
    for j, e in enumerate(keys_list):
        if i <= j and d in search_queries_all_repos.keys() and e in search_queries_all_repos.keys():
            print(d, e, 
                        len(search_queries_all_repos[d]), 
                        len(search_queries_all_repos[e]), 
                        len(search_queries_all_repos[d].intersection(search_queries_all_repos[e])), 
                        overlap(search_queries_all_repos[d], search_queries_all_repos[e]), 
                        sorensen_dice(search_queries_all_repos[d], search_queries_all_repos[e]), flush=True, sep="\t")

print("\nInteractions -- Search Results Only\n", flush=True)

for i, d in enumerate(keys_list):
    for j, e in enumerate(keys_list):
        if i <= j and d in search_queries_search_finding_repos.keys() and e in search_queries_search_finding_repos.keys():
            print(d, e, 
                        len(search_queries_search_finding_repos[d]), 
                        len(search_queries_search_finding_repos[e]), 
                        len(search_queries_search_finding_repos[d].intersection(search_queries_search_finding_repos[e])), 
                        overlap(search_queries_search_finding_repos[d], search_queries_search_finding_repos[e]), 
                        sorensen_dice(search_queries_search_finding_repos[d], search_queries_search_finding_repos[e]), flush=True, sep="\t")


print("Number of unique repos", len(all_repos))

with open("data_cleaning/consolidated/data/manual.txt", "w") as f:
    for r in sorted(all_repos):
        f.write(r + "\n")