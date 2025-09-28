# 🖥️ NordicHosting Server Management

En terminalbaserad serverhanteringsapplikation skriven i Python med SSH-integration.

## Funktioner

- **Serverhantering**: Lägg till, ta bort, starta, stoppa och starta om servrar
- **SSH-integration**: Anslut direkt till servrar via SSH (speciellt 10.0.0.38)
- **Administration**: Avancerade serveradministrationsverktyg
- **Processövervakning**: Visa systemstatus, CPU, minne, diskutrymme
- **Backup & Restore**: Säkerhetskopiera och återställa serverkonfigurationer
- **Svenskt gränssnitt**: Helt på svenska för enkel användning

## 🚀 Installation

1. Klona repositoryt:
```bash
git clone https://github.com/thorbjornnordichosting/NordicHosting-Server-Management.git
cd NordicHosting-Server-Management
```

2. Installera Python 3:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3

# CentOS/RHEL
sudo yum install python3
```

3. Kör applikationen:
```bash
python3 server_manager.py
```

## 📋 Användning

### Huvudmeny
```
🖥️  SERVER MANAGER
==================================================
1. Lista servrar
2. Lägg till server
3. Ta bort server
4. Starta server
5. Stoppa server
6. Starta om server
7. Visa serverstatus
8. Starta alla servrar
9. Stoppa alla servrar
A. Administrera server
S. SSH-anslutning
C. Anslut till 10.0.0.38 (SSH)
0. Avsluta
==================================================
```

### SSH-anslutning till 10.0.0.38

Applikationen har specialstöd för SSH-anslutning till servern 10.0.0.38:

- **Snabb anslutning**: Välj alternativ `C` för direkt SSH-anslutning
- **Via serverhantering**: Välj alternativ 4, 5, 6 eller 7 och skriv `10.0.0.38`
- **Flexibel input**: Accepterar både `10.0.0.38` och `server-10-0-0-38`

### Exempel på användning

```bash
# Starta applikationen
python3 server_manager.py

# Välj alternativ 4 (Starta server)
# Skriv: 10.0.0.38
# Ansluter automatiskt via SSH
```

## 🔧 Konfiguration

Serverkonfigurationer sparas i `servers.json`:

```json
{
  "server-10-0-0-38": {
    "name": "server-10-0-0-38",
    "port": 8080,
    "command": "python3 server_10_0_0_38.py",
    "description": "Webbserver på 10.0.0.38:8080 med SSH-info",
    "status": "online",
    "pid": null
  }
}
```

## 📁 Filer

- `server_manager.py` - Huvudapplikation
- `server_10_0_0_38.py` - Testserver för 10.0.0.38
- `servers.json` - Serverkonfigurationer
- `.gitignore` - Git ignore-regler

## 🛠️ Utveckling

### Krav
- Python 3.6+
- Git
- SSH-klient (för SSH-funktionalitet)

### Bidrag
1. Forka repositoryt
2. Skapa en feature branch
3. Commita dina ändringar
4. Pusha till branch
5. Skapa en Pull Request

## 📝 Licens

Detta projekt är öppet källkod och tillgängligt under MIT-licensen.

## 🤝 Support

För frågor eller problem, skapa en issue på GitHub.

---

**Skapad med ❤️ för enkel serverhantering i Norge** 🇳🇴
