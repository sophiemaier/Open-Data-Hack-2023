import os
from openai import OpenAI
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import plotly.express as px

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        with pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ''.join(pdf_reader.pages[i].extract_text() for i in range(len(pdf_reader.pages)))
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
    return text

def ask_chatgpt(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", #gpt-4
        messages=[
            {"role": "system", "content": "Du sollst eine Projektanalyse erstellen. Die Projektanalyse soll auf Basis der Nachhaltigkeitsprinzipien des Cercle Indicateurs des Bundes der Schweiz basieren. Die Schwerpunkte sind Umwelt, Wirtschaft, Gesellschaft und Governance."},
            {"role": "user", "content": prompt}
        ]
    )
    content = completion.choices[0].message.content
    return content

def main():
    st.title("PDF Analyzer - GreenLight")

    pdf_file = st.file_uploader("PDF-Datei hochladen", type=["pdf"])
    pdf_text = extract_text_from_pdf(pdf_file)

    categories = {
        "Natürliche Lebensgrundlagen": {
            "Fokus": "Natur, Biodiversität, Umweltschutz",
            "Wirkung": "Erhalt und Förderung naturnaher Landschaften und der Biodiversität, Erhalt und Förderung der Artenvielfalt im Siedlungsraum, Erhalt und Förderung natürlicher Ressourcen., Vermeidung schädlicher Einwirkungen auf die Umwelt (Luft, Boden, Wasser, Lärm und Strahlung)"
        },
        "Energie und Klima": {
            "Fokus": "Fokus Energieversorgung, Energieverbrauch, Klimaschutz, Anpassung an den Klimawandel",
            "Wirkung": "Umstellung der Energieproduktion und -nutzung auf erneuerbare und lokale Energieformen, Ausbau der Energie-Speicherkapazitäten, Energieverbrauch minimieren (Effizienz), CO2-Emissionen vermeiden und senken, Vermeidung/Verminderung von Hitzeinseln durch Begrünung, Durchlüftung, Wasserflächen und Entsiegelung, Förderung der Wasserretention (Schwammstadt)"
        }
    }

    data = []

    for category, values in categories.items():
        focus = values["Fokus"]
        description = values["Wirkung"]

        queries = [
            "Gib numerisch an, wie sich das Projekt auf diesen Fokus der Nachhaltigkeit auswirkt. Verwende die Skala: 2 = sehr nachhaltig, 1 = eher nachhaltig, 0 = neutral, -1 = wenig nachhaltig, -2 = nicht nachhaltig. Die Ausgabe sollte nur ein nummerisches Zeichen sein (d.h. max. 2 Zeichen), basierend auf dieser Skala. Keine Begründung erforderlich.",
            "Auf Baisis deiner vorherigen Antwort: Begründe zusammenfassend in drei Bulletpoints (•) (max. 10 Wörter pro Punkt) die Kategorisierung  (2 = sehr nachhaltig, 1 = eher nachhaltig, 0 = neutral, -1 = wenig nachhaltig, -2 = nicht nachhaltig) des Projekts hinsichtlich des Fokusses auf die Nachhaltigkeit. Die Erwähnung der Kategorie und der Zahl darf nicht gemacht werden. Maximal 100 Zeichen und keine nummerischen Werte.",
            "Gib zusammenfassend in drei Bulletpoints (•) (max. 10 Wörter pro Punkt) das Optimierungspotenzial und mögliche Synergien des Projekts an hisichtlich des Fokusses der Nachhaltigkeit. Vermeide Erwähnung der Kategorie. Maximal 100 Zeichen."
        ]


        row_data = [category, focus, description]

        for i, query in enumerate(queries):
            full_query = f"{query} Beantworte dies gezielt auf den Fokus '{category} - {focus} - {description}' {pdf_text}"
            answer = ask_chatgpt(full_query)

            if i == 0:
                # First query goes to "Wirkung"
                row_data = [category, focus, answer, None, None]
            elif i == 1:
                # Second query goes to "Begründung Bewertung"
                row_data[3] = answer
            elif i == 2:
                # Third query goes to "Optimierung / Synergien"
                row_data[4] = answer


        data.append(row_data)

    # Erstelle DataFrame und zeige Tabelle an
    df = pd.DataFrame(data, columns=["Thema/Indikator", "Fokus", "Wirkung", "Begründung Bewertung", "Optimierung / Synergien"])
    
    # Färbe die Zahlen in der Spalte "Wirkung" entsprechend ein
    df_style = df.style.applymap(lambda x: 'background-color: #00CC00' if x == 2 else ('background-color: #66FF66' if x == 1 else ('background-color: #FFFFFF' if x == 0 else ('background-color: #FF9999' if x == -1 else 'background-color: #CC0000'))), subset=["Wirkung"])

    # Zeige die formatierte Tabelle in Streamlit an
    st.table(df_style)

    
    # Erstelle ein Area-Chart
    area_chart = px.area(df, x="Thema/Indikator", y="Wirkung", title="Wirkung auf Thema/Indikator", labels={"Wirkung": "Numerische Wirkung"})
    st.plotly_chart(area_chart)

if __name__ == "__main__":
    main()
