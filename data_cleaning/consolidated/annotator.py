import os
import json
import datetime
import pandas as pd
import traceback

class Repo:
    def __init__(self, name) -> None:
        self.name = name
        self.created_at = None
        self.updated_at = None
        self.pushed_at = None
        self.fork = None
        self.stargazers_count = None
        self.watch_count = None
        self.forks_count = None
        self.forks = None
        self.open_issues = None
        self.has_issues = None
        self.has_projects = None
        self.has_downloads = None
        self.has_wiki = None
        self.has_pages = None
        self.has_discussions = None
        self.open_issues = None
        self.open_issues_count = None
        self.network_count = None
        self.subscriber_count = None
        self.is_template = None

        self.contributors = list()
        self.contributors_by_contribution_count = dict() # Key = contributor username, value = # of contributions
        self.contributors_by_contribution_percentage = dict() # Key = contributor username, value = # of contributions

file_prefix = "data_cleaning/consolidated/meta/"
directories = os.walk(file_prefix)

repos = list()

now = datetime.datetime.now().timestamp()

print("name", "creation_timestamp", 
                "last_push_timestamp", 
                "time_between_creation_and_last_push", 
                "time_since_creation", 
                "time_since_last_push", 
                "stargazers_count", 
                "watch_count", 
                "subscriber_count", 
                "open_issues", 
                "fork", 
                "forks_count", 
                "network_count",
                "contributors",
                "contributions",
                "cont_per_0", "cont_per_1", "cont_per_2", "cont_per_3", "cont_per_4",
                "cont_per_5", "cont_per_6", "cont_per_7", "cont_per_8", "cont_per_9",
                sep="\t", flush=True)

unique_users = set()

no_big_query_repos = set()
with open(file_prefix + "../unique_repos_no_bigquery.txt") as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if line != "":
            no_big_query_repos.add(line)
    

for d in directories:
    try:
        d = d[0]
        if "-----" not in d:
            continue
        repo_name = d.split("/")[-1].replace("-----", "/")

        #if repo_name not in no_big_query_repos:
        #    continue

        r = Repo(repo_name)
        repo_info_json = None
        repo_contributors_json = None
        with open(d + "/repo_info.json", "r") as f:
            repo_info_json = json.load(f)
        with open(d + "/repo_contributors.json", "r") as f:
            repo_contributors_json = json.load(f)

        attributes = ["created_at", "updated_at", "pushed_at", 
        "fork", "stargazers_count", "watch_count", "forks_count", "forks", "has_issues",
        "has_projects", "has_downloads", "has_wiki", "has_pages", "has_discussions",
        "open_issues", "open_issues_count", "network_count", "subscriber_count", "is_template"]
        
        for a in attributes:
            val = repo_info_json[a] if a in repo_info_json else 0
            if type(val) == str:
                val = pd.to_datetime(val).to_pydatetime()
                #val = datetime.datetime.strptime(repo_info_json[a], '%Y-%m-%dT%H:%M:%S.%f%Z')
            if type(val) == bool:
                val = 1 if val else 0

            setattr(r, a, val)

        try:
            r.contributors = [user["login"] for user in repo_contributors_json]
            unique_users.update(r.contributors)
            for user in repo_contributors_json:
                r.contributors_by_contribution_count[user["login"]] = user["contributions"]

            all_contributions_count = sum(r.contributors_by_contribution_count.values())

            for user in repo_contributors_json:
                r.contributors_by_contribution_percentage[user["login"]] = user["contributions"] / all_contributions_count
        except:
            with open("annotator_errors.txt", "a") as f:
                #print("Error", repo_name, e, file=f)
                #print(traceback.format_exc(), file=f)
                print(repo_name, file=f)
            pass

        cont_per = sorted(r.contributors_by_contribution_percentage.values(), reverse=True)
        if len(cont_per) < 10:
            cont_per = cont_per + [0] * (10 - len(cont_per))
        elif len(cont_per) > 10:
            cont_per = cont_per[:10]

        print(r.name, int(r.created_at.timestamp()), 
                int(r.pushed_at.timestamp()), 
                int(r.pushed_at.timestamp()) - int(r.created_at.timestamp()), 
                int(now - r.created_at.timestamp()), 
                int(now - r.pushed_at.timestamp()), 
                r.stargazers_count, 
                r.watch_count, 
                r.subscriber_count, 
                r.open_issues, 
                r.fork, 
                r.forks_count, 
                r.network_count,
                len(r.contributors),
                sum(r.contributors_by_contribution_count.values()),
                str([round(_, 2) for _ in cont_per])[1:-1].replace(", ", "\t"), 
                sep="\t", flush=True)

        repos.append(r)
        
    except Exception as e:
        with open("annotator_errors.txt", "a") as f:
            #print("Error", repo_name, e, file=f)
            #print(traceback.format_exc(), file=f)
            print(repo_name, file=f)
    
with open("annotator_unique_authors.txt", "w") as f:
    for u in sorted(unique_users):
        f.write(u + "\n")
