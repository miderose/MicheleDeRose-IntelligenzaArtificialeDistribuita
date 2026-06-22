import sys
import socket
import json
import time
import threading

# Configurazione del sistema Token Ring
NODES_CONFIG = {
    1: {"port": 5001, "next_port": 5002, "transaction": None},
    2: {"port": 5002, "next_port": 5003, "transaction": {"type": "prelievo", "amount": 200}},
    3: {"port": 5003, "next_port": 5004, "transaction": {"type": "deposito", "amount": 100}},
    4: {"port": 5004, "next_port": 5001, "transaction": {"type": "prelievo", "amount": 500}}
}

class ATMNode:
    def __init__(self, node_id):
        self.node_id = node_id
        config = NODES_CONFIG[node_id]
        self.port = config["port"]
        self.next_port = config["next_port"]
        self.pending_transaction = config["transaction"]
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(1)
        
        self.next_node_socket = None

    def log(self, message):
        """Stampa a schermo e scrive su file di log con timestamp human-readable."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [ATM{self.node_id}] {message}"
        print(log_line)
        try:
            with open("atm.log", "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            print(f"[!] Errore di scrittura su atm.log: {e}")

    def start(self):
        self.log(f"ATM avviato. In attesa di connessioni sulla porta {self.port}...")
        
        # Avvia thread per accettare la connessione dal nodo precedente
        accept_thread = threading.Thread(target=self.accept_connection)
        accept_thread.daemon = True
        accept_thread.start()

        # Connessione al nodo successivo (con retry per attendere che sia online)
        self.connect_to_next()

        # Se è il nodo 1, inietta il token iniziale dopo aver atteso che l'anello sia formato
        if self.node_id == 1:
            self.log("Attendo 5 secondi affinché tutti i nodi siano connessi...")
            time.sleep(5)
            self.inject_token(1000)

        # Loop principale per mantenere in vita il thread principale
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("ATM in chiusura.")

    def accept_connection(self):
        """Accetta la connessione dal nodo precedente nell'anello logico."""
        conn, addr = self.server_socket.accept()
        self.log("Connessione accettata dal nodo precedente.")
        self.handle_messages(conn)

    def connect_to_next(self):
        """Si connette al nodo successivo nell'anello logico."""
        self.next_node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        while not connected:
            try:
                self.next_node_socket.connect(('localhost', self.next_port))
                connected = True
                self.log(f"Connesso al nodo successivo sulla porta {self.next_port}.")
            except ConnectionRefusedError:
                time.sleep(1) # Riprova tra 1 secondo

    def inject_token(self, initial_balance):
        """Inietta il token iniziale nell'anello (eseguito solo da ATM1)."""

        # il token è un json con il saldo.
        token = {"type": "TOKEN", "balance": initial_balance}
        self.log(f"--- INIZIO --- Ricevuto (appena creato in realtà) token iniziale con saldo: {initial_balance}")
        self.forward_token(token)

    def handle_messages(self, conn):
        """Ascolta continuamente i messaggi in ingresso dal nodo precedente."""
        buffer = ""
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                # Estrae messaggi completi separati da newline
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    message = json.loads(message_str)
                    
                    if message["type"] == "TOKEN":
                        self.process_token(message)
                        
            except Exception as e:
                self.log(f"Errore di connessione: {e}")
                break

    def process_token(self, token):
        """Logica della SEZIONE CRITICA: gestione del token."""

        # Attendo un secondo perchè i print nelle finestre affiancate così si vedono meglio
        # (in pratica simuliamo la latenza di rete...)
        time.sleep(1)

        self.log(f"RICEZIONE DEL TOKEN (Saldo corrente: {token['balance']})")
        
        # Se il nodo ha una transazione in sospeso, la esegue
        if self.pending_transaction:
            self.log("INIZIO DELLA TRANSAZIONE")

            # mi serve per stampare il log, più in basso.
            initial_balance = token["balance"]

            current_balance = initial_balance
            trans_type = self.pending_transaction["type"]
            amount = self.pending_transaction["amount"]
            
            success = False

            # verifico che amount non sia negativo
            if amount < 0:
                self.log("L'importo della transazione deve essere sempre positivo.")
            
            # se è un prelievo, controllo se ci sono abbastanza fondi
            elif trans_type == "prelievo":
                self.log(f"Richiesta di prelievo: {amount}")
                if current_balance >= amount:
                    current_balance -= amount
                    self.log("Transazione completata con successo.")
                    success = True
                else:
                    self.log("Fondi insufficienti per il prelievo.")
            
            # deposito...
            elif trans_type == "deposito":
                self.log(f"Richiesta di deposito: {amount}")
                current_balance += amount
                self.log("Transazione completata con successo.")
                success = True
            
            # aggiorno il saldo nel token
            token["balance"] = current_balance

            # rimuovo la transazione in sospeso: ora è stata elaborata
            self.pending_transaction = None
            
            # stampo il log finale della transazione
            if success:
                trans_type_upper = trans_type.upper()
                self.log(f"*** FINE DELLA TRANSAZIONE: SALDO INIZIALE {initial_balance} *** {trans_type_upper} {amount} *** SALDO AGGIORNATO: {current_balance} ***")
            else:
                trans_type_upper = trans_type.upper()
                self.log(f"*** FINE DELLA TRANSAZIONE (FALLITA). SALDO INIZIALE {initial_balance} *** {trans_type_upper} {amount} (Non eseguita) *** SALDO ATTUALE: {current_balance} ***")
        else:
            self.log("Nessuna transazione in sospeso.")
            
        # Inoltro il token al nodo successivo (piccolo sleep solo per migliorare la visibilità dei print)
        time.sleep(1)
        self.forward_token(token)

    def forward_token(self, token):
        """Invia il token al nodo successivo."""
        self.log("INOLTRO DEL TOKEN al nodo successivo...")
        message_str = json.dumps(token) + '\n'
        self.next_node_socket.sendall(message_str.encode('utf-8'))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python atm_node.py <node_id>")
        sys.exit(1)
        
    node_id = int(sys.argv[1])
    if node_id not in NODES_CONFIG:
        print("Node ID deve essere tra 1 e 4.")
        sys.exit(1)
        
    node = ATMNode(node_id)
    node.start()
