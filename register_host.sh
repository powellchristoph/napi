#!/bin/bash

HOSTNAME=`hostname -s`
IP=`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
SVR=NAGIOS_SERVER

function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

if [[ $HOSTNAME == 'localhost' ]]; then
	echo -e "\nIt appears that a hostname has not been set."
	echo "Please resolve the issue and re-register."
	exit
fi

if ! valid_ip $IP; then
	echo -e "\nIt appears that $IP is not a valid ip."
	echo "Please resolve the issue and re-register."
	exit
fi

if [ ! -n "$1" ]; then

	clear
	echo -e "\nTransport method:"
	echo -e "\t1: standard"
	echo -e "\t2: kencast"
	echo -e "\t3: aspera"
	echo
	read -p "Enter the appropriate number: > " METHOD
	
	case $METHOD in
		[123]* ) ;;
		* ) echo -e "\n$METHOD is not a valid selection.\n"; exit;;
	esac
	
	echo -e "\nRegistering:"
	echo "Hostname - $HOSTNAME"
	echo "IP       - $IP"
	echo "Method   - $METHOD"
	echo
	
	/usr/bin/curl --data "host=$HOSTNAME&ip=$IP&tmethod=$METHOD" http://$SVR/napi/add
	
	if [[ $? -ne 0 ]]; then
		echo -e "\nError registering, please view the previous output."
	else
		echo -e "\nRegistering complete."
	fi
else
	if [[ $1 == "-u" ]]; then
		echo "Removing $HOSTNAME:$IP"
		/usr/bin/curl --data "host=$HOSTNAME&ip=$IP" http://$SVR/napi/delete
	else
		echo "Unknown argument"
		exit
	fi
fi
