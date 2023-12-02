import os
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from PyPDF2 import PdfReader

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        # Try extracting text from PDF using PyPDF2
        with pdf_file:
            pdf_reader = PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


#def ask_chatgpt(prompt, engine="text-davinci-003", temperature=0.6):
   # response = client.chat.completions.create(
   #     model=engine,
    #    messages=[{"role": "system", "content": "You are a helpful assistant."},
     #             {"role": "user", "content": prompt}],
      #  temperature=temperature,

def ask_chatgpt(prompt):

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are assistent who is capable of analyzing how sustainable a project is, based on a PDF Dokument that is given to you"},
            {"role": "user", "content": prompt}
        ]
    )   
    content = completion.choices[0].message.content
    st.text(content)

    #try:
    #    completion = client.chat.completions.create(
     #       model="gpt-3.5-turbo",
      #      messages=[
       #          {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        #         {"role": "user", "content": "Say one sentence"}
     #        ],
      #   
       # )
    #    # Überprüfe, ob die Antwort erwartungsgemäß strukturiert ist
        #if 'choices' in completion and completion['choices'] and 'message' in completion['choices'][0]:
    #        content = completion['choices'][0]['message']['content']
     #       st.write(content)  # Nutze st.write statt print für Streamlit
      #  else:
       #     st.write(f"Error in response structure: {completion}")
    #except Exception as e:
    #    st.write(f"Error in API request: {e}")

def main():
    st.title("PDF Analyzer - Nachhaltigkeitsprojekt")

#    completion = client.chat.completions.create(
#        model="gpt-3.5-turbo",
#        messages=[
#            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#            {"role": "user", "content": "say one word"}
#        ]
#    )   
#
#    content = completion.choices[0].message.content
#    st.text(content)

# Benutzerinteraktion - PDF hochladen
    pdf_file = st.file_uploader("PDF-Datei hochladen", type=["pdf"])

    # Beantworte Fragen basierend auf dem extrahierten Text

        
    pdf_text = extract_text_from_pdf(pdf_file)  # Extrahiere Text aus PDF
    
    st.header("Schwerpunkt Umwelt")

    st.subheader("Natürliche Lebensgrundlage")
    st.markdown("**Fokus: Natur, Biodiversität, Umweltschutz**")
    categorie1 = ["Natürliche Lebensgrundlagen mit Fokus Natur, Biodiversität, Umweltschutz"]
    categorie2 = ["Energie und Klima mit Fokus Energieversorgung, Energieverbrauch, Klimaschutz, Anpassung an den Klimawandel"]
    queries1 = [
        "Kategorisiere das Projekt bezüglich {}. Dazu soll ohne Begründung eine der folgenden Kategorien ausgegeben werden: positiv, eher positiv, neutral, negativ oder sehr negativ. Nur die Kategorie und keine weiteren Wörter ausgeben.".format(category)
        for category in categorie1
    ] + [
        "Begründe in wenigen Stichworten die Antwort auf die Frage: Kategorisiere das Projekt bezüglich {}. Es muss kurz und knapp sein. Keine Erwähnung der Kategorie".format(category)
        for category in categorie1

    ] + [
        "Begründe in wenigen Stichworten Optimierungspotenzial und mögliche Synergien bezüglich {}. Es muss kurz und knapp sein. Keine Erwähnung der Kategorie".format(category)
        for category in categorie1
        
    ]
    queries2 = [
        "Kategorisiere das Projekt bezüglich {}. Dazu soll ohne Begründung eine der folgenden Kategorien ausgegeben werden: positiv, eher positiv, neutral, negativ oder sehr negativ. Nur die Kategorie und keine weiteren Wörter ausgeben.".format(category)
        for category in categorie1
    ] + [
        "Begründe in wenigen Stichworten die Antwort auf die Frage: Kategorisiere das Projekt bezüglich {}. Es muss kurz und knapp sein. Keine Erwähnung der Kategorie".format(category)
        for category in categorie1

    ] + [
        "Begründe in wenigen Stichworten Optimierungspotenzial und mögliche Synergien bezüglich {}. Es muss kurz und knapp sein. Keine Erwähnung der Kategorie".format(category)
        for category in categorie1
        
    ]
    for query in queries1:
        full_query = f"{query} {pdf_text}"  # Füge den extrahierten Text zur Frage hinzu
        answer = ask_chatgpt(full_query)
        st.text(answer)  

    st.subheader("Energie und Klima")
    st.markdown("**Fokus: Energieversorgung, Energieverbrauch, Klimaschutz, Anpassung an den Klimawandel**")
    for query in queries2:
        full_query = f"{query} {pdf_text}"  # Füge den extrahierten Text zur Frage hinzu
        answer = ask_chatgpt(full_query)
        st.text(answer) 
if __name__ == "__main__":
    main()
