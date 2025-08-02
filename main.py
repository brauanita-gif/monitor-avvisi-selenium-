import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
import time

# --- CONFIGURAZIONE ---
URLS = [
    "https://www.aspalsardegna.it/aspalpost/personale-per-progetti-scolastici/",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=SC24478",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=SC27334",
    "https://www.ic2nuoro.edu.it/albo-online",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=SC27512",
    "https://www.trasparenzascuole.it/Public/APDPublic_ExtV2.aspx?CF=81000530907",
    "https://web.spaggiari.eu/sdg2/AlboOnline/NUME0013",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=SC14931",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=SC28343",
    "https://www.portaleargo.it/albopretorio/online/#/?customerCode=sc28342",
    "https://www.comune.nuoro.it/it/novita/avvisi",
    "https://www.asl3nuoro.it/albo-pretorio/avvisi-e-comunicazioni/",
    "https://www.mim.gov.it/web/nuoro",
    "https://www.subito.it/annunci-sardegna/vendita/offerte-lavoro/?q=Mediazione+culturale"
]

KEYWORDS = [
    "avviso", "manifestazione", "interesse", "interpello", "progetto",
    "mediazione linguistica e culturale", "mediazione culturale",
    "mediazione linguistica", "mediazione interculturale",
    "mediatore linguistico culturale", "mediatore culturale",
    "mediatore linguistico", "mediatore interculturale", "lingue",
    "facilitatore linguistico", "inglese", "francese",
    "lingua inglese", "lingua francese"
]

EMAIL_SENDER = "brauanita@gmail.com"
EMAIL_PASSWORD = "taadhlvrtzrcqnoj"
EMAIL_RECEIVER = "brauanita@gmail.com"

def check_static_site(url):
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text().lower()
        found_keywords = [kw for kw in KEYWORDS if kw in text]
        return found_keywords if found_keywords else None
    except Exception as e:
        print(f"[STATIC] Errore su {url}: {e}")
        return None

def check_dynamic_site(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)
        time.sleep(5)
        text = driver.page_source.lower()
        driver.quit()

        found_keywords = [kw for kw in KEYWORDS if kw in text]
        return found_keywords if found_keywords else None
    except Exception as e:
        print(f"[DYNAMIC] Errore su {url}: {e}")
        return None

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

def main():
    results = []
    for url in URLS:
        if any(x in url for x in ["argo", "spaggiari", "trasparenzascuole", "subito.it"]):
            found = check_dynamic_site(url)
        else:
            found = check_static_site(url)
        if found:
            results.append((url, found))

    if results:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        body = f"🔔 Avvisi trovati il {now}:

"
        for url, keywords in results:
            body += f"- {url}
  ➤ Parole trovate: {', '.join(keywords)}
"
        send_email("🔔 Nuove segnalazioni trovate (Selenium)", body)
        print("✅ Email inviata con i risultati.")

        with open("log_risultati.csv", "a", encoding="utf-8") as f:
            for url, keywords in results:
                riga = f"{now};{url};{','.join(keywords)}\n"
                f.write(riga)
    else:
        print("✅ Nessuna parola chiave trovata.")

if __name__ == "__main__":
    main()
