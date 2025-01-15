import polars as pl
import streamlit as st
import altair as alt
import geopandas as gpd

with st.sidebar:
    st.title("Indice")
    st.divider()
    st.write('''
- Introduzione e descrizione dei dati
    - Fonti
- Presentazione dei dati
- Evoluzione temporale 
    - 27 peasi nel loro complesso
    - Confronto tra paesi
- Produzione totale di rifiuti per pericolosità e anno
- Settore prevalente per paese e anno
- Correlazione tra PIL e totale di rifiuti prodotti (pro capite) per anno
- Generazione di rifiuti pro-capite (in kg) per settore e anno
    - Grafico a barre
    - Cartina d'Europa
- Conclusioni
        
             ''')
    st.divider()

st.write(" # Produzione di rifiuti in Europa")
url1=("https://ec.europa.eu/eurostat/databrowser/view/env_wasgen__custom_14750179/default/table?lang=en")
url2=("https://ec.europa.eu/eurostat/databrowser/view/sdg_08_10/default/table?lang=en")
st.write(f''' 
### Introduzione e descrizione dei dati
La seguente analisi verterà sulla *generazione di rifiuti* da parte dei Paesi Europei, con particolare attenzione alle attività economiche (e delle famiglie) coinvolte, alla pericolosità dei rifiuti e all' evoluzione nel tempo della quantità prodotta.

Le informazioni sono disaggregate per:
-  **fonti**: 19 attività commerciali secondo la classificazione NACE rev.2 e attività delle famiglie in ambito domestico.
             La generazione di rifiuti è quindi attribuita ad attività di produzione o di consumo.
-  **categorie** di rifiuti (secondo la Classificazione Europea dei Rifiuti a fini statistici). 
> Il **periodo di riferimento** è strutturato ad intervalli biennali e va dal 2004 al 2022.  Per il primo anno, il 2004, gli Stati membri hanno potuto chiedere l'autorizzazione a non fornire parte delle informazioni riguardante i rifiuti 
dei settori "Agricolture and fishing" e "Services", perciò per alcuni paesi questi valori sono mancanti.         

> Le **misurazioni** sono disponibili sia in tonnellate di rifiuti che in kg pro-capite, sulla base della media annua della popolazione.

\nGli Stati membri sono liberi di decidere sulle **modalità di raccolta** dei dati, ma le opzioni generali sono: indagini, fonti amministrative, stime statistiche o una combinazione di metodi.

Le informazioni sul trattamento dei rifiuti sono suddivise in 5 tipologie di **trattamento** (recupero, incenerimento con recupero energetico, 
altri incenerimenti, smaltimento a terra e trattamento a terra) e in categorie di rifiuti.

\n *A lato è possibile visualizzare un **indice** dei punti che si analizzeranno nel corso dell'analisi. Per visualizzarlo è sufficente cliccare sulla freccia in alto a sinistra*
''')

if st.button("📍 Fonti "):
    st.write(f'''
I dati in seguito analizzati provengono dal sito **Eurostat**, in particolare ci si riferisce ai database:
- [Generation of waste by waste category, hazardousness and NACE Rev. 2 activity]({url1})

- [Real GDP per capita]({url2})
             ''')
st.divider()

st.write('''
### Presentazione dei dati
La **tabella** riporta i dati sulla produzione di rifiuti (in tonnellate) nei diversi settori economici per ogni paese membro dell'UE.

Per comodità di *rappresentazione* si sono qui considerati i rifiuti pericolosi e non pericolosi nel loro totale.
\n ❗L'**esclusione dell'Albania** è dovuta alla quasi totale assenza di dati in ogni anno/attività. 


         ''')


start_data = (pl
            .read_csv("Gen_of_waste_all.csv", separator=",", null_values=[":", ""])
            .drop(pl.col("DATAFLOW","LAST UPDATE", "OBS_FLAG", "freq"))
            .select(pl.col("geo", "unit", "hazard", "nace_r2","TIME_PERIOD", "OBS_VALUE", "waste")
            .filter(pl.col("geo") != "Albania", 
                    pl.col("waste") == "Total waste")))

@st.cache_data    
# tabella tidy da prioiettare
def table():
    return (      
    start_data
    .filter(pl.col("hazard") == "Hazardous and non-hazardous - total",
            pl.col("unit") == "Tonne")
    .select(pl.col("*").exclude("hazard", "unit", "waste"))
    .pivot(on="TIME_PERIOD", values="OBS_VALUE")
    .sort(by="geo")
    )
st.write(table())

#  data
# .group_by(["geo","nace_r2"])
# .agg(pl.col("values").fill_null(strategy="forward/backward").alias("previsioni"))

# table()
# .with_columns(previsioni=pl.col("2004").interpolate_by("2006"))

data= (
    table()
    .unpivot(index=["geo", "nace_r2"], 
                      value_name="values", 
                      variable_name="year")
    .filter(pl.col("geo")!= "European Union - 27 countries (from 2020)",
            pl.col("geo") != "European Union - 28 countries (2013-2020)")
    .sort(["nace_r2", "geo", "year"])  
    )

st.divider()

st.write('''
### Evoluzione temporale della produzione di rifiuti
#### Considerazione dei 27 paesi UE nel loro complesso         
 Il seguente grafico mette in luce l'evoluzione della produzione **totale** di rifiuti negli anni dal 2004 al 2022 da parte dei paesi oggetto di studio, **senza distinzione per attività economica**.
Nel periodo 2004 -2020 vengono considerati **tutti i 27 paesi**   , mentre per l'intervallo 2020 - 2022 i valori si riferiscono a 26 paesi in quanto l'Inghilterra, uscendo dall'UE, non ha più fornito i propri dati.
  
\n Il **calo** degli ultimi 2 anni (2020-2022) va attribuito alla mancanza di un paese nel conteggio più che ad un' effettiva diminuzione della produzione di rifiuti. 
Si può invece ipotizzare che, tenendo conto dell'andamento passato, il totale sarebbe stato in lieve aumento o pressocchè stazionario.
\n Nell'asse delle ascisse sono riportati gli *anni*, mentre in quello delle ordinate i *valori* per ogni anno in tonnellate.
\n 💡 _Posizionandosi con il cursore sopra alle barre è possibile visualizzare "un'etichetta" che riporta il corrispettivo anno e il valore di rifiuti totali.
Si può anche scegliere di visualizzare i dati in forma tabellare cliccando sopra "Data"_

         ''')
data1= (table()
        .unpivot(index=["geo", "nace_r2"], 
                      value_name="values", 
                      variable_name="year")
        .filter(pl.col("geo") == ("European Union - 28 countries (2013-2020)" ),
                pl.col("nace_r2") == "All NACE activities plus households")
        .pivot(on="year", values="values")
        .with_columns(pl.col("2020").fill_null(2153170000), # 2020 2153170000
                      pl.col("2022").fill_null(2233120000)) # 2022 2233120000
        .unpivot(index=["geo", "nace_r2"], 
                      value_name="values", 
                      variable_name="year")
        .select(pl.col("*").exclude("geo", "nace_r2"))
        )

line = alt.Chart(data1).mark_line(color="red").encode(
    x=alt.X('year').axis(labelAngle=-40, titleColor="black", title="Years"),
    y=alt.Y('values').axis(domain=False, titleAngle=0, titleAlign="right", title="Tonnes", titleColor="black")
    ).properties(width=600, height=400)

bar= alt.Chart(data1).mark_bar(color="orange", opacity=0.4).encode(
    x="year",
    y="values"
)
tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
tab1.altair_chart(bar+line)
tab2.write(data1)


st.divider()

st.write("""
### Confronto tra paesi
#### Come si è evoluta la produzione di rifiuti nei vari stati dal 2004 al 2022?
Il grafico precedente permetteva di osservare l'andamento dei paesi nel loro complesso, ma che tipo di evoluzione ha avuto ogni singolo stato?
Come si presenta rispetto agli altri?
\nPer rispondere a queste domande è sufficiente selezionare uno o più stati dei quali si è interessati.
Il grafico permette poi di effettuare un **confronto**, osservandone al contempo l'**evoluzione individuale**.

Nell'asse delle ascisse sono riportati gli *anni*, mentre in quello delle ordinate i *valori* per ogni anno, i quali
corrispondo alla somma di rifiuti prodotti per ogni settore.
Man mano che verranno selezionati i paesi apparirà una legenda sotto al grafico con il nome dello stato e il rispettivo colore. 
\n 💡 _Posizionandosi con il cursore sopra alle linee è possibile visualizzare "un'etichetta" che riporta l'anno considerato, il nome del paese e il corrispettivo valore di rifiuti totali_
""")


def time_evolution():
    countries = data.select("geo").unique().sort("geo")
    selected_country = st.multiselect(
        "Seleziona uno o più stati",
        countries,
        default="Italy"
    )
    st.line_chart(
        data 
        .filter(pl.col("nace_r2") == "All NACE activities plus households")
        .with_columns(pl.col("year").cast(pl.Int64))
        .filter(pl.col("geo").is_in(selected_country)),
        x="year",
        y="values",
        color="geo",
        use_container_width=True
    )

time_evolution()


if st.button("Osservazioni", icon="🔎"):
    st.write('''
        In generale la maggior parte dei paesi rimane pressocchè *stazionaria* attorno ad un valore con una tendenza a *crescere*.
        \nE' interessante, invece, notare come **Spagna**, **Romania** e **Bulgaria** abbiano un andamento *complessivamente decrescente*. 
        In particolare la Romania presenta un abbassamento significativo nel 2006 e 2012, mentre la Bulgaria a partire dal 2014.
         ''' )

st.divider()

st.write('''
### Produzione totale di rifiuti
#### Confronto in base alla *pericolosità* dei rifiuti senza distinzione tra le attività economiche 
Il seguente grafico evidenzia quali sono gli stati che producono la **maggiore quantità di scarti** considerando la somma delle 
tonnellate prodotte da ogni settore economico in riferimento all'anno selezionato. E' possibile scegliere l'anno che si desidera considerare.
\nNell'asse delle ascisse è riportato il *valore* della quantità di rifuti prodotti in tonnellate, mentre in quello delle ordinate gli *stati*.         
\n Si osserva che per tutti gli stati la proporzione di scarti **non-pericolosi** è nettamente superiore a quella dei pericolosi. 
**Germania** e **Francia** sembrano essere gli stati che ogni anno generano la maggiore quantità di rifiuti, seguite da **Italia**, **Polonia** e **Regno Unito**.

\n 💡 _Posizionandosi con il cursore sopra alle barre è possibile visualizzare "un'etichetta" che riporta il nome del paese e il corrispettivo valore di rifiuti totali_

         ''' )

def select_year(key):
    years = [2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022]
    year = st.pills("Seleziona l'anno", years, default=2022, key=key)
    return year

def hazardness():
    year= select_year("key0")
    datayear= (
        start_data
            .filter(pl.col("hazard") != "Hazardous and non-hazardous - total",
                    pl.col("unit") == "Tonne",
                    pl.col("nace_r2")!=  "All NACE activities plus households",
                    pl.col("geo")!= "European Union - 27 countries (from 2020)",
                    pl.col("geo") != "European Union - 28 countries (2013-2020)")
            .select(pl.col("*").exclude("unit", "waste", "nace_r2"))
            .with_columns(pl.col("TIME_PERIOD").cast(pl.Int64))
            .filter(pl.col("TIME_PERIOD")== year)
    )
    st.altair_chart(
        alt.Chart(datayear)
        .mark_bar()
        .encode(
            x=alt.X('sum(OBS_VALUE):Q', title='Total waste (tonnes)').axis(titleColor="black"),
            y=alt.Y('geo:N', title='Country', sort="-x").axis(titleColor="black"),
            color=alt.Color('hazard:N', legend=alt.Legend(title="Hazard"))
        ),
        use_container_width=True
    )
hazardness()
st.divider()

st.write('''
### Correlazione tra PIL e totale di rifiuti prodotti (pro capite)
Il seguente grafico di dispersione rappresenta la correlazione tra la **crescita economica pro capite**, misurata in euro pro capite, e la produzione di **rifiuti pro capite (in kg)** senza distinzione per settore. 
Ogni :blue[punto] rappresenta un paese e il legame tra questi è evidenziato da una retta di regressione :red[rossa].   
\nNell'asse delle ascisse è riportato il valore del *PIL pro capite*, mentre in quello delle ordinate i *kg pro capite* di rifiuti generati.
         
\n E' da notare  la presenza di alcuni **valori anomali** (detti "outliers") che influenzano la retta di regressione diminuendone la pendenza. 
 La retta non sembra, infatti, adattarsi al meglio ai dati, nonostante parga esserci una correlazione tra le due variabili.
 Anche la scarsa numerosità di dati(solo 27) non aiuta, ma si può individuare una lieve **correlazione positiva** per cui, 
 generalmente, all'aumentare del valore del PIL pro-capite aumenta il valore di kg di rifiuti prodotti pro capite. 
 Poichè alcuni dati presentano una relazione decisamente diversa è probabile che ci siano fattori non osservati in questo studio che hanno un'incidenza significativa.
         
\n 💡 _Posizionandosi con il cursore sopra ai punti è possibile visualizzare "un'etichetta" che riporta il nome del *paese* e i corrispettivi valori di rifiuti prodotti in *kg pro capite* e il *PIL pro capite*_ 
      
         ''')

@st.cache_data
def pil_table():
    return(
        pl
        .read_csv("Real_GDP_per_capita.csv", separator=",", null_values=[":", ""], schema_overrides= {"OBS_VALUE": pl.Float64})
        .drop(pl.col("DATAFLOW", "LAST UPDATE","freq",  "OBS_FLAG"))
        .select(pl.col("geo", "TIME_PERIOD", "unit", "na_item", "OBS_VALUE"))
        .filter(pl.col("unit")== "Chain linked volumes (2010), euro per capita",
                pl.col("TIME_PERIOD").is_in([2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022]) )
        .with_columns(pl.col("OBS_VALUE").cast(pl.Float64))
        .select(pl.col("*").exclude("na_item", "unit"))
        .pivot(on="TIME_PERIOD", values="OBS_VALUE")
        .unpivot(index="geo", value_name= "GDP_per_capita", variable_name="year")
    )

year2=select_year("key3")
data_kg2= (start_data
            .filter(pl.col("unit") == "Kilograms per capita",
                pl.col("hazard") == "Hazardous and non-hazardous - total",
                pl.col("nace_r2") == "All NACE activities plus households",
                pl.col("TIME_PERIOD")== year2)
            .select(pl.col("*").exclude("hazard", "unit", "waste"))
            .pivot(on="TIME_PERIOD", values= "OBS_VALUE")
            .unpivot(index=["geo", "nace_r2"], 
                    value_name="kg_pro_capite", 
                    variable_name="year")
            .with_columns(pl.col("kg_pro_capite").cast(pl.Float64))
        )

GDP_waste=(data_kg2.join(pil_table(), on=["geo", "year"], how="inner"))

line= alt.Chart(GDP_waste).mark_point().encode(
        x=alt.X('GDP_per_capita:Q').axis(titleColor="black"),
        y=alt.Y('kg_pro_capite').axis(titleColor="black")).transform_regression('GDP_per_capita', 'kg_pro_capite').mark_line(color="red")

points= alt.Chart(GDP_waste).mark_point(fill="blue").encode(
        x='GDP_per_capita:Q',
        y='kg_pro_capite:Q',
        tooltip=["geo:N", "kg_pro_capite", "GDP_per_capita"]
        ).properties(
            width=600,
            height=400 
        )
points+line

st.divider()

st.write('''
### Qual è il settore prevalente in ogni paese?
Il seguente grafico rappresenta la quantità di **rifiuti** generati (in tonnellate) da un paese in un dato anno suddivisa **per attività economiche(e familiare)**.
I valori sono rappresentati da delle barre ordinate in ordine decrescente in modo da mettere in risalto il settore **prevalente**. 
\nE' possibile scegliere l'anno e il paese che si è più interessati ad osservare, oltre alla modalità di rappresentazione: grafica o tabellare.
Si ricorda, inoltre, che per gli anni 2020-2022 non sono presenti dati per il Regno Unito!
\nNell'asse delle ascisse sono riportate le *tonnellate* di rifiuti prodotti, mentre in quello delle ordinate i *settori*.         
\n 💡 _Posizionandosi con il cursore sopra le barre è possibile visualizzare "un'etichetta" che riporta le tonnellate di rifuti prodotti e il settore a cui si riferiscono_
''')

def select_country(key):
    countries= data.select("geo").unique().sort("geo")
    country= st.selectbox("Seleziona il paese", countries, key= key)
    return country

year= select_year("key4")
country= select_country("keyc")
data_country=(
        data
        .with_columns(pl.col("year").cast(pl.Int64))
        .filter(pl.col("geo")== country, pl.col("year")== year, pl.col("nace_r2") != "All NACE activities plus households")
        .sort("values", descending=True)
        .select(pl.col("*").exclude("geo", "year"))
    )
chart=(alt.Chart(data_country).mark_bar().encode(
    x= alt.X("values").axis(titleColor="black", title="Tonnes" ),
    y= alt.Y("nace_r2", sort="-x").axis(titleColor="black", labelLimit=150, title="Settore"),
    color=alt.value("darkorange")
    ).properties(width=600))
tab3, tab4 = st.tabs(["📈 Chart", "🗃 Data"])
tab4.write(data_country)
tab3.altair_chart(chart)

st.divider()

st.write('''
### Generazione di rifiuti pro-capite (in kg) per settore
I 27 paesi membri dell'UE presentano naturalmente **dimensioni** geografiche, e quindi demografiche, **diverse**.
Ciò implica che stati più grandi e più densamente popolati produrranno una maggiore quantità di rifiuti rispetto a quelli più piccoli.
\nAllora la domanda che sorge spontanea è: come possiamo rendere i paesi confrontabili?
    Si può considerare un'altra unità di misura che li metta tutti sullo stesso piano: i **kg pro-capite**.
\nIn questa sezione è possibile scegliere l'**anno** e il **settore economico** dei dati che si è interessati a visualizzare.
         ''')

if st.button("Osservazioni", icon="🔎", key="k"):
    st.write('''
I dati si prestano a molteplici combinazioni. Vengono qui riportati alcuni suggerimenti di ricerca che potrebbero essere interessanti:
- settore: **"All NACE activities plus households"**
> Ancora una volta si possono considerare le attività nel loro complesso, ma in questo caso con misurazione in kg pro-capite. Che tipo di cambiamento comporta questo passaggio di unità di misura?

> Si nota che, mentre con la misurazione in tonnellate primeggiavano ogni anno Germania e Francia, con la rilevazione pro-capite la situazione è molto diversa. Emergono in particolare Finlandia, Estonia,Luxembourg, Svezia e Bulgaria.
 Nel 2022 ha avuto un considerevole incremento anche la Serbia.
             
- settore: **"Household"**
> Potrebbe essere interessante considerare l'ambito familiare, quindi ciò che riguarda i consumi domestici, in quanto è qualcosa che coinvolge tutte le persone e non solo alcuni settori economici. 

> Si possono considerare gli ultimi anni per vedere se c'è stato una diminuzione della quantità dei rifiuti prodotti in seguito all'aumento della sensibilizzazione per temi di salvaguardia dell'ambiente. 
 Si nota che mentre nel 2016, 2018, 2020 tutti gli stati avevano valori molto simili, nel 2022 i paesi del Nord ed Est Europa presentano un abbassamento rispetto agli altri.

> Molto interessante è anche l'**anno 2012** in quanto il Liechtenstein presenta un valore spropositato che fa sembrare tutti gli altri paesi molto bassi quando in realtà hanno valori molto simili a quelli degli anni precedenti.

             ''')

def select_activity(key):
    activities= data.select("nace_r2").unique().sort("nace_r2")
    activity= st.selectbox("Seleziona il settore", activities, key= key)
    return activity

year= select_year("key1")
nace= select_activity("key2")

data_kg= (start_data
            .filter(pl.col("unit") == "Kilograms per capita",
                pl.col("hazard") == "Hazardous and non-hazardous - total",
                pl.col("geo")!= "European Union - 27 countries (from 2020)",
                pl.col("geo") != "European Union - 28 countries (2013-2020)",
                pl.col("nace_r2") == nace,
                pl.col("TIME_PERIOD") == year)
            .select(pl.col("*").exclude("hazard", "unit", "waste"))
            .pivot(on="TIME_PERIOD", values= "OBS_VALUE")
            .unpivot(index=["geo", "nace_r2"], 
                    value_name="kg_pro_capite", 
                    variable_name="year")
            .with_columns(pl.col("kg_pro_capite").cast(pl.Float64))
            .sort(["nace_r2", "geo", "year"])
        )

st.divider()

st.write('''
##### Grafico a barre
Una prima visualizzazione dei dati è fornita dal seguente grafico avente nell'asse delle ascisse i *paesi* e in quello delle ordinate i *rifiuti in kg pro-capite*.
\n 💡 _Posizionandosi con il cursore sopra le barre è possibile visualizzare "un'etichetta" che riporta il paese e i corrispettivi kg pro capite_

''')
base = alt.Chart(data_kg).encode(
    y=alt.Y('kg_pro_capite:Q').axis(titleColor="black"),
    x=alt.X("geo:O", sort="-y").axis(titleColor="black"),
)
base.mark_bar() + base.mark_text(align='center', dy=-6)

st.write('''
    ##### Cartina dell'Europa
Un'ulteriore rappresentazione che permette un confronto visivo più immediato è la seguente cartina d'Europa.
\nOgni pease è colorato secondo una **scala di colori** che va dal giallo al rosso, ovvero da una più bassa produzione di rifuti pro-capite ad una più alta.
Vengono indicati in grigio tutti gli stati che non sono oggetto di studio in quanto non appartenenti all'Unione Europea o che appartengono ma non  presentano dati per l'anno/settore selezionati.
\nA lato è presente una **legenda** che mostra l'associazione tra colore e valore. Vista la natura dei dati, per rendere visibile la differenza tra paesi si è adottata una scala "square root".
\n 💡 _Posizionandosi con il cursore sopra agli stati colorati nella cartina è possibile visualizzare "un'etichetta" che riporta il nome del *paese* e il corrispettivo *valore* di rifiuti prodotti in kg pro-capite_ 

         ''')

@st.cache_data   
def get_geography():
    url = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"
    dati = gpd.read_file(url)
    return dati

world= get_geography()
data = world.merge(data_kg.to_pandas(), left_on="ADMIN", right_on="geo")

def add_map(chart):
    chart.save("map.html")
    with open("map.html") as fp:
        st.components.v1.html(fp.read(), width=800, height=800)
world = (
    alt.Chart(world)
    .properties(width=600, height=600)
    .mark_geoshape(color="lightgray", stroke="white")
)
chart = (
    alt.Chart(data)
    .properties(width=600, height=600)
    .mark_geoshape(stroke="white")
    .encode(
        alt.Color("kg_pro_capite").scale(scheme="yelloworangered", type="sqrt"), 
        alt.Tooltip(["ADMIN", "kg_pro_capite"])
    )
)
complete = (world + chart).project(  
        type="azimuthalEqualArea",
        scale=700,
        center=(10, 48)
)
add_map(complete)
st.divider()
st.write('''
### Conclusioni
I principali aspetti che sono emersi da questo breve studio sulla generazione di rifiuti da parte dei paesi europei sulla base degli anni dal 2004 al 2022 e degli ambiti economici e familiare sono:
- I 27 paesi considerati presentano nel loro complesso un lieve aumento nel corso degli anni. Gli stati presi singolarmente presentano oscillazioni ma con un andamento complessivo crescente, tranne alcune eccezioni
- Gli stati che producono la maggiore quantità di rifiuti in tonnellate sono Germania e Francia, ma principalmente si tratta per tutti di rifiuti non-pericolosi
- La correlazione tra PIL reale pro capite e rifiuti generati in kg pro capite sembra positiva, ma non si tratta di una relazione forte e va tenuta conto la presenza di diversi "outliers"
\nQuelle presentate qui sono solo alcune delle considerazioni che si possono fare. Altri risultati possono essere osservati intervenendo attivamente sui grafici messi a disposizione.
         ''')