# Michele De Rose - Intelligenza Artificiale Distribuita

Eseguire `python atm_node.py <id_nodo>` per ogni nodo (sono 4 in totale, da 1 a 4).

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

# Ulteriori dettagli
Ulteriori dettagli sono disponibili nel file [Dettagli implementativi e spiegazione del codice.pdf](https://github.com/miderose/MicheleDeRose-IntelligenzaArtificialeDistribuita/blob/main/Dettagli%20implementativi%20e%20spiegazione%20del%20codice.pdf)

# Video
Link del video: [Token - 4 nodi ATM](https://github.com/miderose/MicheleDeRose-IntelligenzaArtificialeDistribuita/blob/main/Token%20-%204%20nodi%20ATM.mp4)