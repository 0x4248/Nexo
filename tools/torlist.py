import requests
import hashlib

def get_tor_list():
	url = 'http://localhost:8080/list.txt'
	response = requests.get(url)
	if response.status_code == 200:
		return response.text.splitlines()
	else:
		raise Exception(f"Failed to fetch tor list: {response.status_code}")

def hashipe(line):
	return hashlib.sha1(line.encode()).hexdigest()

ip_list = get_tor_list()	
print(f"Fetched {len(ip_list)} lines from the Tor list.")
hashes = []
for line in ip_list:
	if line.startswith('#'):
		continue
	hash = hashipe(line)
	hashes.append(hash)

with open('data/torlist.txt', 'w') as f:
	for hash in hashes:
		f.write(hash + '\n')

print(f"Fetched {len(hashes)} hashes from the Tor list.")