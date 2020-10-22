from rdflib import Graph, URIRef
import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact, interactive
from IPython.display import IFrame, clear_output

def task1():
    soDownloadButton = widgets.Button(description="Download Symptom ontology")
    label = widgets.Label(description="")
    so = widgets.Output()
    display(soDownloadButton, label, so)
    global df
    df = pd.DataFrame(columns=["so_uri", "soid", "label", "subclassof", "aliases"])
    @soDownloadButton.on_click
    def downloadSO(b):
        # Download
        global df
        label.value = "\nDownloading the Symptom Ontology..."
        url = "https://raw.githubusercontent.com/DiseaseOntology/SymptomOntology/main/symp.owl"

        # Parse owl file into a graph object
        symptomGraph = Graph()
        symptomGraph.parse(url, format="xml")

        qres = symptomGraph.query(
        """
           PREFIX obo: <http://www.geneontology.org/formats/oboInOwl#>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>

           SELECT DISTINCT ?so_uri ?soid ?label (GROUP_CONCAT(?subClassOf;separator="|") as ?subclasses)
                                                (GROUP_CONCAT(?exactsynonym;separator="|") as ?exact_synonyms)
           WHERE {
            ?so_uri obo:id ?soid ;
                      rdfs:label ?label .
            FILTER NOT EXISTS {?so_uri owl:deprecated true}
             OPTIONAL {?so_uri rdfs:subClassOf ?subClassOf ;}
             OPTIONAL {?so_uri oboInOwl:hasExactSynonym ?exactsynonym}
           }
           GROUP BY ?so_uri """)

        for row in qres:
            df = df.append({
             "so_uri": str(row[0]),
             "soid": str(row[1]),
             "label":  str(row[2]),
             "subclassof": str(row[3]),
             "aliases": str(row[4])
              }, ignore_index=True)
        label.value = ""
        with so:    
            display(df)
            
def task2():
    @interact
    def browse(symptom=df["label"].tolist()):
        symptomrow = df[df["label"]==symptom].T
        label = symptomrow.loc["label"].values[0]
        soid = symptomrow.loc["soid"].values[0].replace("SYMP:","")
        WikipediaLabelSearchTab = IFrame(src='https://en.wikipedia.org/w/index.php?&fulltext=1&ns0=1&title=Special%3ASearch&search='+label, width=1000, height=600)
        wdLabelSearch = IFrame(src='https://www.wikidata.org/w/index.php?title=Special:Search&profile=advanced&fulltext=1&advancedSearch-current=%7B%7D&ns0=1&ns120=1&search='+label, width=1000, height=600)
        wdqsTab=IFrame(src="https://query.wikidata.org/#SELECT%20%3Fsymptom%20%3FsymptomLabel%20WHERE%20%7B%0A%20%20%20%20%3Fsymptom%20wdt%3AP8656%20%22"+soid+"%22%20.%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%7D", width=1000, height=600)
        resultTab = IFrame(src="https://query.wikidata.org/embed.html#SELECT%20%3Fsymptom%20%3FsymptomLabel%20WHERE%20%7B%0A%20%20%20%20%3Fsymptom%20wdt%3AP8656%20%22"+soid+"%22%20.%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22%5BAUTO_LANGUAGE%5D%2Cen%22.%20%7D%0A%7D", width=1000, height=600)
        tab1 = widgets.Output()
        tab2 = widgets.Output()
        tab3 = widgets.Output()
        tab = widgets.Tab(children=[
            tab1,
            tab2,
            tab3])
        with tab1:
            display(WikipediaLabelSearchTab)
        with tab2:
            display(wdLabelSearch)
        with tab3:
            display(wdqsTab)

        tab.set_title(0, 'in Wikipedia')
        tab.set_title(1, 'in Wikidata')
        tab.set_title(2, 'SPARQL')
        return display(tab)