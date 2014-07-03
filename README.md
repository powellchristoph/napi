NAPI
====

NAPI is a very rudimentary API into my Nagios master. It allows you to add a host with the appropriate checks with the use of a POST curl call.

It adds hosts to the *HOSTS_FILE* in napi.py.

The check are already configured on the Nagios server using [Object Inheritance](http://nagios.sourceforge.net/docs/3_0/objectinheritance.html) by hostname. It is configured to support a tmethod parameter which is used to determine which checks are applied to the host.

It does some basic validation to ensure the POST request is correct and that the host is not currently in Nagios by looking for the hostname and ip. It will return the correct HTTP response and xml error, if any.

It will add or remove the host using [PyNag](http://pynag.org/) and then reload the Nagios service. To do this, the Apache user must have sudo access to reload the Nagios service.

The following endpoints are supported.
* /napi/ - (GET) Basic health api. Returns "Napi is running."
* /napi/add - (POST) with ip, host and tmethod parameters, it will add the host to Nagios and reload the service.
* /napi/delete - (POST) with ip and host, it will remove the host from Nagios and reload the service.

Installation:
* bottle.py - Place in /var/www/napi directory and give ownership to the apache/www-data user. 
* napi.conf - Apache configuration file, place in /etc/{httpd,apache}/conf.d/
* napi.py - Place in /var/www/napi directory and give ownership to the apache/www-data user.
* napi.wsgi - Place in /var/www/napi directory and give ownership to the apache/www-data user.

To run, just start the Apache process.

The register_host.sh is a very basic script that will prompt and register the host. It also performs some basic host-side validation prior to registration. It checks for a valid IP and that the hostname has been set.
