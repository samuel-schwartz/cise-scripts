def overlap(set_a, set_b):
    return len(set_a.intersection(set_b)) / min(len(set_a), len(set_b)) if min(len(set_a), len(set_b)) > 0 else 0

def sorensen_dice(set_a, set_b):
    return (2* len(set_a.intersection(set_b))) / (len(set_a) + len(set_b)) if len(set_a) + len(set_b) > 0 else 0


# Set up container for repos
all_repos = set()
data_holder = list() # [([search query 1, search query 2], {repo1, repo2, ...})]
data_holder.append(([], set()))

file_prefix = "data_cleaning/manual_searching/data/"

print("Adding Repos", flush=True)
# Add unique repos
with open(file_prefix+"MoreMildlyCleanedGitHubSearchResults.csv", "r") as f:
    current_search_query = ""
    data_index = 0

    for line in f.readlines()[1:]:
        # Do Cleaning
        line = line.strip()
        search_query, results_found, repo, find_type = line.split(",")
        search_query = search_query.strip()
        results_found = results_found.strip()
        repo = repo.strip()
        find_type = find_type.strip()

        # Determine if we need to add a new search query
        if search_query != "":
            previous_search_query = current_search_query
            current_search_query = search_query
            
            if "." in previous_search_query and "." not in current_search_query: # If we have passed the last search query of a group (which contains a url with a ".", for example .gov), go to next group in data_holder
                data_holder.append(([current_search_query], set()))
                data_index += 1
            else:
                data_holder[data_index][0].append(current_search_query)
            continue
        data_holder[data_index][1].add(repo)
        all_repos.add(repo)

# Print summary results table:

print(len(all_repos))

for row in data_holder:
    print(str(row[0])[1:-1].replace(",", "-").replace("'", ""), ",", len(row[1]))


# Print Overlap coefficents

print("\nOverlap Coefficents")

keys_list = [search_queries for (search_queries, _) in data_holder]

for i, d in enumerate(keys_list):
    for j, e in enumerate(keys_list):
        if i <= j:
            print(d[-1], e[-1], 
                        len(data_holder[i][1]), 
                        len(data_holder[j][1]), 
                        len(data_holder[i][1].intersection(data_holder[j][1])), 
                        overlap(data_holder[i][1], data_holder[j][1]), 
                        sorensen_dice(data_holder[i][1], data_holder[j][1]), flush=True, sep=",")