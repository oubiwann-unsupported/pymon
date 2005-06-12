from twisted.enterprise import adbapi
from twisted.internet import defer, reactor

class MySQLStatus:

    def __init__(self):
        self.db_pool = adbapi.ConnectionPool("MySQLdb", host="localhost",
                                                     db="mysql", user="root")
 
    def queryStatus(self):
        results = self.db_pool.runQuery("show status")
        return results

def getStatus(results):
    dict_results = {}
    for result in results:
        dict_results[result[0]] = result[1]
    aborted_clients = dict_results['Aborted_clients']
    slow_queries = dict_results['Slow_queries']
    threads_connected = dict_results['Threads_connected']
    threads_running = dict_results['Threads_running']
    questions = dict_results['Questions']
    uptime = dict_results['Uptime']
    print questions
    

mysql = MySQLStatus()
results = mysql.queryStatus()
results.addCallback(getStatus)

reactor.callLater(4, reactor.stop); reactor.run()
