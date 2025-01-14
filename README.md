# Produzione di rifiuti in Europa

## Run
Per avviare l'applicazione è sufficiente digitare il comando **" uv run streamlit run Generazione_rifiuti.py"** sul terminale.

Affinchè si riesca a visualizzare tutti i grafici e ad usare i link presenti è necessario essere connessi ad **internet**.
 
L'applicazione va eseguita con il tema chiaro. 

## Descrizione dei dati 
L'applicazione contiene un'analisi fatta sui dati riguardanti la generazione di rifiuti da parte dei Paesi Europei membri UE, con particolare attenzione alle attività economiche (e delle famiglie) coinvolte, alla pericolosità dei rifiuti e all' evoluzione nel tempo della quantità prodotta. Il database di partenza contiene anche informazioni sulle categorie di rifiuti, ma non si è considerata questa variabile in quanto non d'interesse per lo studio che si voleva fare. 

Oltre ai dati principali su cui verte l'analisi, sono presenti anche le informazioni riguardanti il PIL pro-capite per ogni paese. L'indicatore è calcolato come il rapporto tra il PIL reale e la popolazione media di un anno specifico. Il PIL misura il valore della produzione finale totale di beni e servizi prodotti da un'economia in un determinato periodo di tempo. Include beni e servizi che hanno mercati (o che potrebbero avere mercati) e prodotti che sono prodotti da amministrazioni pubbliche e istituzioni non profit. È una misura dell'attività economica ed è anche utilizzata come proxy per lo sviluppo degli standard di vita materiali di un paese. Questi dati vengono utilizzati nell'analisi per vedere se c'è una correlazione tra kg di rifiuti generati e pil pro capite.

Maggiori informazioni sulle **caratteristiche dei dati** e sulle **fonti** sono riportate all'inizio dell'applicazione nel paragrafo "Introduzione e descrizione dei dati".

## Obiettivo
Lo scopo dell'analisi è:
- mettere in luce l'evoluzione temporale dei paesi nella produzione totale di rifiuti
- evidenziare quelli che sono i maggiori produttori e la pericolosità dei rifiuti generati
- individuare il settore economico prevalente per ogni stato
- determinare se ci sia una correlazione tra PIL pro capite e kg di rifuti prodotti pro capite

Oltre all'analisi di per sè, l'obiettivo dell'applicazione è quello di permettere all'utente che la utilizza di **interagire** liberamente con le funzionalità presenti, potendo scegliere quali dati osservare in base a ciò che più interessa, facendosi guidare talvolta dai suggerimenti ed osservazioni riportati.

## Preprocessing
I dati originali per entrambi i dataset non sono in forma tidy e presentano molte variabili per cui vi è stato un lavoro di manipolazione per renderli adatti al tipo di analisi che si intendeva fare. 

Per il **primo database**, quello sui rifiuti, vista la complessità si è deciso di creare una "tabella madre" che contenesse caratteristiche comuni a tutte le successive tabelle, le quali sono state poi lavorate individualmente filtrando le proprietà specifiche in base al loro scopo. Nella tabella di partenza sono state tolte tutte le colonne che avevano valori uguali per tutte le unità come DATAFLOW, frequenza, e LAST UPDATE. E' stata eliminata anche la colonna delle flags. Si è tolta l'Albania perchè non informativa per nessun tipo di analisi e si è scelto di considerare le **categorie** di rifiuti nel loro complesso.
Per riuscire a rendere visibile la tabella si è scelto di considerare solo le colonne con la pericolosità complessiva e con l'unità di misura le tonnellate. Si è fatta un'operazione di pivot tra tempo e valori e si sono ordinati i paesi per ordine alfabetico. Alcune tabelle successive sono state costruite a partire da questa con un'operazione di unpivot e filtraggio delle colonne necessarie, altre derivano dalla tabella madre in quanto necessitavano di una diversa unità di misura o della differenziazione tra pericolosità/non-pericolosità.

Anche per il **secondo database**, quello sul PIL pro capite, sono state tolte le flags e tutte le colonne che avevano valori uguali per tutte le unità come DATAFLOW, frequenza, e LAST UPDATE. Come unità si è scelto l'euro per capita e per gli anni si sono considerati solo quelli compatibili con il primo database. Si è poi effettuato un pivot su tempo e valori seguito da un unpivot per creare una colonna anno contenente i gdp per capita.
Per effettuare l'analisi sulla correlazione tra PIL e Kg pro capite è stato eseguito un inner join tra le due tabelle attraverso "geo" e "year".

### Strade alternative
Vista la presenza di diversi valori nulli si era tentato di sostituirli con **previsioni** fatte sulla base dei dati presenti negli anni precedenti e futuri.
I tentativi consistevano in:
- raggruppamento per paese e settore e aggregazione dei valori applicando strategie "forward/backward" di sostituzione di valori nulli (funzioni group_by(), agg(), fill_null(strategy=))
- interpolazione di una colonna year rispetto ad un'altra colonna year (funzione interpolate_by())
- interpolazione tramite metodi "linear/nearest" (funzione interpolate(method=))

 Purtroppo non è stato possibile raggiungere risultati soddisfacenti per cui si è deciso di procedere con i dati originali. 
