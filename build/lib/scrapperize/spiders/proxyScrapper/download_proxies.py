from requests import get

links = ['https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all', 'https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=10000&country=all', 'https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country=all']
responses = []
for link in links:
    responses.append(get(link).content)
proxies = '\n'.join(responses)