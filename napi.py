#!/usr/bin/env python

import socket
from subprocess import check_call, Popen, PIPE

from pynag import Model

from bottle import Bottle, run, template, request, abort, HTTPResponse

HOSTS_FILE = '/etc/nagios/conf.d/x2-hosts.cfg'

app = Bottle()

transfer_methods = {
        1 : 'standard',
        2 : 'kencast',
        3 : 'aspera',
    }

def error_response(code, msg):
    return """<?xml version="1.0" encoding="UTF-8"?>
<Error>
  <Code>%s</Code>
  <Message>%s</Message>
</Error>\n""" % (code, msg)

def exists(host, ip):
    names = Model.Host().objects.filter(host_name=host.lower())
    ips = Model.Host().objects.filter(address=ip)

    if names or ips:
        return True
    else:
        return False

def add_host(host_name, ip, method):
    host = Model.Host()
    host.set_filename(HOSTS_FILE)
    host.use = 'linux-server'
    host.host_name = host_name.lower()
    host.alias = host_name.upper()
    host.address = ip
    host.hostgroups = 'x2-docker-' + transfer_methods[method]
    host.save()

def delete_host(hostname):
    host_list = Model.Host.objects.filter(host_name=hostname)
    host = host_list[0]
    host.delete()

def reload_nagios():

    status = check_call('sudo /etc/init.d/nagios reload', shell=True)
    return status == 0


@app.get('/napi/')
def status():
    return "NAPI is running."

@app.post('/napi/add')
def add():
    ip = request.POST.ip or None
    host = request.POST.host.lower() or None
    tmethod = int(request.POST.tmethod) or None

    # Make sure they are passing a valid IP
    try:
        socket.inet_aton(ip)
        if ip.count('.') != 3:
            raise Exception('Not a valid address')
    except Exception, err:
        return HTTPResponse(error_response(11, err), 403)

    # Make sure that host/ip are provided in the POST request
    if not host or not ip or not tmethod:
        return HTTPResponse(error_response(400, "Bad Request"), 400)

    # Make sure that the host/ip is not already in Nagios
    elif exists(host, ip):
        return HTTPResponse(error_response(10, "Host/IP Exists"), 403)

    elif tmethod not in transfer_methods.keys():
        return HTTPResponse(error_response(11, "Transfer Method not supported."), 403)

    # Update/Restart nagios
    try:
        add_host(host, ip, tmethod)
        reload_nagios()
    except Exception, err:
        return HTTPResponse(error_response(11, err), 500)

@app.post('/napi/delete')
def delete():
    ip = request.POST.ip or None
    host = request.POST.host.lower() or None

    if not host or not ip:
        return HTTPResponse(error_response(400, "Bad Request"), 400)

    try:
        delete_host(host)
        reload_nagios()
    except Exception, err:
        return HTTPResponse(error_response(11, err), 500)

if __name__ == '__main__':
    run(app, host='0.0.0.0', port=80,debug=True)
