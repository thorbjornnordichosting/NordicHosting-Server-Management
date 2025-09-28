#!/usr/bin/env python3
"""
Server Manager - En terminalapplikation för att hantera servrar
Med SSH-funktionalitet för fjärråtkomst
"""

import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Server:
    name: str
    command: str
    port: int
    working_directory: str
    description: str = ""
    auto_start: bool = False
    pid: Optional[int] = None
    status: str = "stopped"

class ServerManager:
    def __init__(self, config_file: str = "servers.json"):
        self.config_file = config_file
        self.servers: Dict[str, Server] = {}
        self.load_servers()
    
    def load_servers(self):
        """Laddar servrar från konfigurationsfil"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, server_data in data.items():
                        self.servers[name] = Server(**server_data)
            except Exception as e:
                print(f"Fel vid laddning av servrar: {e}")
    
    def save_servers(self):
        """Sparar servrar till konfigurationsfil"""
        try:
            data = {name: asdict(server) for name, server in self.servers.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fel vid sparande av servrar: {e}")
    
    def add_server(self, name: str, command: str, port: int, working_directory: str, 
                   description: str = "", auto_start: bool = False):
        """Lägger till en ny server"""
        if name in self.servers:
            print(f"Server '{name}' finns redan!")
            return False
        
        server = Server(
            name=name,
            command=command,
            port=port,
            working_directory=working_directory,
            description=description,
            auto_start=auto_start
        )
        
        self.servers[name] = server
        self.save_servers()
        print(f"Server '{name}' har lagts till!")
        return True
    
    def remove_server(self, name: str):
        """Tar bort en server"""
        if name not in self.servers:
            print(f"Server '{name}' hittades inte!")
            return False
        
        if self.servers[name].status == "running":
            self.stop_server(name)
        
        del self.servers[name]
        self.save_servers()
        print(f"Server '{name}' har tagits bort!")
        return True
    
    def list_servers(self):
        """Listar alla servrar"""
        if not self.servers:
            print("Inga servrar konfigurerade.")
            return
        
        print("\n" + "="*80)
        print(f"{'Namn':<20} {'Port':<8} {'Status':<12} {'Beskrivning':<30}")
        print("="*80)
        
        for name, server in self.servers.items():
            status_color = "🟢" if server.status == "running" else "🔴"
            print(f"{name:<20} {server.port:<8} {status_color} {server.status:<10} {server.description:<30}")
        print("="*80)
    
    def start_server(self, name: str):
        """Startar en server"""
        if name not in self.servers:
            print(f"Server '{name}' hittades inte!")
            return False
        
        server = self.servers[name]
        
        if server.status == "running":
            print(f"Server '{name}' körs redan!")
            return False
        
        try:
            # Kontrollera om porten redan används
            if self.is_port_in_use(server.port):
                print(f"Port {server.port} används redan!")
                return False
            
            # Starta servern
            process = subprocess.Popen(
                server.command.split(),
                cwd=server.working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            server.pid = process.pid
            server.status = "running"
            self.save_servers()
            
            print(f"Server '{name}' startad på port {server.port} (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"Fel vid start av server '{name}': {e}")
            return False
    
    def stop_server(self, name: str):
        """Stoppar en server"""
        if name not in self.servers:
            print(f"Server '{name}' hittades inte!")
            return False
        
        server = self.servers[name]
        
        if server.status != "running":
            print(f"Server '{name}' körs inte!")
            return False
        
        try:
            if server.pid:
                if os.name != 'nt':
                    os.killpg(os.getpgid(server.pid), 9)
                else:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(server.pid)])
            
            server.pid = None
            server.status = "stopped"
            self.save_servers()
            
            print(f"Server '{name}' stoppad!")
            return True
            
        except Exception as e:
            print(f"Fel vid stopp av server '{name}': {e}")
            return False
    
    def restart_server(self, name: str):
        """Startar om en server"""
        print(f"Startar om server '{name}'...")
        self.stop_server(name)
        time.sleep(1)
        self.start_server(name)
    
    def is_port_in_use(self, port: int) -> bool:
        """Kontrollerar om en port används"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def get_server_status(self, name: str):
        """Hämtar status för en specifik server"""
        if name not in self.servers:
            print(f"Server '{name}' hittades inte!")
            return
        
        server = self.servers[name]
        print(f"\nServer: {name}")
        print(f"Port: {server.port}")
        print(f"Status: {'🟢 Running' if server.status == 'running' else '🔴 Stopped'}")
        print(f"PID: {server.pid if server.pid else 'N/A'}")
        print(f"Kommando: {server.command}")
        print(f"Arbetskatalog: {server.working_directory}")
        print(f"Beskrivning: {server.description}")

def show_menu():
    """Visar huvudmenyn"""
    print("\n" + "="*50)
    print("🖥️  SERVER MANAGER")
    print("="*50)
    print("1. Lista servrar")
    print("2. Lägg till server")
    print("3. Ta bort server")
    print("4. Starta server")
    print("5. Stoppa server")
    print("6. Starta om server")
    print("7. Visa serverstatus")
    print("8. Starta alla servrar")
    print("9. Stoppa alla servrar")
    print("A. Administrera server")
    print("S. SSH-anslutning")
    print("0. Avsluta")
    print("="*50)

def main():
    """Huvudfunktion"""
    manager = ServerManager()
    
    # Starta servrar med auto_start
    for name, server in manager.servers.items():
        if server.auto_start and server.status != "running":
            print(f"Auto-startar server '{name}'...")
            manager.start_server(name)
    
    while True:
        show_menu()
        
        try:
            choice = input("\nVälj alternativ (0-9, A, S): ").strip().upper()
            
            if choice == "0":
                print("Avslutar...")
                break
            elif choice == "1":
                manager.list_servers()
            elif choice == "2":
                add_server_interactive(manager)
            elif choice == "3":
                remove_server_interactive(manager)
            elif choice == "4":
                start_server_interactive(manager)
            elif choice == "5":
                stop_server_interactive(manager)
            elif choice == "6":
                restart_server_interactive(manager)
            elif choice == "7":
                show_server_status_interactive(manager)
            elif choice == "8":
                start_all_servers(manager)
            elif choice == "9":
                stop_all_servers(manager)
            elif choice == "A":
                admin_server_interactive(manager)
            elif choice == "S":
                ssh_connection()
            else:
                print("Ogiltigt val! Försök igen.")
            
            input("\nTryck Enter för att fortsätta...")
            
        except KeyboardInterrupt:
            print("\n\nAvslutar...")
            break
        except Exception as e:
            print(f"Ett fel uppstod: {e}")

def add_server_interactive(manager: ServerManager):
    """Interaktiv funktion för att lägga till server"""
    print("\n--- Lägg till ny server ---")
    
    name = input("Server namn: ").strip()
    if not name:
        print("Namn krävs!")
        return
    
    command = input("Kommando att köra: ").strip()
    if not command:
        print("Kommando krävs!")
        return
    
    try:
        port = int(input("Port: ").strip())
    except ValueError:
        print("Ogiltig port!")
        return
    
    working_directory = input("Arbetskatalog (lämna tom för aktuell): ").strip()
    if not working_directory:
        working_directory = os.getcwd()
    
    description = input("Beskrivning (valfritt): ").strip()
    
    auto_start = input("Auto-start vid uppstart? (j/n): ").strip().lower() == 'j'
    
    manager.add_server(name, command, port, working_directory, description, auto_start)

def remove_server_interactive(manager: ServerManager):
    """Interaktiv funktion för att ta bort server"""
    if not manager.servers:
        print("Inga servrar att ta bort!")
        return
    
    print("\n--- Ta bort server ---")
    manager.list_servers()
    
    name = input("\nServer namn att ta bort: ").strip()
    if name:
        confirm = input(f"Är du säker på att du vill ta bort '{name}'? (j/n): ").strip().lower()
        if confirm == 'j':
            manager.remove_server(name)

def start_server_interactive(manager: ServerManager):
    """Interaktiv funktion för att starta server"""
    if not manager.servers:
        print("Inga servrar att starta!")
        return
    
    print("\n--- Starta server ---")
    manager.list_servers()
    
    name = input("\nServer namn att starta: ").strip()
    if name:
        manager.start_server(name)

def stop_server_interactive(manager: ServerManager):
    """Interaktiv funktion för att stoppa server"""
    if not manager.servers:
        print("Inga servrar att stoppa!")
        return
    
    print("\n--- Stoppa server ---")
    manager.list_servers()
    
    name = input("\nServer namn (eller '10.0.0.38' för SSH): ").strip()
    if name:
        manager.stop_server(name)

def restart_server_interactive(manager: ServerManager):
    """Interaktiv funktion för att starta om server"""
    if not manager.servers:
        print("Inga servrar att starta om!")
        return
    
    print("\n--- Starta om server ---")
    manager.list_servers()
    
    name = input("\nServer namn (eller '10.0.0.38' för SSH): ").strip()
    if name:
        manager.restart_server(name)

def show_server_status_interactive(manager: ServerManager):
    """Interaktiv funktion för att visa serverstatus"""
    if not manager.servers:
        print("Inga servrar att visa!")
        return
    
    print("\n--- Server status ---")
    manager.list_servers()
    
    name = input("\nServer namn (eller '10.0.0.38' för SSH): ").strip()
    if name:
        manager.get_server_status(name)

def start_all_servers(manager: ServerManager):
    """Startar alla servrar"""
    if not manager.servers:
        print("Inga servrar att starta!")
        return
    
    print("Startar alla servrar...")
    for name in manager.servers:
        manager.start_server(name)

def stop_all_servers(manager: ServerManager):
    """Stoppar alla servrar"""
    if not manager.servers:
        print("Inga servrar att stoppa!")
        return
    
    print("Stoppar alla servrar...")
    for name in manager.servers:
        manager.stop_server(name)

def admin_server_interactive(manager: ServerManager):
    """Interaktiv administration av servrar"""
    if not manager.servers:
        print("Inga servrar att administrera!")
        return
    
    while True:
        print("\n" + "="*60)
        print("🔧 SERVER ADMINISTRATION")
        print("="*60)
        print("1. Visa detaljerad serverinfo")
        print("2. Redigera serverkonfiguration")
        print("3. Visa serverloggar")
        print("4. Kontrollera portanvändning")
        print("5. Systemstatus")
        print("6. Hantera processer")
        print("7. Backup/Återställ konfiguration")
        print("0. Tillbaka till huvudmeny")
        print("="*60)
        
        choice = input("\nVälj alternativ (0-7): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            show_detailed_server_info(manager)
        elif choice == "2":
            edit_server_config(manager)
        elif choice == "3":
            show_server_logs(manager)
        elif choice == "4":
            check_port_usage(manager)
        elif choice == "5":
            show_system_status()
        elif choice == "6":
            manage_processes(manager)
        elif choice == "7":
            backup_restore_config(manager)
        else:
            print("Ogiltigt val! Försök igen.")
        
        input("\nTryck Enter för att fortsätta...")

def show_detailed_server_info(manager: ServerManager):
    """Visar detaljerad information om servrar"""
    print("\n--- Detaljerad Serverinformation ---")
    manager.list_servers()
    
    name = input("\nServer namn för detaljerad info: ").strip()
    if name and name in manager.servers:
        server = manager.servers[name]
        print(f"\n{'='*60}")
        print(f"🔍 DETALJERAD INFORMATION: {name.upper()}")
        print(f"{'='*60}")
        print(f"Namn: {server.name}")
        print(f"Port: {server.port}")
        print(f"Status: {'🟢 Running' if server.status == 'running' else '🔴 Stopped'}")
        print(f"PID: {server.pid if server.pid else 'N/A'}")
        print(f"Kommando: {server.command}")
        print(f"Arbetskatalog: {server.working_directory}")
        print(f"Beskrivning: {server.description}")
        print(f"Auto-start: {'Ja' if server.auto_start else 'Nej'}")
        
        # Kontrollera port
        port_status = "Används" if manager.is_port_in_use(server.port) else "Ledig"
        print(f"Port-status: {port_status}")

def edit_server_config(manager: ServerManager):
    """Redigerar serverkonfiguration"""
    print("\n--- Redigera Serverkonfiguration ---")
    manager.list_servers()
    
    name = input("\nServer namn att redigera: ").strip()
    if name and name in manager.servers:
        server = manager.servers[name]
        
        print(f"\nRedigerar server: {name}")
        print("Lämna tomt för att behålla nuvarande värde")
        
        new_command = input(f"Kommando [{server.command}]: ").strip()
        if new_command:
            server.command = new_command
        
        new_port = input(f"Port [{server.port}]: ").strip()
        if new_port:
            try:
                server.port = int(new_port)
            except ValueError:
                print("Ogiltig port!")
                return
        
        new_working_dir = input(f"Arbetskatalog [{server.working_directory}]: ").strip()
        if new_working_dir:
            server.working_directory = new_working_dir
        
        new_description = input(f"Beskrivning [{server.description}]: ").strip()
        if new_description:
            server.description = new_description
        
        auto_start = input(f"Auto-start (j/n) [{'j' if server.auto_start else 'n'}]: ").strip().lower()
        if auto_start in ['j', 'n']:
            server.auto_start = (auto_start == 'j')
        
        manager.save_servers()
        print(f"✅ Server '{name}' uppdaterad!")

def show_server_logs(manager: ServerManager):
    """Visar serverloggar"""
    print("\n--- Serverloggar ---")
    manager.list_servers()
    
    name = input("\nServer namn för loggar: ").strip()
    if name and name in manager.servers:
        server = manager.servers[name]
        
        print(f"\n📋 Loggar för server: {name}")
        print("="*50)
        
        # Visa processinformation
        if server.status == "running" and server.pid:
            print(f"🔍 Processinformation (PID: {server.pid}):")
            try:
                import subprocess
                result = subprocess.run(['ps', '-p', str(server.pid), '-o', 'pid,ppid,cmd'], 
                                     capture_output=True, text=True, timeout=5)
                if result.stdout:
                    print(result.stdout)
            except:
                print("Kunde inte läsa processinformation")

def check_port_usage(manager: ServerManager):
    """Kontrollerar portanvändning"""
    print("\n--- Portanvändning ---")
    
    used_ports = []
    for name, server in manager.servers.items():
        if manager.is_port_in_use(server.port):
            used_ports.append((name, server.port, server.status))
    
    if used_ports:
        print("🔴 Portar som används:")
        for name, port, status in used_ports:
            print(f"  {name}: Port {port} ({status})")
    else:
        print("🟢 Inga portar används av Server Manager")

def show_system_status():
    """Visar systemstatus"""
    print("\n--- Systemstatus ---")
    
    try:
        import subprocess
        
        # CPU och minne
        print("💻 Systemresurser:")
        result = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
        if result.stdout:
            print(result.stdout)
        
        # Diskutrymme
        print("\n💾 Diskutrymme:")
        result = subprocess.run(['df', '-h'], capture_output=True, text=True, timeout=5)
        if result.stdout:
            print(result.stdout)
        
        # Uptime
        print("\n⏰ Systemuptime:")
        result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
        if result.stdout:
            print(result.stdout)
            
    except Exception as e:
        print(f"Kunde inte hämta systemstatus: {e}")

def manage_processes(manager: ServerManager):
    """Hanterar processer"""
    print("\n--- Processhantering ---")
    
    running_servers = [name for name, server in manager.servers.items() 
                      if server.status == "running"]
    
    if not running_servers:
        print("Inga servrar körs för tillfället.")
        return
    
    print("🟢 Servrar som körs:")
    for name in running_servers:
        server = manager.servers[name]
        print(f"  {name} (PID: {server.pid}, Port: {server.port})")
    
    print("\n1. Visa alla processer")
    print("2. Döda specifik process")
    print("0. Tillbaka")
    
    choice = input("\nVälj alternativ: ").strip()
    
    if choice == "1":
        try:
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
            if result.stdout:
                print(result.stdout)
        except:
            print("Kunde inte visa processer")
    
    elif choice == "2":
        name = input("Server namn (eller '10.0.0.38' för SSH): ").strip()
        if name in manager.servers:
            manager.stop_server(name)
        else:
            print("Server hittades inte!")

def backup_restore_config(manager: ServerManager):
    """Backup och återställ konfiguration"""
    print("\n--- Backup/Återställ Konfiguration ---")
    print("1. Skapa backup")
    print("2. Återställ från backup")
    print("0. Tillbaka")
    
    choice = input("\nVälj alternativ: ").strip()
    
    if choice == "1":
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"servers_backup_{timestamp}.json"
        
        try:
            shutil.copy2(manager.config_file, backup_file)
            print(f"✅ Backup skapad: {backup_file}")
        except Exception as e:
            print(f"❌ Fel vid backup: {e}")
    
    elif choice == "2":
        import os
        import glob
        
        backup_files = glob.glob("servers_backup_*.json")
        if not backup_files:
            print("Inga backup-filer hittades!")
            return
        
        print("Tillgängliga backups:")
        for i, file in enumerate(backup_files, 1):
            print(f"  {i}. {file}")
        
        try:
            choice = int(input("Välj backup att återställa: ")) - 1
            if 0 <= choice < len(backup_files):
                shutil.copy2(backup_files[choice], manager.config_file)
                manager.load_servers()
                print(f"✅ Återställd från: {backup_files[choice]}")
            else:
                print("Ogiltigt val!")
        except (ValueError, IndexError):
            print("Ogiltigt val!")
        except Exception as e:
            print(f"❌ Fel vid återställning: {e}")

def ssh_connection():
    """SSH-anslutning till servern"""
    print("\n" + "="*60)
    print("🔐 SSH-ANSLUTNING")
    print("="*60)
    print("1. Anslut till lokal server (localhost)")
    print("2. Anslut till fjärrserver")
    print("3. Visa SSH-status")
    print("4. Konfigurera SSH-nycklar")
    print("0. Tillbaka till huvudmeny")
    print("="*60)
    
    choice = input("\nVälj alternativ (0-4): ").strip()
    
    if choice == "1":
        ssh_local_connection()
    elif choice == "2":
        ssh_remote_connection()
    elif choice == "3":
        ssh_status()
    elif choice == "4":
        ssh_key_config()
    elif choice == "0":
        return
    else:
        print("Ogiltigt val! Försök igen.")

def ssh_local_connection():
    """SSH-anslutning till lokal server"""
    print("\n--- SSH till lokal server ---")
    
    # Hämta aktuell användare
    current_user = os.getenv('USER', 'root')
    current_host = os.uname().nodename
    
    print(f"Ansluter till: {current_user}@{current_host}")
    
    try:
        # Starta SSH-session
        subprocess.run(['ssh', f'{current_user}@{current_host}'], check=True)
    except subprocess.CalledProcessError:
        print("❌ SSH-anslutning misslyckades!")
    except FileNotFoundError:
        print("❌ SSH-klient inte installerad!")
        print("Installera med: apt install openssh-client")

def ssh_remote_connection():
    """SSH-anslutning till fjärrserver"""
    print("\n--- SSH till fjärrserver ---")
    
    host = input("Server IP eller hostname: ").strip()
    if not host:
        print("Host krävs!")
        return
    
    user = input(f"Användarnamn (root): ").strip() or "root"
    port = input("SSH-port (22): ").strip() or "22"
    
    print(f"Ansluter till: {user}@{host}:{port}")
    
    try:
        # Starta SSH-session
        subprocess.run(['ssh', '-p', port, f'{user}@{host}'], check=True)
    except subprocess.CalledProcessError:
        print("❌ SSH-anslutning misslyckades!")
    except FileNotFoundError:
        print("❌ SSH-klient inte installerad!")
        print("Installera med: apt install openssh-client")

def ssh_status():
    """Visar SSH-status"""
    print("\n--- SSH-status ---")
    
    try:
        # Kontrollera SSH-tjänst
        result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("🟢 SSH-tjänst: Aktiv")
        else:
            print("🔴 SSH-tjänst: Inaktiv")
    except:
        print("⚠️  Kunde inte kontrollera SSH-tjänst")
    
    # Visa SSH-processer
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        if result.stdout:
            ssh_processes = [line for line in result.stdout.split('\n') if 'sshd' in line]
            if ssh_processes:
                print(f"\n🔍 SSH-processer ({len(ssh_processes)}):")
                for process in ssh_processes[:5]:  # Visa max 5
                    print(f"  {process}")
            else:
                print("\n🔍 Inga SSH-processer hittades")
    except:
        print("⚠️  Kunde inte visa SSH-processer")
    
    # Visa öppna portar
    try:
        result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
        if result.stdout:
            ssh_ports = [line for line in result.stdout.split('\n') if ':22 ' in line]
            if ssh_ports:
                print(f"\n🌐 SSH-portar:")
                for port in ssh_ports:
                    print(f"  {port}")
            else:
                print("\n🌐 Inga SSH-portar öppna")
    except:
        print("⚠️  Kunde inte visa portar")

def ssh_key_config():
    """Konfigurerar SSH-nycklar"""
    print("\n--- SSH-nyckelkonfiguration ---")
    print("1. Generera ny SSH-nyckel")
    print("2. Visa befintliga nycklar")
    print("3. Kopiera publik nyckel")
    print("0. Tillbaka")
    
    choice = input("\nVälj alternativ: ").strip()
    
    if choice == "1":
        generate_ssh_key()
    elif choice == "2":
        list_ssh_keys()
    elif choice == "3":
        copy_public_key()
    elif choice == "0":
        return
    else:
        print("Ogiltigt val! Försök igen.")

def generate_ssh_key():
    """Genererar ny SSH-nyckel"""
    print("\n--- Generera SSH-nyckel ---")
    
    email = input("E-postadress för nyckeln: ").strip()
    if not email:
        print("E-postadress krävs!")
        return
    
    key_type = input("Nyckeltyp (rsa/ed25519) [ed25519]: ").strip() or "ed25519"
    key_file = input(f"Nyckelfil (~/.ssh/id_{key_type}): ").strip() or f"~/.ssh/id_{key_type}"
    
    try:
        subprocess.run(['ssh-keygen', '-t', key_type, '-C', email, '-f', key_file, '-N', ''], 
                      check=True)
        print(f"✅ SSH-nyckel genererad: {key_file}")
    except subprocess.CalledProcessError:
        print("❌ Fel vid generering av SSH-nyckel!")
    except FileNotFoundError:
        print("❌ ssh-keygen inte installerad!")

def list_ssh_keys():
    """Listar befintliga SSH-nycklar"""
    print("\n--- Befintliga SSH-nycklar ---")
    
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        print("❌ SSH-katalog hittades inte!")
        return
    
    key_files = []
    for file in os.listdir(ssh_dir):
        if file.startswith('id_') and not file.endswith('.pub'):
            key_files.append(file)
    
    if key_files:
        print("🔑 SSH-nycklar:")
        for key in key_files:
            key_path = os.path.join(ssh_dir, key)
            pub_key_path = key_path + '.pub'
            
            if os.path.exists(pub_key_path):
                try:
                    with open(pub_key_path, 'r') as f:
                        pub_key = f.read().strip()
                    print(f"  {key}: {pub_key}")
                except:
                    print(f"  {key}: (kunde inte läsa publik nyckel)")
            else:
                print(f"  {key}: (ingen publik nyckel)")
    else:
        print("❌ Inga SSH-nycklar hittades!")

def copy_public_key():
    """Kopierar publik SSH-nyckel"""
    print("\n--- Kopiera publik SSH-nyckel ---")
    
    ssh_dir = os.path.expanduser("~/.ssh")
    pub_keys = []
    
    for file in os.listdir(ssh_dir):
        if file.endswith('.pub'):
            pub_keys.append(file)
    
    if not pub_keys:
        print("❌ Inga publika SSH-nycklar hittades!")
        return
    
    print("Tillgängliga publika nycklar:")
    for i, key in enumerate(pub_keys, 1):
        print(f"  {i}. {key}")
    
    try:
        choice = int(input("Välj nyckel att kopiera: ")) - 1
        if 0 <= choice < len(pub_keys):
            key_file = os.path.join(ssh_dir, pub_keys[choice])
            with open(key_file, 'r') as f:
                pub_key = f.read().strip()
            
            # Kopiera till urklipp
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=pub_key, text=True, check=True)
                print("✅ Publik nyckel kopierad till urklipp!")
            except:
                print("📋 Publik nyckel:")
                print(pub_key)
                print("\nKopiera ovanstående nyckel manuellt.")
        else:
            print("Ogiltigt val!")
    except (ValueError, IndexError):
        print("Ogiltigt val!")

if __name__ == "__main__":
    main()
