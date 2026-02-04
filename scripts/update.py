import requests
from bs4 import BeautifulSoup
from datetime import date

FATF_URL = "https://www.fatf-gafi.org/en/topics/high-risk-and-other-monitored-jurisdictions.html"
EU_URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R1675"

def fetch_fatf():
    r = requests.get(FATF_URL, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    data = {}

    for h in soup.find_all("h2"):
        title = h.get_text(strip=True).lower()
        ul = h.find_next("ul")
        if not ul:
            continue

        for li in ul.find_all("li"):
            c = li.get_text(strip=True)
            if "call for action" in title:
                data[c] = "Black"
            elif "increased monitoring" in title:
                data[c] = "Grey"
    return data

def fetch_eu():
    r = requests.get(EU_URL, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")
    return sorted(
        {li.get_text(strip=True)
         for li in soup.find_all("li")
         if li.get_text(strip=True).isalpha()}
    )

fatf = fetch_fatf()
eu = fetch_eu()

lines = []
lines.append("# AML Country Risk Reference")
lines.append("")
lines.append(f"_Last updated: {date.today()}_")
lines.append("")
lines.append("| Country | FATF Status | EU AML High Risk |")
lines.append("|--------|-------------|------------------|")

countries = sorted(set(fatf.keys()) | set(eu))

for c in countries:
    lines.append(
        f"| {c} | {fatf.get(c, '')} | {'Yes' if c in eu else ''} |"
    )

with open("docs/index.md", "w") as f:
    f.write("\n".join(lines))
