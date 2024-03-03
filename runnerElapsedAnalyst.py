import logging
import requests
from datetime import datetime, timedelta, time
import json
from httplib2 import Http
import os
from csv import writer

def getSecret():
    secret = "ghp_XXXXX"
    return secret

def reposSet():
    repoSet = set([])
    baseUrl = 'https://api.github.com/users/armyost/repos'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}
    for i in range(0, 20):
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
    logging.basicConfig(filename="Log_{the_time}.log".format(the_time=datetime.now().date()),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

    listRepos = reposSet()

    # beforeOneWeekGMT = datetime.today() - timedelta(weeks=1, hours=9)
    beforeOneWeekGMT = datetime.combine(datetime.now().date() - timedelta(weeks=1, days=1), datetime.min.time())
    # beforeOneWeekGMT = datetime.combine(datetime.now().date() - timedelta(weeks=1), datetime.min.time())
    
    logging.info("!!! From : %s, to Now" % beforeOneWeekGMT)
    logging.info("!!! ------------- Logging start ------------- ")
    baseUrl = 'https://api.github.com/repos/'
    timeout = 5
    headers = {'Authorization': 'Bearer ' + getSecret(), 'Accept':'application/vnd.github+json'}

    for repo in listRepos:
        # elapsedTimePerRepo = timedelta(0, 0, 0)
        elapsedTimePerRepo = 0
        actionsUrl = baseUrl+repo+'/actions/runs'
        logging.info("!!! -------------------------- Repository %s Logging start" % repo)
        for i in range(1, 20):
            payloads =  {'per_page':'50', 'page':i}
            actionsData = requests.get(actionsUrl, headers=headers, params=payloads, timeout=timeout)
            actions = json.loads(actionsData.text)
            if actions['workflow_runs']==[]: break
            if datetime.strptime(actions['workflow_runs'][0]['created_at'], '%Y-%m-%dT%H:%M:%SZ') < beforeOneWeekGMT: break
            for workflowData in actions['workflow_runs']:
                workflowCreateTime = datetime.strptime(workflowData['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                workflowUpdateTime = datetime.strptime(workflowData['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                if workflowCreateTime >= beforeOneWeekGMT:
                    elapsedTime = workflowUpdateTime - workflowCreateTime
                    logging.info("!!! RepoName: %(repo)s, RunNumber: %(run_number)s, Elapsed Time : %(elapsedTime)s, WorkflowCreateTime: %(workflowCreateTime)s" % {"repo":repo, "elapsedTime":elapsedTime, "workflowCreateTime":workflowCreateTime, "run_number":workflowData['run_number']})
                    elapsedTimePerRepo += int(elapsedTime.total_seconds()/60)+1
        excelInput([repo, elapsedTimePerRepo])
        logging.info("!!! Repository : %(repo)s, EntireElapsedTime : %(elapsedTimePerRepo)s" % {"repo":repo, "elapsedTimePerRepo":elapsedTimePerRepo})
        logging.info("!!! -------------------------- ")
    
    logging.info("!!! ------------- Logging end ------------- ")
if __name__=="__main__":
    function_invoke()
