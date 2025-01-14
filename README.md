# Produzione di rifiuti in Europa

## Run
Per avviare l'applicazione è sufficiente digitare il comando **" uv run streamlit run Generazione_rifiuti.py"** sul terminale
Affinchè si riesca a visualizzare tutti i grafici e ad usare i link presenti è necessario essere connessi ad **internet**.

## Descrizione dei dati 
L'applicazione contiene un'analisi fatta sui dati riguardanti la generazione di rifiuti da parte dei Paesi Europei membri UE, con particolare attenzione alle attività economiche (e delle famiglie) coinvolte, alla pericolosità dei rifiuti e all' evoluzione nel tempo della quantità prodotta. Il database di partenza contiene anche informazioni sulle categorie di rifiuti, ma non si è considerata questa variabile in quanto non d'interesse per lo studio che si voleva fare. 
Oltre ai dati principali su cui verte l'analisi, sono presenti anche le informazioni riguardanti il PIL pro-capite per ogni paese.L'indicatore è calcolato come il rapporto tra il PIL reale e la popolazione media di un anno specifico. Il PIL misura il valore della produzione finale totale di beni e servizi prodotti da un'economia in un determinato periodo di tempo. Include beni e servizi che hanno mercati (o che potrebbero avere mercati) e prodotti che sono prodotti da amministrazioni pubbliche e istituzioni non profit. È una misura dell'attività economica ed è anche utilizzata come proxy per lo sviluppo degli standard di vita materiali di un paese. Questi dati vengono utilizzati nell'analisi per vedere se c'è una correlazione tra kg di rifiuti generati e pil pro capite.
Maggiori informazioni sulle **caratteristiche dei dati** e sulle **fonti** sono riportate all'inizio dell'applicazione nel paragrafo "Introduzione e descrizione dei dati".

## Obiettivo
Lo scopo dell'analisi è:
- mettere in luce l'evoluzione temporale dei paesi nella produzione totale di rifiuti
- evidenziare quelli che sono i maggiori produttori e la pericolosità dei rifiuti generati
- individuare il settore economico prevalente per ogni stato
- determinare se ci sia una correlazione tra PIL pro capite e kg di rifuti prodotti pro capite

\n Oltre all'analisi di per sè, l'obiettivo dell'applicazione è quello di permettere all'utente che la utilizza di **interagire** liberamente con i grafici presentati, facendosi guidare talvolta dai suggerimenti ed osservazioni riportati.

## Preprocessing
I dati originali non sono in forma tidy e presentano molte variabili per cui vi è stato un lavoro di manipolazione per renderli adatti al tipo di analisi che si intendeva fare. Vista la complessità si è deciso di creare una "tabella madre" che contenesse caratteristiche comuni a tutte le successive tabelle, le quali sono state poi lavorate individualmente filtrando le proprietà specifiche in base al loro scopo.

### Strade alternative
Vista la presenza di diversi valori nulli si era tentato di sostituirli con previsioni fatte sulla base dei dati presenti negli anni precedenti e futuri.
I tentativi consistevano in:
- raggruppamento per paese e settore e aggregazione dei valori applicando strategie "forward/backward" di sostituzione di valori nulli
    data
    .group_by(["geo","nace_r2"])
    .agg(pl.col("values").fill_null(strategy="forward/backward").alias("previsioni"))
- interpolazione di una colonna year rispetto ad un'altra colonna year
    table()
    .with_columns(previsioni=pl.col("2004").interpolate_by("2006"))
- interpolazione tramite metodi "linear/nearest" 
    (...).interpolate(method="linear/nearest")

 Purtroppo non è stato possibile raggiungere risultati soddisfacenti per cui si è deciso di procedere con i dati originali. 