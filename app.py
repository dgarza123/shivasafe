import streamlit as st
import socket, ssl, whois, csv, requests, dns.resolver
import pandas as pd
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from ipwhois import IPWhois

st.set_page_config(page_title="Gov Domain Threat Scanner", layout="wide")
st.title("🛡️ U.S. Government Domain Threat Scanner")

@st.cache_data(show_spinner=False)
def get_tls(domain):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=4) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert(True)
                x509_obj = x509.load_der_x509_certificate(cert, default_backend())
                return x509_obj.fingerprint(ssl.HASH_SHA256()).hex()
    except: return ""

def get_asn_info(domain):
    try:
        ip = socket.gethostbyname(domain)
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        return ip, res.get('asn', ''), res.get('asn_country_code', ''), res.get('asn_description', '')
    except: return "", "", "", ""

def get_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [str(r.exchange).strip('.') for r in answers]
    except:
        return []

def get_cname(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        return str(answers[0].target).strip('.')
    except:
        return ""

def get_whois(domain):
    try:
        w = whois.whois(domain)
        return w.registrar or "", w.org or ""
    except:
        return "", ""

gov_domains = [
    "azdhs.gov", "ncdps.gov", "nhtsa.gov", "cdc.gov", "nih.gov", "noaa.gov", "usgs.gov", "nasa.gov", "energy.gov", "bop.gov",
    "fanniemae.com", "hud.gov", "govdelivery.com", "digital.gov", "govos.com", "tylertech.com", "signal.org",
    "whitehouse.gov", "teamtulsi.com", "fbi.gov", "uscourts.gov", "justice.gov", "dea.gov", "atf.gov",
    "dhs.gov", "cbp.gov", "ice.gov", "interpol.int", "finCEN.gov", "secretservice.gov", "usmarshals.gov",
    "crimesolutions.gov", "tips.fbi.gov", "crime-data-explorer.fr.cloud.gov", "usa.gov", "victimconnect.org",
    "identitytheft.gov", "missingkids.org", "ic3.gov", "ssa.gov", "medicare.gov", "benefits.gov",
    "studentloans.gov", "ed.gov", "dol.gov", "epa.gov", "irs.gov", "treasury.gov", "usps.gov", "uscis.gov",
    "homelandsecurity.gov", "usajobs.gov"
]

newfold_keywords = ["GoDaddy", "Gandi", "Register.com", "Bluehost", "Network Solutions", "Web.com", "CrazyDomains", "Domain.com"]

rows = []
st.info("Scanning in progress... please wait.")
progress = st.progress(0)

for i, domain in enumerate(gov_domains, 1):
    tls_fp = get_tls(domain)
    ip, asn, asn_cc, asn_desc = get_asn_info(domain)
    mx = get_mx_records(domain)
    cname = get_cname(domain)
    registrar, org = get_whois(domain)

    rows.append({
        "domain": domain,
        "tls_fp": tls_fp,
        "asn": asn,
        "asn_country": asn_cc,
        "asn_desc": asn_desc,
        "mx": ", ".join(mx),
        "cname": cname,
        "registrar": registrar,
        "org": org
    })
    progress.progress(i / len(gov_domains))

st.success("Scan complete.")

df = pd.DataFrame(rows)
def check_newfold(row):
    return any(keyword.lower() in str(row['registrar']).lower() or keyword.lower() in str(row['org']).lower() for keyword in newfold_keywords)

df['whois_newfold'] = df.apply(check_newfold, axis=1)
df['whois_markmonitor'] = df.apply(lambda x: 'MarkMonitor' in str(x['registrar']) or 'MarkMonitor' in str(x['org']), axis=1)
df['whois_redacted'] = df.apply(lambda x: 'REDACTED FOR PRIVACY' in str(x['registrar']) or 'REDACTED FOR PRIVACY' in str(x['org']), axis=1)

charged = df[df['whois_newfold'] == True]
st.subheader("⚠️ Newfold-Controlled Government Domains")
st.write(f"Matches found: {len(charged)}")
st.dataframe(charged[['domain', 'registrar', 'org', 'asn_desc']])

# Save download
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Full Scan CSV", csv, "gov_threat_scan.csv", "text/csv")

backup = charged.to_csv(index=False).encode('utf-8')
st.download_button("Download Newfold Matches Only", backup, "newfold_matches.csv", "text/csv")
