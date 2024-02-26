import requests
from datetime import datetime, timedelta, time
import json
from httplib2 import Http
import os
from csv import writer

def getSecret():
    secret = ""
    return secret

def reposSet():
    repoSet = set([])
    # baseUrl = 'https://api.github.com/orgs/ocean-network-express/repos'
    baseUrl = 'https://api.github.com/users/armyost/repos'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}
    for i in range(0, 10):
        payloads =  {'per_page':'50', 'page':i}
        reposData = requests.get(baseUrl, headers=headers, params=payloads, timeout=timeout)
        repos = json.loads(reposData.text)
        for repo in repos:
            repoName = repo['full_name']
            # print('!!! The Repository name : %s' % repoName)
            repoSet.add(repoName)
    return repoSet

def excelInput(resultList):
    with open('gh_actions_runs.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(resultList)
        f_object.close()
        
def function_invoke():
    listRepos = reposSet()
    # listRepos = ['armyost/testPagePy']
    
    # beforeOneWeekGMT = datetime.today() - timedelta(weeks=1, hours=9)
    beforeOneWeekGMT = datetime.combine(datetime.now().date() - timedelta(weeks=1), datetime.min.time())
    
    print("!!! From : %s, to Now" % beforeOneWeekGMT)
    
    baseUrl = 'https://api.github.com/repos/'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}

    for repo in listRepos:
        elapsedTimePerRepo = timedelta(0, 0, 0)
        actionsUrl = baseUrl+repo+'/actions/runs'
        actionsData = requests.get(actionsUrl, headers=headers, timeout=timeout)
        actions = json.loads(actionsData.text)
        for workflowData in actions['workflow_runs']:
            workflowCreateTime = datetime.strptime(workflowData['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            workflowUpdateTime = datetime.strptime(workflowData['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            if workflowCreateTime > beforeOneWeekGMT:
                elapsedTime = workflowUpdateTime - workflowCreateTime
                # print("!!! Elapsed Time : %s" % elapsedTime)
                elapsedTimePerRepo += elapsedTime
        excelInput([repo, elapsedTimePerRepo])
        print("!!! Repository : %(repo)s, ElapsedTime : %(elapsedTimePerRepo)s" % {"repo":repo, "elapsedTimePerRepo":elapsedTimePerRepo})

if __name__=="__main__":
    function_invoke()
