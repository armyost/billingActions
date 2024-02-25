import requests
from datetime import datetime, timedelta
import json
from httplib2 import Http
import os

def getSecret():
    secret = ""
    return secret

def reposSet():
    repoSet = set([])
    # baseUrl = 'https://api.github.com/orgs/ocean-network-express/repos'
    baseUrl = 'https://api.github.com/users/armyost/repos'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}
    for i in range(0, 1):
        payloads =  {'per_page':'50', 'page':i}
        reposData = requests.get(baseUrl, headers=headers, params=payloads, timeout=timeout)
        repos = json.loads(reposData.text)
        for repo in repos:
            repoName = repo['full_name']
            # print('!!! The Repository name : %s' % repoName)
            repoSet.add(repoName)
    return repoSet

def function_invoke():
    
    beforeOneWeekGMT = datetime.today() - timedelta(weeks=1, hours=9)
    listRepos = ['armyost/testPagePy']
    
    # baseUrl = 'https://api.github.com/orgs/ocean-network-express/repos'
    baseUrl = 'https://api.github.com/repos/'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}

    for repo in listRepos:
        actionsUrl = baseUrl+repo+'/actions/runs'
        actionsData = requests.get(actionsUrl, headers=headers, timeout=timeout)
        actions = json.loads(actionsData.text)
        for workflowData in actions['workflow_runs']:
            workflowCreateTime = datetime.strptime(workflowData['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            workflowUpdateTime = datetime.strptime(workflowData['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            if workflowCreateTime > beforeOneWeekGMT:
                runNumber = workflowData['run_number']
                elapsedTime = workflowUpdateTime - workflowCreateTime
                print('!!! runNumber is : %d' % runNumber)
                print('!!! Elapsed Time is : %s' % elapsedTime)

if __name__=="__main__":
    function_invoke()
