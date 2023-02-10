#!/usr/bin/env bash
# Before running this script, make sure you have installed
# the following tools: mailspoof, checkdmarc, dnsutils
# Dependencies installation:
# pipx install mailspoof
# pipx install checkdmarc
# sudo apt install dnsutils


domain="$1"

mailspoof -d $domain -o "$domain".mailspoof.json
checkdmarc $domain -o "$domain".checkdmarc.json
dig +short mx $domain | tee "$domain".digmx.txt
dig +short txt $domain | tee "$domain".digtxt.txt

for sub in owa post mail mymail exchange autodiscover exch exch01 outlook; do
	host $sub.$domain | tee -a "$domain".exchange-enum.txt
done
