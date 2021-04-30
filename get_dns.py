# # script needs creds.py module with the following template
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
import sqlite3
import requests
import json

# --------------------------------------------------------------------------
# connect to pihole
def connect_pihole_api():
    conn = ph.PiHole(creds.pihole_ip)
    conn.authenticate(creds.pihole_pass)
    return conn

def connect_pihole_sql():    
    conn = sqlite3.connect(creds.pihole_db_path)
    return conn

# --------------------------------------------------------------------------
# get domains from pihole
# todo - filter out visited with last 24 hours
def get_domains_api(conn):
    conn.refresh()
    unique = conn.unique_domains
    print("Host visited " + unique + " unique domains")
    conn.refreshTop(unique)    
    return conn.top_queries.items()

def get_domains_sql(conn):        
    sql = "select domain from queries where timestamp>=strftime('%s','now')-" + creds.time_frame + " group by domain"    
    cur = conn.cursor()
    return cur.execute(sql)    

# --------------------------------------------------------------------------
# check agains another database
# todo - wrap HTTP POST requests into separate lib as pihole-api
def check_domain_aptdb(domains):    
    entities = '['       
    for i, domain in enumerate(domains):          
        if i == 0:
            entities += "\"" + domain[0] + "\""
        else:
            entities += ",\"" + domain[0] + "\""            
    # to test with tagged one
    entities += ',\"​azussystems.com\"]'
    print("Asking aptdb for:\n" + entities)
    body = dict(auth_code=creds.apt_db_key, entries=entities)     
    r = requests.post(creds.apt_db_url, body, auth=(creds.apt_db_htuser,creds.apt_db_htpass))                
    return(r)

def deserialize_json(text):
    deserialized = json.loads(text)
    print("The related to known apts are:")    
    print("Domains matched: " + str(deserialized["return_data"]["matches"]))
    print(deserialized["return_data"]["entries"])

# --------------------------------------------------------------------------
if __name__ == "__main__":
    # SQLite way
    print("Using SQLite")
    conn = connect_pihole_sql()
    domains = get_domains_sql(conn)    
    checked = check_domain_aptdb(domains)    
    deserialize_json(checked.text)
    conn.close()

    # HTTP API way
    print("Using HTTP API")
    handle = connect_pihole_api()
    domains = get_domains_api(handle)
    checked = check_domain_aptdb(domains)
    deserialize_json(checked.text)
    # closing the HTTP API connection?
        
    # todo - add proper ctor/dtor for connect/disconnect
    
