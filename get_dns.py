# # creds.py template
# pihole_ip = ""
# pihole_pass = ""
# pihole_db_path = "<path to file pihole-FTL.db>"
# time_frame = "<delta in seconds>" # e.g. 86400 for 24 hours
# apt_db_url = ""
# apt_db_key = ""
# apt_db_htuser = ""
# apt_db_htpass = ""
# 
# for the pihole HTTP API script uses pihole-api lib: python3 -m pip install pihole-api

import creds
import pihole as ph
import pprint as pp
import sqlite3
import requests

# connections block
# --------------------------------------------------------------------------
def connect_pihole_api():
    handle = ph.PiHole(creds.pihole_ip)
    handle.authenticate(creds.pihole_pass)
    return handle

def connect_pihole_sql():    
    conn = sqlite3.connect(creds.pihole_db_path)
    return conn

# requests to databases
# --------------------------------------------------------------------------
# todo - filter out visited with last 24 hours
def get_domains_api(handle):
    handle.refresh()
    unique = handle.unique_domains
    pp.pprint("Host visited " + unique + " unique domains")
    handle.refreshTop(unique)
    check_domain_aptdb(handle.top_queries.items())    

def get_domains_sql(conn):        
    sql = "select domain from queries where timestamp>=strftime('%s','now')-" + creds.time_frame + " group by domain"    
    cur = conn.cursor()
    return cur.execute(sql)    

# todo - wrap HTTP POST requests into separate lib as pihole-api
def check_domain_aptdb(domains):    
    for domain in domains:                
        try:
            print(domain[0])
            body = dict(auth_code=creds.apt_db_key, entries='[\"' + domain[0] + '\"]')                
            r = requests.post(creds.apt_db_url, body, auth=(creds.apt_db_htuser,creds.apt_db_htpass))                
            print(r.text)    
        except TypeError:
            print("Domains list is over")

# --------------------------------------------------------------------------
if __name__ == "__main__":
    # sql way if file is available
    print("Through SQLite")
    conn = connect_pihole_sql()
    domains = get_domains_sql(conn)    
    check_domain_aptdb(domains)
    conn.close()

    # HTTP API way
    print("Through HTTP API")
    handle = connect_pihole_api()
    domains = get_domains_api(handle)
    check_domain_aptdb(domains)
    # closing the HTTP API connection?
        
    # todo - add proper ctor/dtor for connect/disconnect
    
