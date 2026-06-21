# Michele De Rose - Intelligenza Artificiale Distribuita

Eseguire `python atm_node.py <id_nodo>` per ogni nodo.

Esempio:

```bash
python atm_node.py 4
python atm_node.py 3
python atm_node.py 2
python atm_node.py 1
```

Requisito: Python 3 (usato v3.11 per lo sviluppo).

Il nodo 1 inietterà il token iniziale con saldo 1000, quindi è consigliabile farlo partire per ultimo, quando gli altri sono pronti. 
A quel punto, si vedranno i log di ogni nodo (si raccomanda di tenere aperte 4 finestre (una per ogni nodo) per osservare il passaggio del token e l'aggiornamento del saldo) e, se tutto funziona, il token tornerà a girare in eterno nell'anello, aggiornando il saldo ogni volta che passa da un nodo.

In caso di errore, il programma si fermerà e stamperà un messaggio di errore. Controllare il file atm.log per maggiori dettagli.  