import subprocess
import os 
import time 

unique_repos = set()

file_prefix = "data_cleaning/consolidated/"
#with open(file_prefix + "unique_repos.txt", "r") as f:
#    for line in f:
#        unique_repos.add(line.strip())

with open(file_prefix + "cleaned_problem_repos_from_annotation_errors2.txt", "r") as f:
    for line in f:
        unique_repos.add(line.strip())

unique_repos = sorted(unique_repos)

for i, r in enumerate(unique_repos):
    sleep_time = (60 * 60) / 1500  # Only do about 1500 iterations / hour to stay below API rates. Max of 5000 quieries per hour -> 5000/3 queries per repo -> 1666 iterations/hour ->  1500 to be safe
    print("Sleeping for", sleep_time, "seconds", flush=True)
    time.sleep(sleep_time)

    print("Working on", r, ";", i, "of", len(unique_repos), round((100 * i) / len(unique_repos), 2), flush=True)

    file_midfix = "meta/" + r.replace("/", "-----") + "/"
    os.makedirs(file_prefix + file_midfix, exist_ok=True)

    # Get repo info
    print("\t Working on Repo Info")
    cmd = 'gh api   -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"    /repos/' + r
    result = subprocess.run([cmd], capture_output=True, shell=True, universal_newlines=True)
    result_str = str(result.stdout)
    with open(file_prefix + file_midfix + "repo_info.json", "w") as f:
        f.write(result_str)

    # Get contributors
    print("\t Working on Repo Contributors")
    cmd = 'gh api   -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"    /repos/' + r + '/contributors?per_page=100'
    result = subprocess.run([cmd], capture_output=True, shell=True, universal_newlines=True)
    result_str = str(result.stdout)
    with open(file_prefix + file_midfix + "repo_contributors.json", "w") as f:
        f.write(result_str)

    # Get software bill of materials
    print("\t Working on Repo Bill of Materials")
    cmd = 'gh api   -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"    /repos/' + r + '/dependency-graph/sbom'
    result = subprocess.run([cmd], capture_output=True, shell=True, universal_newlines=True)
    result_str = str(result.stdout)
    with open(file_prefix + file_midfix + "repo_sbom.json", "w") as f:
        f.write(result_str)
    




# Repo # gh api   -H "Accept: application/vnd.github+json"  -H "X-GitHub-Api-Version: 2022-11-28"    /repos/llnl/zfp
# SBOM # gh api   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/llnl/zfp/dependency-graph/sbom
# Top 100 contributors # gh api   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/llnl/zfp/contributors?per_page=100
# Emails # gh api   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/llnl/umpire/commits?committer=davidbeckingsale
