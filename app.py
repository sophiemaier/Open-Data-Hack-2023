import os
import base64
import io
import pandas as pd
from openai import OpenAI
import streamlit as st
from PyPDF2 import PdfReader
import plotly.express as px
from PIL import Image
import requests

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Hier die Funktion definition platzieren
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
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du sollst eine Projektanalyse erstellen. Die Projektanalyse soll auf Basis der Nachhaltigkeitsprinzipien des Cercle Indicateurs des Bundes der Schweiz basieren. Die Schwerpunkte sind Umwelt, Wirtschaft, Gesellschaft und Governance."},
            {"role": "user", "content": prompt}
        ]
    )
    content = completion.choices[0].message.content
    return content

def get_table_download_link(df):
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as excel_writer:
        df.to_excel(excel_writer, index=False)
    excel_buffer.seek(0)
    b64 = base64.b64encode(excel_buffer.read()).decode('utf-8')
    return f'<a href="data:application/octet-stream;base64,{b64}" download="table_data.xlsx">Download Excel file</a>'

# Benutzerdefiniertes CSS für das Layout
st.markdown(
        """
        <style>
        
        .main {
            background-color: #FFFFFF; /* Hellgrau für den Hauptbereich */
            padding: 1em;
            border-radius: 10px; /* Abgerundete Ecken */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Schatten für den Hauptbereich */
        }

        .css-1d0s9cy {
            font-family: 'Arial', sans-serif; /* Schriftart ändern */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.markdown(
        """
        <style>
        .main {
            max-width: 1000px; /* Oder eine andere gewünschte Breite */
            margin: 0 auto; /* Zentriert den Hauptbereich */
        }
        </style>
        """,
        unsafe_allow_html=True
    )   

# Logo hinzufügen
url_logo = 'https://partizipieren.stadt.sg.ch/api/v1/spaces/42/logo'
response = requests.get(url_logo, stream=True)
logo_image = Image.open(response.raw)
new_size = (100, 100)  # Passe die gewünschte Größe an
st.image(logo_image, width=100)


def main():
    st.title("PDF Analyzer - GreenLight")
    st.write("Analysieren Sie die Nachhaltigkeit Ihres Projekts basierend auf den Cercle-Indicateurs-Prinzipien der Schweiz.")

    col1, col2 = st.columns(2)
    pdf_file = st.file_uploader("Neues Projekt zur KI-Analyse hochladen", type=["pdf"])



    if pdf_file is not None:
        pdf_text = extract_text_from_pdf(pdf_file)

        categories = {
            "Natürliche Lebensgrundlagen": {
                "Fokus": "Natur, Biodiversität, Umweltschutz",
                "Beschreibung": "Erhalt und Förderung naturnaher Landschaften und der Biodiversität, Erhalt und Förderung der Artenvielfalt im Siedlungsraum, Erhalt und Förderung natürlicher Ressourcen., Vermeidung schädlicher Einwirkungen auf die Umwelt (Luft, Boden, Wasser, Lärm und Strahlung)",
                "Dimension": "Umwelt"
            },
            "Energie und Klima": {
                "Fokus": "Fokus Energieversorgung, Energieverbrauch, Klimaschutz, Anpassung an den Klimawandel",
                "Beschreibung": "Umstellung der Energieproduktion und -nutzung auf erneuerbare und lokale Energieformen, Ausbau der Energie-Speicherkapazitäten, Energieverbrauch minimieren (Effizienz), CO2-Emissionen vermeiden und senken, Vermeidung/Verminderung von Hitzeinseln durch Begrünung, Durchlüftung, Wasserflächen und Entsiegelung, Förderung der Wasserretention (Schwammstadt)",
                "Dimension": "Umwelt"
            },
            "Produktion und Konsum": {
                "Fokus": "Fokus ENachhaltige Produktion, lokale Wertschöpfung, Kreislaufwirtschaft",
                "Beschreibung": "Fördert nachhaltige Produktionsmuster unter Einhaltung von Sozial- und Umweltkriterien, Entkopplung der Wertschöpfung vom Ressourcenverbrauch durch nachhaltige Produktion, Fördert lokale und regionale Wertschöpfung und Innovation, Sicherstellen der nachhaltigen Versorgung heutiger und zukünftiger Generationen, Fördert den sparsamen und effizienten Umgang mit Ressourcen, Fördert die Kreislaufwirtschaft",
                "Dimension": "Wirtschaft"
            }
        }

        data = []

        for category, values in categories.items():
            focus = values["Fokus"]
            description = values["Beschreibung"]
            dimension = values["Dimension"]

            queries = [
                "Gib eine numerische Bewertung für die Nachhaltigkeitswirkung des Projekts an, basierend auf einer Skala von 2 bis -2. Verwende die folgende Skala: 2 = sehr nachhaltig, 1 = eher nachhaltig, 0 = neutral, -1 = wenig nachhaltig, -2 = nicht nachhaltig. Deine Antwort sollte nur ein numerisches Zeichen sein (maximal 2 Zeichen). Eine Begründung ist nicht erforderlich. Gib bitte nur die numerische Bewertung an (2, 1, 0, -1, -2). Es muss für das ganze nur eine Zahl zurückgegeben werden",
                "Auf Basis deiner vorherigen Antwort: Begründe zusammenfassend in drei Bulletpoints (•) (max. 10 Wörter pro Punkt) die Kategorisierung  (2 = sehr nachhaltig, 1 = eher nachhaltig, 0 = neutral, -1 = wenig nachhaltig, -2 = nicht nachhaltig) des Projekts hinsichtlich des Fokus auf die Nachhaltigkeit. Die Erwähnung der Kategorie und der Zahl darf nicht gemacht werden. Maximal 100 Zeichen und keine nummerischen Werte.",
                "Gib zusammenfassend in drei Bulletpoints (•) (max. 10 Wörter pro Punkt) das Optimierungspotenzial und mögliche Synergien des Projekts an hinsichtlich des Fokus der Nachhaltigkeit. Vermeide Erwähnung der Kategorie. Maximal 100 Zeichen."
            ]

            row_data = [dimension, category, focus, None, None, None]

            for i, query in enumerate(queries):
                full_query = f"{query} Beantworte dies gezielt auf den Fokus '{category} - {focus} - {description} - {dimension}' {pdf_text}"
                answer = ask_chatgpt(full_query)

                if i == 0:
                    # First query goes to "Wirkung"
                    row_data[3] = answer
                elif i == 1:
                    # Second query goes to "Begründung Bewertung"
                    row_data[4] = answer
                elif i == 2:
                    # Third query goes to "Optimierung / Synergien"
                    row_data[5] = answer

            data.append(row_data)

        df = pd.DataFrame(data, columns=["Dimension", "Thema/Indikator", "Fokus", "Wirkung", "Begründung Bewertung", "Optimierung / Synergien"])
        df["Wirkung"] = pd.to_numeric(df["Wirkung"], errors="coerce")

        df_style = df.style.applymap(lambda x: 'background-color: #00CC00' if x == 2 else ('background-color: #66FF66' if x == 1 else ('background-color: #FFFFFF' if x == 0 else ('background-color: #FF9999' if x == -1 else 'background-color: #CC0000'))), subset=["Wirkung"])


        

        # Hier den zweiten Datensatz (other_df) einfügen und die Diagramme aktualisieren
        # Beispiel:
        other_df = pd.DataFrame({
            "Dimension": ["Umwelt", "Umwelt", "Wirtschaft"],
            "Thema/Indikator": ["Durchschnitt", "Durchschnitt", "Durchschnitt"],
            "Fokus": ["Durchschnitt", "Durchschnitt", "Durchschnitt"],
            "Wirkung": [1, 0, -1],
            "Begründung Bewertung": ["Durchschnitt", "Durchschnitt", "Durchschnitt"],
            "Optimierung / Synergien": ["Durchschnitt", "Durchschnitt", "Durchschnitt"]
        })

        # Bereich für das erste Diagramm
        st.header("ChatGPT Analyse")
        st.subheader("Wirkung in den zehn Themen der Nachhaltigen Entwicklung")
        area_chart = px.area(df, x="Thema/Indikator", y="Wirkung", title="Wirkung - Vergleich", labels={"Wirkung": "Wirkung"}, line_shape="linear", color_discrete_sequence=["blue"], height=400, width=800)
        area_chart.add_trace(px.area(other_df, x="Thema/Indikator", y="Wirkung", title="Wirkung - Vergleich", labels={"Wirkung": "Wirkung"}, line_shape="linear", color_discrete_sequence=["red"], height=400, width=800).data[0])

        st.plotly_chart(area_chart)

        # Bereich für das zweite Diagramm
        st.subheader("Gesamtwirkung in den Nachhaltigkeitsdimensionen")
        aggregated_df = df.groupby("Dimension").agg({"Wirkung": "sum"}).reset_index()
        total_chart = px.area(aggregated_df, x="Dimension", y="Wirkung", title="Gesamtwirkung - Vergleich", labels={"Wirkung": "Gesamtnumerische Wirkung"}, line_shape="linear", color_discrete_sequence=["blue"], height=400, width=800)
        total_chart.add_trace(px.area(other_df.groupby("Dimension").agg({"Wirkung": "sum"}).reset_index(), x="Dimension", y="Wirkung", title="Gesamtwirkung - Vergleich", labels={"Wirkung": "Gesamtnumerische Wirkung"}, line_shape="linear", color_discrete_sequence=["red"], height=400, width=800).data[0])
        
        st.plotly_chart(total_chart)

        st.table(df_style)

        st.markdown(get_table_download_link(df), unsafe_allow_html=True)

    else:
        st.info("Noch keine PDF-Datei hochgeladen.")

if __name__ == "__main__":
    main()