from re import findall
from subprocess import Popen, PIPE

def ping(host, pingCount, timeoutMiliseconds='500'):
    pingCount = str(pingCount)
    output = Popen(["fping", host, '-c', pingCount, '-t', timeoutMiliseconds], stdout=PIPE)
    output.wait()
    stdout = output.stdout.read().decode('utf-8')
    status = findall(r'64 bytes', stdout)
    if status:
        result = 'UP'
    else:
        result = 'DOWN'
    return [stdout, result]

def ping_multiple(hosts, pingCount, timeoutMiliseconds='500'):
    pingCount = str(pingCount)
    output = Popen(["fping", *hosts, '-c', pingCount, '-t', timeoutMiliseconds], stdout=PIPE)
    output.wait()
    stdout = output.stdout.read().decode('utf-8')
    print(output)
    status = findall(r'64 bytes', stdout)
    if status:
        result = 'UP'
    else:
        result = 'DOWN'
    return [stdout, result]