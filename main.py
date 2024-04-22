import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, date
import sqlite3
from sqlite3 import Error
import os
import ast

from dd_selection import platz_opt, risiko_opt, ja_nein_opt, vertragsart_opt, ausschreibung_opt, status_opt, renewal_opt, schicksal_opt, sql_columns
from edit_selection import wording_opt, insurer_opt

def get_contract_data(contract_number):
    #Diese Funktion holt die Daten für eine gegebene Vertragsnummer aus der Datenbank.
    query = f"SELECT * FROM manuelle_daten WHERE vertragsnummer = {contract_number}"
    conn = get_mdb_connection('manuelle_daten.db')
    df = pd.read_sql_query(query, conn)
    return df

def display_copy_function():
    st.header("Daten von einem Vertrag in einen anderen kopieren")
    conn = get_mdb_connection('manuelle_daten.db')
    # Vertragsnummern zur Auswahl stellen
    query = "SELECT vertragsnummer FROM manuelle_daten"
    df = pd.read_sql_query(query, conn)
    contract_numbers = df['vertragsnummer'].tolist()

    source_contract = st.selectbox("Quell-Vertragsnummer:", contract_numbers, key="source")
    target_contract = st.selectbox("Ziel-Vertragsnummer:", contract_numbers, key="target")

    if source_contract and target_contract:
        # Spalten zur Auswahl stellen
        source_data = get_contract_data(source_contract)
        source_data = source_data.drop(source_data.columns[0], axis=1)
        columns = source_data.columns.tolist()
        
        # Möglichkeit bieten, alle Optionen auszuwählen
        if st.checkbox("Alle Spalten auswählen", key="select_all"):
            selected_columns = columns
        else:
            selected_columns = st.multiselect("Zu kopierende Spalten:", columns, key="columns")
        
        # Zeige die zu kopierenden und zu überschreibenden Werte
        if selected_columns:
            target_data = get_contract_data(target_contract)

            st.write("Aktuelle Werte der Quell-Vertragsnummer:")
            st.write(source_data[selected_columns])

            st.write("Aktuelle Werte der Ziel-Vertragsnummer:")
            st.write(target_data[selected_columns])

            # Kopieraktion
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            if st.button("Werte kopieren"):
                for col in selected_columns:
                    # Update-Befehl für die Datenbank
                    col_escaped = f"`{col}`"
                    update_query = f"""
                    UPDATE manuelle_daten
                    SET {col_escaped} = (SELECT {col_escaped} FROM manuelle_daten WHERE vertragsnummer = '{source_contract}')
                    WHERE vertragsnummer = '{target_contract}';
                    """
                    conn.execute(update_query)
                conn.commit()
                st.success("Werte erfolgreich kopiert!")


# Definiert Funktionen für jeden Abschnitt oder "Tab" der Anwendung
def display_vertragsdaten():
        st.markdown("<h3 style='color: #002c77'>Aktuelle Vertragsdaten</h3>", unsafe_allow_html=True)
        load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
        st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)
        if 'ivp' not in st.session_state:
            st.session_state.ivp = ja_nein_opt[2]
        if st.session_state.ivp not in ja_nein_opt:
            st.session_state.ivp = ja_nein_opt[2]
        if 'haupt_vertragsdeckungssumme' not in st.session_state:
            st.session_state.haupt_vertragsdeckungssumme = " "
        if 'selbstbehalt_attachment_point' not in st.session_state:
            st.session_state.selbstbehalt_attachment_point = " "      
        if 'hoehe_der_courtage_lokalpolicen(in_%)' not in st.session_state:
            st.session_state['hoehe_der_courtage_lokalpolicen(in_%)'] = ' '
        if 'akt._jahresprogrammbeitrag(inkl._lopos)' not in st.session_state:
            st.session_state['akt._jahresprogrammbeitrag(inkl._lopos)'] = ' '
        if 'vertical_pricing' not in st.session_state:
            st.session_state.vertical_pricing = ja_nein_opt[2]
        if st.session_state.vertical_pricing not in ja_nein_opt:
            st.session_state.vertical_pricing = ja_nein_opt[2]

        def update_vertragsdaten():
            st.session_state.ivp = st.session_state.select_ivp
            st.session_state.haupt_vertragsdeckungssumme = st.session_state.number_input_haupt_vertragsdeckungssumme 
            st.session_state['hoehe_der_courtage_lokalpolicen(in_%)'] = st.session_state.text_input_hoehe_der_courtage_lokalpolicen
            st.session_state['akt._jahresprogrammbeitrag(inkl._lopos)'] = st.session_state.number_input_akt_jahresprogrammbeitrag
            st.session_state.vertical_pricing = st.session_state.select_vertical_pricing
            st.session_state.selbstbehalt_attachment_point = st.session_state.number_input_selbstbehalt_attachment_point
            st.session_state.vertragsart = st.session_state.select_vertragsart
            contract_number = st.session_state['vertrags_id']
            update_fields = {'ivp' : st.session_state.select_ivp,
            '`hoehe_der_courtage_lokalpolicen(in_%)`' : st.session_state.text_input_hoehe_der_courtage_lokalpolicen,
            'haupt_vertragsdeckungssumme' : st.session_state.number_input_haupt_vertragsdeckungssumme,
            '`akt._jahresprogrammbeitrag(inkl._lopos)`' : st.session_state.number_input_akt_jahresprogrammbeitrag,
            'selbstbehalt_attachment_point' :  st.session_state.number_input_selbstbehalt_attachment_point,
            'vertragsart' : st.session_state.select_vertragsart,
            'vertical_pricing' : st.session_state.select_vertical_pricing}
    
            update_data(contract_number, update_fields)
        
        with st.form("vertragsdaten_form"):
            ver_left, ver_right = st.columns(2)
            with ver_left:
                st.selectbox("IVP:", options=ja_nein_opt, index=ja_nein_opt.index
                    (st.session_state['ivp']), key="select_ivp")
                st.number_input("Haupt-Vertragsdeckungssumme:", value=st.session_state.haupt_vertragsdeckungssumme, key="number_input_haupt_vertragsdeckungssumme")
                st.number_input("Selbstbehalt/Attachment Point:", value=st.session_state.selbstbehalt_attachment_point, key="number_input_selbstbehalt_attachment_point")
                st.text_input("Höhe der Courtage Lokalpolicen(in %):", value=st.session_state['hoehe_der_courtage_lokalpolicen(in_%)'], key="text_input_hoehe_der_courtage_lokalpolicen")     
            with ver_right:
                st.number_input("Akt. Jahresprogrammbeitrag (inkl. LoPos):", value=st.session_state['akt._jahresprogrammbeitrag(inkl._lopos)'], key="number_input_akt_jahresprogrammbeitrag")
                st.selectbox("Vertragsart:",options=vertragsart_opt, index=vertragsart_opt.index
                (st.session_state['vertragsart']), key="select_vertragsart")
                st.selectbox("Vertical Pricing:",options=ja_nein_opt, index=ja_nein_opt.index
                (st.session_state['vertical_pricing']), key="select_vertical_pricing")
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            if st.form_submit_button("Änderungen übernehmen", on_click=update_vertragsdaten):
                st.success("Vertragsdaten wurden aktualisiert.")

# Diese Funktion versucht, einen String zu einem Datum zu parsen.
# Gibt True zurück, wenn das Parsen erfolgreich ist, sonst False.
def hat_datumsformat(s, format="%Y-%m-%d"):
    try:
        datetime.strptime(s, format)
        return True
    except ValueError:
        return False

def display_risiko_information():
        st.markdown("<h3 style='color: #002c77'>Risikoinformationen</h3>", unsafe_allow_html=True)
        load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
        st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)
        if 'platzierungsart' not in st.session_state:
            st.session_state.platzierungsart = 'keine Platzierung gewählt'
        if 'risikoart' not in st.session_state:
            st.session_state.risikoart = 'keine Risikoart gewählt'

         # Versuche, das Datum zu konvertieren, falls es im session_state gespeichert ist
        if 'risiko_dialog' in st.session_state:
            # Überprüfe, ob es ein String ist und versuche, ihn zu konvertieren.
            if isinstance(st.session_state.risiko_dialog, str):
                try:
                    st.session_state.risiko_dialog = datetime.strptime(st.session_state.risiko_dialog, "%Y-%m-%d").date()
                except ValueError:
                    st.session_state.risiko_dialog = none_var
            # Überprüfe, ob es ein Datum ist. Wenn nicht, setze none_var.
            elif not isinstance(st.session_state.risiko_dialog, date):
                st.session_state.risiko_dialog = none_var
        else:
            # Wenn 'risiko_dialog' nicht im session_state ist, initialisiere es mit none_var.
            st.session_state.risiko_dialog = none_var

        if 'risikoinfos' in st.session_state:
            # Überprüfe, ob es ein String ist und versuche, ihn zu konvertieren.
            if isinstance(st.session_state.risikoinfos, str):
                try:
                    st.session_state.risikoinfos = datetime.strptime(st.session_state.risikoinfos, "%Y-%m-%d").date()
                except ValueError:
                    st.session_state.risikoinfos = none_var
            # Überprüfe, ob es ein Datum ist. Wenn nicht, setze none_var.
            elif not isinstance(st.session_state.risikoinfos, date):
                st.session_state.risikoinfos = none_var
        else:
            # Wenn 'risiko_dialog' nicht im session_state ist, initialisiere es mit none_var.
            st.session_state.risiko_dialog = none_var

        if 'jahresfahrplan_vom_ce_erhalten' in st.session_state:
            # Überprüfe, ob es ein String ist und versuche, ihn zu konvertieren.
            if isinstance(st.session_state.jahresfahrplan_vom_ce_erhalten, str):
                try:
                    st.session_state.jahresfahrplan_vom_ce_erhalten = datetime.strptime(st.session_state.jahresfahrplan_vom_ce_erhalten, "%Y-%m-%d").date()
                except ValueError:
                    st.session_state.jahresfahrplan_vom_ce_erhalten = none_var
            # Überprüfe, ob es ein Datum ist. Wenn nicht, setze none_var.
            elif not isinstance(st.session_state.jahresfahrplan_vom_ce_erhalten, date):
                st.session_state.jahresfahrplan_vom_ce_erhalten = none_var
        else:
            # Wenn 'risiko_dialog' nicht im session_state ist, initialisiere es mit none_var.
            st.session_state.risiko_dialog = none_var

        if 'wording_version' not in st.session_state:
            st.session_state.wording_version = wording_opt[0]
        if st.session_state.wording_version not in wording_opt:
            st.session_state.wording_version = wording_opt[0]

        def update_risikoinformationen():
            st.session_state.platzierungsart = st.session_state.select_platzierungsart
            st.session_state.risikoart = st.session_state.select_risikoart
            st.session_state.risiko_dialog = st.session_state.date_risiko_dialog
            st.session_state.risikoinfos = st.session_state.date_risiko_infos   
            st.session_state.jahresfahrplan_vom_ce_erhalten = st.session_state.date_jahresfahrplan
            st.session_state.wording_version = st.session_state.select_wording
            contract_number = st.session_state['vertrags_id']
            update_fields = {'platzierungsart' : st.session_state.select_platzierungsart,
            'risikoart' : st.session_state.select_risikoart,
            'risiko_dialog' : st.session_state.date_risiko_dialog,
            'risikoinfos' : st.session_state.date_risiko_infos,   
            'jahresfahrplan_vom_ce_erhalten' : st.session_state.date_jahresfahrplan,
            'wording_version' : st.session_state.select_wording}
            update_data(contract_number, update_fields)
        with st.form("risikoinformationen"):
            ris_left, ris_right = st.columns(2)
            with  ris_left:
                st.selectbox("Platzierungsart:",options=platz_opt, index=platz_opt.index
                (st.session_state['platzierungsart']), key="select_platzierungsart")                  
                st.date_input("Risiko-Dialog:", value=st.session_state.risiko_dialog, key='date_risiko_dialog')
                st.date_input("Jahresfahrplan vom CE erhalten:", value=st.session_state.jahresfahrplan_vom_ce_erhalten, key='date_jahresfahrplan')
            with ris_right:
                st.selectbox("Risikoart:",options=risiko_opt, index=risiko_opt.index
                (st.session_state['risikoart']), key="select_risikoart")                
                st.date_input("Risiko-Informationen:", value=st.session_state.risikoinfos, key='date_risiko_infos')
            if st.session_state['wording_version'] not in wording_opt:
                st.session_state['wording_version'] = 'kein Wording gewählt'
            st.selectbox("Wording Version:",options=wording_opt, index=wording_opt.index
                (st.session_state['wording_version']), key="select_wording")
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            if st.form_submit_button("Änderungen übernehmen", on_click=update_risikoinformationen):
                st.success("Bemerkung wurde aktualisiert.")

def display_ausschreibung():
    st.markdown("<h3 style='color: #002c77'>Ausschreibung</h3>", unsafe_allow_html=True)
    load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
    st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)

    if 'ausschreibung_fuer_kommendes_renewal' not in st.session_state:
        st.session_state.ausschreibung_fuer_kommendes_renewal = ausschreibung_opt[0]
    if st.session_state.ausschreibung_fuer_kommendes_renewal not in ausschreibung_opt:
        st.session_state.ausschreibung_fuer_kommendes_renewal = ausschreibung_opt[0]
    # region ausschreibung_an_versicherer_1 - 15
    if 'ausschreibung_an_versicherer_1' not in st.session_state:
        st.session_state.ausschreibung_an_versicherer_1 = insurer_opt[1]
    if st.session_state.ausschreibung_an_versicherer_1 not in insurer_opt:
        st.session_state.ausschreibung_an_versicherer_1 = insurer_opt[1]
    if 'vr_2' not in st.session_state:
        st.session_state.vr_2 = insurer_opt[1]
    if st.session_state.vr_2 not in insurer_opt:
        st.session_state.vr_2 = insurer_opt[1]
    if 'vr_3' not in st.session_state:
        st.session_state.vr_3 = insurer_opt[1]
    if st.session_state.vr_3 not in insurer_opt:
        st.session_state.vr_3 = insurer_opt[1]
    if 'vr_4' not in st.session_state:
        st.session_state.vr_4 = insurer_opt[1]
    if st.session_state.vr_4 not in insurer_opt:
        st.session_state.vr_4 = insurer_opt[1]
    if 'vr_5' not in st.session_state:
        st.session_state.vr_5 = insurer_opt[1]
    if st.session_state.vr_5 not in insurer_opt:
        st.session_state.vr_5 = insurer_opt[1]
    if 'vr_6' not in st.session_state:
        st.session_state.vr_6 = insurer_opt[1]
    if st.session_state.vr_6 not in insurer_opt:
        st.session_state.vr_6 = insurer_opt[1]
    if 'vr_7' not in st.session_state:
        st.session_state.vr_7 = insurer_opt[1]
    if st.session_state.vr_7 not in insurer_opt:
        st.session_state.vr_7 = insurer_opt[1]
    if 'vr_8' not in st.session_state:
        st.session_state.vr_8 = insurer_opt[1]
    if st.session_state.vr_8 not in insurer_opt:
        st.session_state.vr_8 = insurer_opt[1]
    if 'vr_9' not in st.session_state:
        st.session_state.vr_9 = insurer_opt[1]
    if st.session_state.vr_9 not in insurer_opt:
        st.session_state.vr_9 = insurer_opt[1]
    if 'vr_10' not in st.session_state:
        st.session_state.vr_10 = insurer_opt[1]
    if st.session_state.vr_10 not in insurer_opt:
        st.session_state.vr_10 = insurer_opt[1]
    if 'vr_11' not in st.session_state:
        st.session_state.vr_11 = insurer_opt[1]
    if st.session_state.vr_11 not in insurer_opt:
        st.session_state.vr_11 = insurer_opt[1]
    if 'vr_12' not in st.session_state:
        st.session_state.vr_12 = insurer_opt[1]
    if st.session_state.vr_12 not in insurer_opt:
        st.session_state.vr_12 = insurer_opt[1] 
    if 'vr_13' not in st.session_state:
        st.session_state.vr_13 = insurer_opt[1]
    if st.session_state.vr_13 not in insurer_opt:
        st.session_state.vr_13 = insurer_opt[1]   
    if 'vr_14' not in st.session_state:
        st.session_state.vr_14 = insurer_opt[1]
    if st.session_state.vr_14 not in insurer_opt:
        st.session_state.vr_14 = insurer_opt[1]
    if 'vr_15' not in st.session_state:
        st.session_statevrr_15 = insurer_opt[1]
    if st.session_state.vr_15 not in insurer_opt:
        st.session_state.vr_15 = insurer_opt[1]
    #endregion
    # region angebotene_praemie_1 - 15
    if 'angebotene_praemie_1' not in st.session_state:
            st.session_state.angebotene_praemie_1 = " " 
    if 'angebotene_praemie_2' not in st.session_state:
            st.session_state.angebotene_praemie_2 = " "
    if 'angebotene_praemie_3' not in st.session_state:
            st.session_state.angebotene_praemie_3 = " "
    if 'angebotene_praemie_4' not in st.session_state:
            st.session_state.angebotene_praemie_4 = " "
    if 'angebotene_praemie_5' not in st.session_state:
            st.session_state.angebotene_praemie_5 = " "
    if 'angebotene_praemie_6' not in st.session_state:
            st.session_state.angebotene_praemie_6 = " "
    if 'angebotene_praemie_7' not in st.session_state:
            st.session_state.angebotene_praemie_7 = " "
    if 'angebotene_praemie_8' not in st.session_state:
            st.session_state.angebotene_praemie_8 = " "
    if 'angebotene_praemie_9' not in st.session_state:
            st.session_state.angebotene_praemie_9 = " "
    if 'angebotene_praemie_10' not in st.session_state:
            st.session_state.angebotene_praemie_10 = " "
    if 'angebotene_praemie_11' not in st.session_state:
            st.session_state.angebotene_praemie_11 = " "
    if 'angebotene_praemie_12' not in st.session_state:
            st.session_state.angebotene_praemie_12 = " "
    if 'angebotene_praemie_13' not in st.session_state:
            st.session_state.angebotene_praemie_13 = " "
    if 'angebotene_praemie_14' not in st.session_state:
            st.session_state.angebotene_praemie_14 = " "
    if 'angebotene_praemie_15' not in st.session_state:
            st.session_state.angebotene_praemie_15 = " "
    # endregion
    # region status_des_angebots_1 - 15
    if 'status_des_angebots_1' not in st.session_state:
        st.session_state.status_des_angebots_1 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_1 not in ausschreibung_opt:
        st.session_state.status_des_angebots_1 = ausschreibung_opt[0]
    if 'status_des_angebots_2' not in st.session_state:
        st.session_state.status_des_angebots_2 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_2 not in ausschreibung_opt:
        st.session_state.status_des_angebots_2 = ausschreibung_opt[0]
    if 'status_des_angebots_3' not in st.session_state:
        st.session_state.status_des_angebots_3 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_3 not in ausschreibung_opt:
        st.session_state.status_des_angebots_3 = ausschreibung_opt[0]
    if 'status_des_angebots_4' not in st.session_state:
        st.session_state.status_des_angebots_4 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_4 not in ausschreibung_opt:
        st.session_state.status_des_angebots_4 = ausschreibung_opt[0]
    if 'status_des_angebots_5' not in st.session_state:
        st.session_state.status_des_angebots_5 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_5 not in ausschreibung_opt:
        st.session_state.status_des_angebots_5 = ausschreibung_opt[0]
    if 'status_des_angebots_6' not in st.session_state:
        st.session_state.status_des_angebots_6 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_6 not in ausschreibung_opt:
        st.session_state.status_des_angebots_6 = ausschreibung_opt[0]
    if 'status_des_angebots_7' not in st.session_state:
        st.session_state.status_des_angebots_7 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_7 not in ausschreibung_opt:
        st.session_state.status_des_angebots_7 = ausschreibung_opt[0]
    if 'status_des_angebots_8' not in st.session_state:
        st.session_state.status_des_angebots_8 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_8 not in ausschreibung_opt:
        st.session_state.status_des_angebots_8 = ausschreibung_opt[0]
    if 'status_des_angebots_9' not in st.session_state:
        st.session_state.status_des_angebots_9 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_9 not in ausschreibung_opt:
        st.session_state.status_des_angebots_9 = ausschreibung_opt[0]
    if 'status_des_angebots_10' not in st.session_state:
        st.session_state.status_des_angebots_10 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_10 not in ausschreibung_opt:
        st.session_state.status_des_angebots_10 = ausschreibung_opt[0]
    if 'status_des_angebots_11' not in st.session_state:
        st.session_state.status_des_angebots_11 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_11 not in ausschreibung_opt:
        st.session_state.status_des_angebots_11 = ausschreibung_opt[0]
    if 'status_des_angebots_12' not in st.session_state:
        st.session_state.status_des_angebots_12 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_12 not in ausschreibung_opt:
        st.session_state.status_des_angebots_12 = ausschreibung_opt[0]
    if 'status_des_angebots_13' not in st.session_state:
        st.session_state.status_des_angebots_13 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_13 not in ausschreibung_opt:
        st.session_state.status_des_angebots_13 = ausschreibung_opt[0]
    if 'status_des_angebots_14' not in st.session_state:
        st.session_state.status_des_angebots_14 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_14 not in ausschreibung_opt:
        st.session_state.status_des_angebots_14 = ausschreibung_opt[0]
    if 'status_des_angebots_15' not in st.session_state:
        st.session_state.status_des_angebots_15 = ausschreibung_opt[0]
    if st.session_state.status_des_angebots_15 not in ausschreibung_opt:
        st.session_state.status_des_angebots_15 = ausschreibung_opt[0]
    # endregion

    if 'kuefri' in st.session_state:
        # Wenn 'kuefri' ein String ist, versuche, ihn zu einem datetime.date zu konvertieren.
        if isinstance(st.session_state.kuefri, str):
            try:
                st.session_state.kuefri = datetime.strptime(st.session_state.kuefri, "%Y-%m-%d").date()
            except ValueError:
                # Wenn die Konvertierung fehlschlägt, setze 'kuefri' auf None.
                st.session_state.kuefri = none_var
        # Wenn 'kuefri' weder ein Datum noch ein korrekt formatierter String ist, setze es auf None.
        elif not isinstance(st.session_state.kuefri, date):
            st.session_state.kuefri = none_var
    else:
        # Wenn 'kuefri' nicht im session_state existiert, initialisiere es mit None.
        st.session_state.kuefri = none_var

    if 'status' not in st.session_state:
        st.session_state.status = status_opt[5]
    if st.session_state.status not in status_opt:
        st.session_state.status = status_opt[5]

    # region def update_ausschreibung
    def update_ausschreibung():
        st.session_state.ausschreibung_fuer_kommendes_renewal = st.session_state.select_ausschreibung_fuer_kommendes_renewal
        st.session_state.ausschreibung_an_versicherer_1 = st.session_state.select_ausschreibung_an_versicherer_1
        st.session_state.vr_2 = st.session_state.select_vr_2
        st.session_state.vr_3 = st.session_state.select_vr_3
        st.session_state.vr_4 = st.session_state.select_vr_4
        st.session_state.vr_5 = st.session_state.select_vr_5
        st.session_state.vr_6 = st.session_state.select_vr_6
        st.session_state.vr_7 = st.session_state.select_vr_7
        st.session_state.vr_8 = st.session_state.select_vr_8
        st.session_state.vr_9 = st.session_state.select_vr_9
        st.session_state.vr_10 = st.session_state.select_vr_10
        st.session_state.vr_11 = st.session_state.select_vr_11
        st.session_state.vr_12 = st.session_state.select_vr_12
        st.session_state.vr_13 = st.session_state.select_vr_13
        st.session_state.vr_14 = st.session_state.select_vr_14
        st.session_state.vr_15 = st.session_state.select_vr_15
        st.session_state.angebotene_praemie_1 = st.session_state.number_input_angebotene_praemie_1
        st.session_state.angebotene_praemie_2 = st.session_state.number_input_angebotene_praemie_2
        st.session_state.angebotene_praemie_3 = st.session_state.number_input_angebotene_praemie_3
        st.session_state.angebotene_praemie_4 = st.session_state.number_input_angebotene_praemie_4
        st.session_state.angebotene_praemie_5 = st.session_state.number_input_angebotene_praemie_5
        st.session_state.angebotene_praemie_6 = st.session_state.number_input_angebotene_praemie_6
        st.session_state.angebotene_praemie_7 = st.session_state.number_input_angebotene_praemie_7
        st.session_state.angebotene_praemie_8 = st.session_state.number_input_angebotene_praemie_8
        st.session_state.angebotene_praemie_9 = st.session_state.number_input_angebotene_praemie_9
        st.session_state.angebotene_praemie_10 = st.session_state.number_input_angebotene_praemie_10
        st.session_state.angebotene_praemie_11 = st.session_state.number_input_angebotene_praemie_11
        st.session_state.angebotene_praemie_12 = st.session_state.number_input_angebotene_praemie_12
        st.session_state.angebotene_praemie_13 = st.session_state.number_input_angebotene_praemie_13
        st.session_state.angebotene_praemie_14 = st.session_state.number_input_angebotene_praemie_14
        st.session_state.angebotene_praemier_15 = st.session_state.number_input_angebotene_praemie_15
        st.session_state.status_des_angebots_1 = st.session_state.select_status_des_angebots_1
        st.session_state.status_des_angebots_2 = st.session_state.select_status_des_angebots_2
        st.session_state.status_des_angebots_3 = st.session_state.select_status_des_angebots_3
        st.session_state.status_des_angebots_4 = st.session_state.select_status_des_angebots_4
        st.session_state.status_des_angebots_5 = st.session_state.select_status_des_angebots_5
        st.session_state.status_des_angebots_6 = st.session_state.select_status_des_angebots_6
        st.session_state.status_des_angebots_7 = st.session_state.select_status_des_angebots_7
        st.session_state.status_des_angebots_8 = st.session_state.select_status_des_angebots_8
        st.session_state.status_des_angebots_9 = st.session_state.select_status_des_angebots_9
        st.session_state.status_des_angebots_10 = st.session_state.select_status_des_angebots_10
        st.session_state.status_des_angebots_11 = st.session_state.select_status_des_angebots_11
        st.session_state.status_des_angebots_12 = st.session_state.select_status_des_angebots_12
        st.session_state.status_des_angebots_13 = st.session_state.select_status_des_angebots_13
        st.session_state.status_des_angebots_14 = st.session_state.select_status_des_angebots_14
        st.session_state.status_des_angebots_15 = st.session_state.select_status_des_angebots_15
        st.session_state.kuefri = st.session_state.date_kuefri
        st.session_state.status = st.session_state.select_status

        contract_number = st.session_state['vertrags_id']
        update_fields ={'ausschreibung_fuer_kommendes_renewal' : st.session_state.select_ausschreibung_fuer_kommendes_renewal,
        'ausschreibung_an_versicherer_1' : st.session_state.select_ausschreibung_an_versicherer_1,  
        'vr_2' : st.session_state.select_vr_2, 
        'vr_3' : st.session_state.select_vr_3, 
        'vr_4' : st.session_state.select_vr_4, 
        'vr_5' : st.session_state.select_vr_5, 
        'vr_6' : st.session_state.select_vr_6, 
        'vr_7' : st.session_state.select_vr_7, 
        'vr_8' : st.session_state.select_vr_8, 
        'vr_9' : st.session_state.select_vr_9, 
        'vr_10' : st.session_state.select_vr_10, 
        'vr_11' : st.session_state.select_vr_11, 
        'vr_12' : st.session_state.select_vr_12, 
        'vr_13' : st.session_state.select_vr_13, 
        'vr_14' : st.session_state.select_vr_14, 
        'vr_15' : st.session_state.select_vr_15,
        'angebotene_praemie_1' : st.session_state.number_input_angebotene_praemie_1,
        'angebotene_praemie_2' : st.session_state.number_input_angebotene_praemie_2,
        'angebotene_praemie_3' : st.session_state.number_input_angebotene_praemie_3,
        'angebotene_praemie_4' : st.session_state.number_input_angebotene_praemie_4,
        'angebotene_praemie_5' : st.session_state.number_input_angebotene_praemie_5,
        'angebotene_praemie_6' : st.session_state.number_input_angebotene_praemie_6,
        'angebotene_praemie_7' : st.session_state.number_input_angebotene_praemie_7,
        'angebotene_praemie_8' : st.session_state.number_input_angebotene_praemie_8,
        'angebotene_praemie_9' : st.session_state.number_input_angebotene_praemie_9,
        'angebotene_praemie_10' : st.session_state.number_input_angebotene_praemie_10,
        'angebotene_praemie_11' : st.session_state.number_input_angebotene_praemie_11,
        'angebotene_praemie_12' : st.session_state.number_input_angebotene_praemie_12,
        'angebotene_praemie_13' : st.session_state.number_input_angebotene_praemie_13,
        'angebotene_praemie_14' : st.session_state.number_input_angebotene_praemie_14,
        'angebotene_praemie_15' : st.session_state.number_input_angebotene_praemie_15,
        'status_des_angebots_1' : st.session_state.select_status_des_angebots_1,
        'status_des_angebots_2' : st.session_state.select_status_des_angebots_2,
        'status_des_angebots_3' : st.session_state.select_status_des_angebots_3,
        'status_des_angebots_4' : st.session_state.select_status_des_angebots_4,
        'status_des_angebots_5' : st.session_state.select_status_des_angebots_5,
        'status_des_angebots_6' : st.session_state.select_status_des_angebots_6,
        'status_des_angebots_7' : st.session_state.select_status_des_angebots_7,
        'status_des_angebots_8' : st.session_state.select_status_des_angebots_8,
        'status_des_angebots_9' : st.session_state.select_status_des_angebots_9,
        'status_des_angebots_10' : st.session_state.select_status_des_angebots_10,
        'status_des_angebots_11' : st.session_state.select_status_des_angebots_11,
        'status_des_angebots_12' : st.session_state.select_status_des_angebots_12,
        'status_des_angebots_13' : st.session_state.select_status_des_angebots_13,
        'status_des_angebots_14' : st.session_state.select_status_des_angebots_14,
        'status_des_angebots_15' : st.session_state.select_status_des_angebots_15,
        'kuefri' : st.session_state.date_kuefri, 
        'status' : st.session_state.select_status
                        } 
        update_data(contract_number, update_fields)
    # endregion

    with st.form("ausschreibung_form"):
        
        aus1_left,aus1_mid, aus1_right = st.columns(3)
        with aus1_left:
            st.selectbox("Ausschreibung für kommendes Renewal:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['ausschreibung_fuer_kommendes_renewal']), key="select_ausschreibung_fuer_kommendes_renewal")
        with aus1_mid:
            st.date_input("Kündigungsfrist:", value=st.session_state.kuefri, key='date_kuefri')
        with aus1_right:
            st.selectbox("Status:", options=status_opt, index=status_opt.index
                        (st.session_state['status']), key="select_status")  
        st.markdown("""---""")

        aus2_left,aus2_mid, aus2_right = st.columns(3)
        with aus2_left:   
            st.selectbox("Ausschreibung an Versicherer 1:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['ausschreibung_an_versicherer_1']), key="select_ausschreibung_an_versicherer_1")
            st.selectbox("Ausschreibung an Versicherer 2:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_2']), key="select_vr_2")
            st.selectbox("Ausschreibung an Versicherer 3:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_3']), key="select_vr_3")
            st.selectbox("Ausschreibung an Versicherer 4:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_4']), key="select_vr_4")
            st.selectbox("Ausschreibung an Versicherer 5:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_5']), key="select_vr_5")
            st.selectbox("Ausschreibung an Versicherer 6:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_6']), key="select_vr_6")
            st.selectbox("Ausschreibung an Versicherer 7:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_7']), key="select_vr_7")
            st.selectbox("Ausschreibung an Versicherer 8:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_8']), key="select_vr_8")
            st.selectbox("Ausschreibung an Versicherer 9:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_9']), key="select_vr_9")
            st.selectbox("Ausschreibung an Versicherer 10:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_10']), key="select_vr_10")
            st.selectbox("Ausschreibung an Versicherer 11:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_11']), key="select_vr_11")
            st.selectbox("Ausschreibung an Versicherer 12:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_12']), key="select_vr_12")
            st.selectbox("Ausschreibung an Versicherer 13:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_13']), key="select_vr_13")
            st.selectbox("Ausschreibung an Versicherer 14:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_14']), key="select_vr_14")
            st.selectbox("Ausschreibung an Versicherer 15:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['vr_15']), key="select_vr_15")

        with aus2_mid:
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_1, key="number_input_angebotene_praemie_1")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_2, key="number_input_angebotene_praemie_2")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_3, key="number_input_angebotene_praemie_3")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_4, key="number_input_angebotene_praemie_4")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_5, key="number_input_angebotene_praemie_5")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_6, key="number_input_angebotene_praemie_6")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_7, key="number_input_angebotene_praemie_7")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_8, key="number_input_angebotene_praemie_8")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_9, key="number_input_angebotene_praemie_9")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_10, key="number_input_angebotene_praemie_10")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_11, key="number_input_angebotene_praemie_11")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_12, key="number_input_angebotene_praemie_12")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_13, key="number_input_angebotene_praemie_13")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_14, key="number_input_angebotene_praemie_14")
            st.number_input("Angebotene Prämie:", value=st.session_state.angebotene_praemie_15, key="number_input_angebotene_praemie_15")

        with aus2_right:
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_1']), key="select_status_des_angebots_1")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_2']), key="select_status_des_angebots_2")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_3']), key="select_status_des_angebots_3")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_4']), key="select_status_des_angebots_4")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_5']), key="select_status_des_angebots_5")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_6']), key="select_status_des_angebots_6")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_7']), key="select_status_des_angebots_7")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_8']), key="select_status_des_angebots_8")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_9']), key="select_status_des_angebots_9")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_10']), key="select_status_des_angebots_10")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_11']), key="select_status_des_angebots_11")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_12']), key="select_status_des_angebots_12")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_13']), key="select_status_des_angebots_13")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_14']), key="select_status_des_angebots_14")
            st.selectbox("Status des Angebots:", options=ausschreibung_opt, index=ausschreibung_opt.index
                        (st.session_state['status_des_angebots_15']), key="select_status_des_angebots_15")           
        
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.form_submit_button("Änderungen übernehmen", on_click=update_ausschreibung):
            st.success("Vertragsdaten wurden aktualisiert.")

def display_renewal_ergebnis():
    st.markdown("<h3 style='color: #002c77'>Renewalergebnis</h3>", unsafe_allow_html=True)
    load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
    st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)

    if 'renewalergebnis' not in st.session_state:
        st.session_state.renewalergebnis = renewal_opt[3]
    if st.session_state.renewalergebnis not in renewal_opt:
        st.session_state.renewalergebnis = renewal_opt[3]
    if 'neuer_fuehrender_versicherer' not in st.session_state:
        st.session_state.neuer_fuehrender_versicherer = insurer_opt[0]
    if st.session_state.neuer_fuehrender_versicherer not in insurer_opt:
        st.session_state.neuer_fuehrender_versicherer = insurer_opt[0]    
    if 'neue_beteiligte_versicherer(1)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(1)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(1)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(1)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(2)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(2)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(2)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(2)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(3)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(3)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(3)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(3)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(4)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(4)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(4)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(4)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(5)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(5)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(5)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(5)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(6)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(6)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(6)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(6)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(7)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(7)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(7)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(7)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(8)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(8)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(8)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(8)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(9)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(9)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(9)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(9)'] = insurer_opt[0]
    if 'neue_beteiligte_versicherer(10)' not in st.session_state:
        st.session_state['neue_beteiligte_versicherer(10)'] = insurer_opt[0]
    if st.session_state['neue_beteiligte_versicherer(10)'] not in insurer_opt:
        st.session_state['neue_beteiligte_versicherer(10)'] = insurer_opt[0]
    if 'fuehrungsquote(in_%)' not in st.session_state:
        st.session_state['fuehrungsquote(in_%)'] = ' '
    if 'beteiligungsquote(in_%)_1' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_1'] = ' '
    if 'beteiligungsquote(in_%)_2' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_2'] = ' '
    if 'beteiligungsquote(in_%)_3' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_3'] = ' '
    if 'beteiligungsquote(in_%)_4' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_4'] = ' '
    if 'beteiligungsquote(in_%)_5' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_5'] = ' '
    if 'beteiligungsquote(in_%)_6' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_6'] = ' '
    if 'beteiligungsquote(in_%)_7' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_7'] = ' '
    if 'beteiligungsquote(in_%)_8' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_8'] = ' '
    if 'beteiligungsquote(in_%)_9' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_9'] = ' '
    if 'beteiligungsquote(in_%)_10' not in st.session_state:
        st.session_state['beteiligungsquote(in_%)_10'] = ' '
    if 'neuer_jahresprogrammbeitrag(100%_exkl.lopos)' not in st.session_state:
            st.session_state['neuer_jahresprogrammbeitrag(100%_exkl.lopos)'] = ' '
    if 'neuer_jahresprogrammbeitrag(100%_inkl.lopos)' not in st.session_state:
            st.session_state['neuer_jahresprogrammbeitrag(100%_inkl.lopos)'] = ' '

    def update_renewal_ergebnis():
        st.session_state.renewalergebnis = st.session_state.select_renewalergebnis
       
        contract_number = st.session_state['vertrags_id']
        update_fields ={'renewalergebnis' : st.session_state.select_renewalergebnis,
        'neuer_fuehrender_versicherer' : st.session_state.select_neuer_fuehrender_versicherer,
        '`neue_beteiligte_versicherer(1)`' : st.session_state.select_neue_beteiligte_versicherer_1,
        '`neue_beteiligte_versicherer(2)`' : st.session_state.select_neue_beteiligte_versicherer_2,
        '`neue_beteiligte_versicherer(3)`' : st.session_state.select_neue_beteiligte_versicherer_3,
        '`neue_beteiligte_versicherer(4)`' : st.session_state.select_neue_beteiligte_versicherer_4,
        '`neue_beteiligte_versicherer(5)`' : st.session_state.select_neue_beteiligte_versicherer_5,
        '`neue_beteiligte_versicherer(6)`' : st.session_state.select_neue_beteiligte_versicherer_6,
        '`neue_beteiligte_versicherer(7)`' : st.session_state.select_neue_beteiligte_versicherer_7,
        '`neue_beteiligte_versicherer(8)`' : st.session_state.select_neue_beteiligte_versicherer_8,
        '`neue_beteiligte_versicherer(9)`' : st.session_state.select_neue_beteiligte_versicherer_9,
        '`neue_beteiligte_versicherer(10)`' : st.session_state.select_neue_beteiligte_versicherer_10,
        '`fuehrungsquote(in_%)`' : st.session_state.text_input_fuehrungsquote,
        '`beteiligungsquote(in_%)_1`' : st.session_state.text_input_beteiligungsquote_1,
        '`beteiligungsquote(in_%)_2`' : st.session_state.text_input_beteiligungsquote_2,
        '`beteiligungsquote(in_%)_3`' : st.session_state.text_input_beteiligungsquote_3,
        '`beteiligungsquote(in_%)_4`' : st.session_state.text_input_beteiligungsquote_4,
        '`beteiligungsquote(in_%)_5`' : st.session_state.text_input_beteiligungsquote_5,
        '`beteiligungsquote(in_%)_6`' : st.session_state.text_input_beteiligungsquote_6,
        '`beteiligungsquote(in_%)_7`' : st.session_state.text_input_beteiligungsquote_7,
        '`beteiligungsquote(in_%)_8`' : st.session_state.text_input_beteiligungsquote_8,
        '`beteiligungsquote(in_%)_9`' : st.session_state.text_input_beteiligungsquote_9,
        '`beteiligungsquote(in_%)_10`' : st.session_state.text_input_beteiligungsquote_10,
        '`neuer_jahresprogrammbeitrag(100%_exkl.lopos)`' : st.session_state.number_input_haupt_jahresprogrammbeitrag_exkl_lopos,
        '`neuer_jahresprogrammbeitrag(100%_inkl.lopos)`' : st.session_state.number_input_haupt_jahresprogrammbeitrag_inkl_lopos,
                        } 
        update_data(contract_number, update_fields)

    with st.form("renewal_ergebnis_form"):
        ren1_left, ren1_mid, ren1_right = st.columns(3)
        with ren1_left:   
            st.selectbox("Renewalergebnis:", options=renewal_opt, index=renewal_opt.index
                        (st.session_state['renewalergebnis']), key="select_renewalergebnis")
        with ren1_mid:                  
            st.number_input("Neuer Jahresprogrammbeitrag(100% exkl.Lopos):", value=st.session_state['neuer_jahresprogrammbeitrag(100%_exkl.lopos)'], key="number_input_haupt_jahresprogrammbeitrag_exkl_lopos")
        with ren1_right:
            st.number_input("Neuer Jahresprogrammbeitrag(100% inkl.Lopos):", value=st.session_state['neuer_jahresprogrammbeitrag(100%_inkl.lopos)'], key="number_input_haupt_jahresprogrammbeitrag_inkl_lopos")
        st.markdown("""---""")
        ren2_left, ren2_right = st.columns(2)
        with ren2_left:  
            st.selectbox("Neuer führender Versicherer:", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neuer_fuehrender_versicherer']), key="select_neuer_fuehrender_versicherer")
            st.selectbox("Neuer beteiligter Versicherer(1):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(1)']), key="select_neue_beteiligte_versicherer_1")
            st.selectbox("Neuer beteiligter Versicherer(2):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(2)']), key="select_neue_beteiligte_versicherer_2")
            st.selectbox("Neuer beteiligter Versicherer(3):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(3)']), key="select_neue_beteiligte_versicherer_3")
            st.selectbox("Neuer beteiligter Versicherer(4):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(4)']), key="select_neue_beteiligte_versicherer_4")
            st.selectbox("Neuer beteiligter Versicherer(5):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(5)']), key="select_neue_beteiligte_versicherer_5")
            st.selectbox("Neuer beteiligter Versicherer(6):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(6)']), key="select_neue_beteiligte_versicherer_6")
            st.selectbox("Neuer beteiligter Versicherer(7):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(7)']), key="select_neue_beteiligte_versicherer_7")
            st.selectbox("Neuer beteiligter Versicherer(8):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(8)']), key="select_neue_beteiligte_versicherer_8")
            st.selectbox("Neuer beteiligter Versicherer(9):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(9)']), key="select_neue_beteiligte_versicherer_9")
            st.selectbox("Neuer beteiligter Versicherer(10):", options=insurer_opt, index=insurer_opt.index
                        (st.session_state['neue_beteiligte_versicherer(10)']), key="select_neue_beteiligte_versicherer_10")
        with ren2_right:
            st.text_input("Führungsquote (in %):", value=st.session_state['fuehrungsquote(in_%)'], key="text_input_fuehrungsquote")
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_1'], key="text_input_beteiligungsquote_1") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_2'], key="text_input_beteiligungsquote_2") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_3'], key="text_input_beteiligungsquote_3") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_4'], key="text_input_beteiligungsquote_4") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_5'], key="text_input_beteiligungsquote_5")
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_6'], key="text_input_beteiligungsquote_6") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_7'], key="text_input_beteiligungsquote_7") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_8'], key="text_input_beteiligungsquote_8") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_9'], key="text_input_beteiligungsquote_9") 
            st.text_input("Beteiligungsquote (in %):", value=st.session_state['beteiligungsquote(in_%)_10'], key="text_input_beteiligungsquote_10")  
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.form_submit_button("Änderungen übernehmen", on_click=update_renewal_ergebnis):
            st.success("Vertragsdaten wurden aktualisiert.")

def display_abarbeitung_renewal():
    st.markdown("<h3 style='color: #002c77'>Abarbeitung des Renewals</h3>", unsafe_allow_html=True)
    load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
    st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)
    if 'pdcs' not in st.session_state:
        st.session_state.pdcs = ja_nein_opt[2]
    if st.session_state.pdcs not in ja_nein_opt:
        st.session_state.pdcs = ja_nein_opt[2]
    if 'allokation+rechnung' not in st.session_state:
        st.session_state["allokation+rechnung"] = ja_nein_opt[2]
    if st.session_state["allokation+rechnung"] not in ja_nein_opt:
        st.session_state["allokation+rechnung"] = ja_nein_opt[2]
    if 'mgc' not in st.session_state:
        st.session_state.mgc = ja_nein_opt[2]
    if st.session_state.mgc not in ja_nein_opt:
        st.session_state.mgc = ja_nein_opt[2]
    if 'pol' not in st.session_state:
        st.session_state.pol = ja_nein_opt[2]
    if st.session_state.pol not in ja_nein_opt:
        st.session_state.pol = ja_nein_opt[2]
    if 'schicksal_des_kunden' not in st.session_state:
        st.session_state.schicksal_des_kunden = schicksal_opt[3]
    if st.session_state.schicksal_des_kunden not in schicksal_opt:
        st.session_state.schicksal_des_kunden = schicksal_opt[3]

    def update_abarbeitung_renewal():
        st.session_state.pdcs = st.session_state.select_pdcs
        st.session_state["allokation+rechnung"] = st.session_state["select_allokation+rechnung"]
        st.session_state.mgc = st.session_state.select_mgc
        st.session_state.pol = st.session_state.select_pol
        st.session_state.schicksal_des_kunden = st.session_state.select_schicksal_des_kunden
        contract_number = st.session_state['vertrags_id']
        update_fields ={'pdcs' : st.session_state.select_pdcs,  
                        '`allokation+rechnung`': st.session_state["select_allokation+rechnung"],
                        'mgc' : st.session_state.select_mgc,
                        'pol' : st.session_state.select_pol,
                        'schicksal_des_kunden' : st.session_state.select_schicksal_des_kunden} 
        update_data(contract_number, update_fields)
        
    with st.form("abarbeitung_form"):
        aba_left, aba_right = st.columns(2)
        with aba_left:   
            st.selectbox("PDCS:", options=ja_nein_opt, index=ja_nein_opt.index
                        (st.session_state['pdcs']), key="select_pdcs")
            st.selectbox("Allokation + Rechnung:", options=ja_nein_opt, index=ja_nein_opt.index
                        (st.session_state['pdcs']), key="select_allokation+rechnung")                 
        with aba_right:
            st.selectbox("MGC:", options=ja_nein_opt, index=ja_nein_opt.index
                        (st.session_state['mgc']), key="select_mgc")
            st.selectbox("POL:", options=ja_nein_opt, index=ja_nein_opt.index
                        (st.session_state['pol']), key="select_pol") 
        st. selectbox("Schicksal des Kunden:", options=schicksal_opt, index=schicksal_opt.index
                        (st.session_state['schicksal_des_kunden']), key="select_schicksal_des_kunden") 
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.form_submit_button("Änderungen übernehmen", on_click=update_abarbeitung_renewal):
            st.success("Vertragsdaten wurden aktualisiert.")

def display_bemerkung():
    st.markdown("<h3 style='color: #002c77'>Bemerkung</h3>", unsafe_allow_html=True)
    load_contract_to_session_state(st.session_state['vertrags_id']) # Vertragsdetails in den Sitzungsstatus laden
    st.markdown(f"<h4 style='color: #002c77;'>Aktueller Vertrag: {str(st.session_state['vertrags_id'])}</h4>", unsafe_allow_html=True)
    if 'bemerkung' not in st.session_state:
        st.session_state.bemerkung = ''
        
    def update_bemerkung():
        st.session_state.bemerkung = st.session_state.text_input_bemerkung
        contract_number = st.session_state['vertrags_id']
        update_fields = {'bemerkung' : st.session_state.text_input_bemerkung}
        update_data(contract_number, update_fields)
        
    with st.form("bemerkung_form"):
        st.text_input("Bemerkungen:", value=st.session_state.bemerkung, key="text_input_bemerkung")
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.form_submit_button("Änderungen übernehmen", on_click=update_bemerkung):
            st.success("Bemerkung wurde aktualisiert.")

# Funktion, um die Verbindung zur manuelle Daten Datenbank herzustellen
def get_mdb_connection(mdb_path):
    conn = sqlite3.connect(mdb_path)
    conn.row_factory = sqlite3.Row  # Ermöglicht den Zugriff auf die Daten durch Spaltennamen
    return conn

# Funktion, um die Verbindung zur technische Daten Datenbank herzustellen
def load_sqlite_data(table_name, db_path):
    try:  
        conn = sqlite3.connect(db_path)
        # Laden Sie Daten aus der angegebenen Tabelle in einen DataFrame
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except (sqlite3.OperationalError, FileNotFoundError) as e:
        # Der Einfachheit halber werden sowohl Datei nicht gefunden als auch Betriebsfehler (z. B. Tabelle existiert nicht) abgefangen.
        print(f"An error occurred: {e}.")
       
# Update-Funktion
def update_data(contract_number, update_fields):
  
    # Aktualisiert Daten in der Datenbank basierend auf der vertragsnummer.
    # Args:
    #      - contract_number (str): Die Vertragsnummer, die die zu aktualisierende Zeile identifiziert.
    #      - update_fields (dict): Ein Dictionary, das die zu aktualisierenden Spalten und ihre neuen Werte enthält.
    conn = get_mdb_connection(mdb_path)
    if conn is not None:
        try:
            cursor = conn.cursor()
            updates = ', '.join([f"{key} = ?" for key in update_fields.keys()])
            values = list(update_fields.values()) + [contract_number]
            sql = f"UPDATE manuelle_daten SET {updates} WHERE vertragsnummer = ?"
            cursor.execute(sql, values)
            conn.commit()
            if cursor.rowcount == 0:
                st.error("No contract number found or no update needed.")
            
        except Error as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    else:
        st.error("Could not establish database connection.")

def load_contract_to_session_state(contract_number):
    conn = get_mdb_connection(mdb_path)
    try:
        # SQL ausführen
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manuelle_daten WHERE vertragsnummer = ?", (contract_number,))
        row = cursor.fetchone()  # Ruft die erste Zeile des Abfrageergebnisses ab
       
        # Überprüfen Sie, ob eine Zeile gefunden wurde
        if row:
            # Speichern Sie jede Spalte im session_state
            for column in row.keys():
                st.session_state[column] = row[column]
        else:
            # Keine Zeile gefunden, also fügen Sie eine neue Zeile nur mit der Vertragsnummer ein
            cursor.execute("INSERT INTO manuelle_daten (vertragsnummer) VALUES (?)", (contract_number,))
            conn.commit()
            st.info('New contract number added to the dataset.')
            
    except Exception as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

def save_contract_change(contract_number, column, value):
    # Stellt sicher, ob 'md' im session_state liegt
    if 'md' in st.session_state:
        # Umwandlung vom Dataset zum Dataframe 
        df = st.session_state['md']
        # Zeilenindex finden für die Contractnumber
        row_index = df.index[df['vertragsnummer'] == contract_number]
        # Prüfen ob genau einmal ein Eintrag drin steht
        if len(row_index) == 1:
            # Aktualisieren Sie den Wert in der angegebenen Spalte für die Zeile
            df.loc[row_index, column] = value  
            # Speichern Sie den aktualisierten DataFrame wieder in session_state
            st.session_state['md'] = df
            st.success('The contract was successfully updated.')
        elif len(row_index) == 0:
            st.error('No contract number found in the dataset.')
        else:
            st.error('More than one row found for this contract number. Check the uniqueness of the contract numbers.')
    else:
        st.error('Dataset is not present in session_state.')

if 'insurer_opt' not in st.session_state:
    st.session_state['insurer_opt'] = insurer_opt
if 'wording_opt' not in st.session_state:
    st.session_state['wording_opt'] = wording_opt

def select_list(list_name):
    # Hier den Pfad zur dd_selection.py-Datei angeben
    file_path = 'edit_selection.py'

    # Überprüfen, ob die Datei existiert
    if os.path.exists(file_path):
        # Listen aus der Datei lesen
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            module = ast.parse(file_content)
            for node in module.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == list_name:
                            return eval(compile(ast.Expression(node.value), filename=file_path, mode='eval'))
    return None

def save_lists_to_file():
    try:
        with open('edit_selection.py', 'w', encoding='utf-8') as file:
            file.write("# insurer_opt Liste\n")
            file.write(f"insurer_opt = {st.session_state.insurer_opt}\n\n")

            file.write("# wording_opt Liste\n")
            file.write(f"wording_opt = {st.session_state.wording_opt}\n")
        st.success("Änderungen erfolgreich gespeichert")
    except Exception as e:
        st.error(f"Fehler beim Speichern der Datei: {e}")

def update_database(selected_entry, new_value):
    conn = get_mdb_connection(mdb_path)
    cursor = conn.cursor()
    affected_columns = [
        'neuer_fuehrender_versicherer',
        'neue_beteiligte_versicherer(1)', 'neue_beteiligte_versicherer(2)', 'neue_beteiligte_versicherer(3)',
        'neue_beteiligte_versicherer(4)', 'neue_beteiligte_versicherer(5)', 'neue_beteiligte_versicherer(6)',
        'neue_beteiligte_versicherer(7)', 'neue_beteiligte_versicherer(8)', 'neue_beteiligte_versicherer(9)',
        'neue_beteiligte_versicherer(10)', 'ausschreibung_an_versicherer_1', 'vr_2', 'vr_3', 'vr_4',
        'vr_5', 'vr_6', 'vr_7', 'vr_8', 'vr_9', 'vr_10', 'vr_11', 'vr_12', 'vr_13', 'vr_14', 'vr_15'
    ]
    try:
        for column in affected_columns:
            col_escaped = f"`{column}`"
            sql_update_query = f"UPDATE manuelle_daten SET {col_escaped} = ? WHERE {col_escaped} = ?"
            cursor.execute(sql_update_query, (new_value, selected_entry))
        conn.commit()
        print(f"Updated columns from {selected_entry} to {new_value} where applicable.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()


def display_dropdown_edit():
    # Dropdown-Menü für die Auswahl der Liste
    dropdown_options = ['insurer_opt', 'wording_opt']
    selected_list_name = st.selectbox("Dropdown 1: Liste auswählen:", dropdown_options)

    # Dropdown-Menü für die Auswahl des Eintrags
    selected_list = select_list(selected_list_name)
    selected_entry = st.selectbox("Dropdown 2: Eintrag auswählen:", selected_list)

    # Aufteilen des Bildschirms in drei Spalten für die Buttons
    col1, col2 = st.columns(2)
    
    new_item = col1.text_input("Neuer Eintrag:")

    if col1.button("Eintrag hinzufügen", key="add_entry_button"):
        if new_item:
            st.session_state[selected_list_name].append(new_item)
            st.success(f"Eintrag '{new_item}' wurde zur Liste hinzugefügt.")
            save_lists_to_file()

    new_value = col2.text_input("Neuer Wert:", value=selected_entry, key='neuer_wert')
    
    if col2.button("Eintrag bearbeiten", key="edit_entry_confirm_button"):
        if selected_entry in selected_list:
            index = selected_list.index(selected_entry)
            # Überprüfen, ob der Index innerhalb des gültigen Bereichs liegt
            if 0 <= index < len(st.session_state[selected_list_name]):
                st.session_state[selected_list_name][index] = new_value
                st.success(f"Eintrag '{selected_entry}' wurde zu '{new_value}' geändert.")
                update_database(selected_entry, new_value)
                save_lists_to_file()
            else:
                st.error("Ungültiger Index für die Bearbeitung des Eintrags.")
        else:
            st.error("Der ausgewählte Eintrag ist nicht in der Liste vorhanden.")

    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
    if st.button("Eintrag löschen", key="delete_entry_confirm_button"):
        if selected_entry in selected_list:
            st.session_state[selected_list_name].remove(selected_entry)
            st.success(f"Eintrag '{selected_entry}' wurde gelöscht.")
            save_lists_to_file()

# Hauptfunktion, die die App steuert
def main():   
    with st.sidebar: 
        try:
        # Versuchen Sie, das Bild zu laden und anzuzeigen
            st.image(image_path)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")
        st.markdown("<hr style='margin:0; border: none; border-top: 4px solid #002c77;'>", unsafe_allow_html=True)
        # Advisorauswahl
        td = st.session_state['td']  
        advisor_selection = st.selectbox('Auswahl Advisor:', td['Advisor'].unique().tolist())
        st.session_state['advisor'] = advisor_selection

       # Line of Business basierend auf Advisor
        line_of_business_options = td[td['Advisor'] == advisor_selection]['Line of Business'].unique().tolist()
        line_of_business_selection = st.selectbox('Auswahl Line of Business:', line_of_business_options)
        st.session_state['line_of_business'] = line_of_business_selection

        # Vertrag basierend auf Advisor und Line of Business
        vertrags_id_options = td[(td['Advisor'] == advisor_selection) & (td['Line of Business'] == line_of_business_selection)]['Vertrag'].dropna().unique()
        vertrags_id_options = [int(id) for id in vertrags_id_options]  # float zu int
        vertrags_id_selection = st.selectbox('Auswahl Vertrag:', vertrags_id_options)
        st.session_state['vertrags_id'] = vertrags_id_selection
        st.markdown("<hr style='margin:0; border: none; border-top: 4px solid #002c77;'>", unsafe_allow_html=True)
        st.markdown('<br>', unsafe_allow_html=True)
        st.markdown("""<style>.streamlit-button {
        width: 100%;    /* Set the width to maximum of the container */
        height: 50px;   /* Set a fixed height */
        margin-bottom: 5px; /* Optional: add some space between the buttons */}</style>""", unsafe_allow_html=True)
        if st.button('Aktuelle Vertragsdaten'):
            st.session_state['current_tab'] = 'Aktuelle Vertragsdaten'
        if st.button('Risikoinformationen'):
            st.session_state['current_tab'] = 'Risikoinformationen'
        if st.button('Ausschreibung'):
            st.session_state['current_tab'] = 'Ausschreibung'
        if st.button('Renewalergebnis'):
            st.session_state['current_tab'] = 'Renewalergebnis'
        if st.button('Abarbeitung des Renewals'):
            st.session_state['current_tab'] = 'Abarbeitung des Renewals'
        if st.button('Bemerkung'):
            st.session_state['current_tab'] = 'Bemerkung'
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True) 
        if st.button('Dropdown bearbeiten'):
            st.session_state['current_tab'] = 'Dropdown bearbeiten'
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.button('Datensatz kopieren'):
            st.session_state['current_tab'] = 'Datensatz kopieren'
        
    st.markdown("<h2 style='color: #002c77'>Dateneingabe</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:0; border: none; border-top: 2px solid #002c77;'>", unsafe_allow_html=True)
    col1, col2, col3= st.columns(3)
    with col1:
        st.write('Gewählter Advisor:', st.session_state['advisor'])
    with col2: 
        if line_of_business_selection:
            st.write('Gewählte Line of Business:', st.session_state['line_of_business'])
    with col3:
        if  vertrags_id_selection:
            st.write('Gewählter Vertrag:', str(st.session_state['vertrags_id']))
            
    filtered_df2 = td[td['Vertrag'] == vertrags_id_selection][['EUR Net Premium Amount 2023', ' EUR Net Revenue 2023']]
    st.dataframe(filtered_df2.style.format(thousands="",precision=2), hide_index=True) 
    st.markdown("<hr style='margin:0; border: none; border-top: 2px solid #002c77;'>", unsafe_allow_html=True)
    filtered_df1 = td[(td['Advisor'] == advisor_selection) & (td['Line of Business'] == line_of_business_selection)][['Vertrag', 'Kunde', 'Company / Office','Line of Business', 'Tax/Commission Code - Label', 'Leading Insurer']]
    st.dataframe(filtered_df1.style.format(thousands="",precision=0), hide_index=True)          
    st.markdown("<hr style='margin:0; border: none; border-top: 2px solid #002c77;'>", unsafe_allow_html=True)
    # Initialisiere 'current_tab' in session_state, wenn nicht vorhanden
    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = 'Aktuelle Vertragsdaten'  # Standardmäßig der erste Tab 
   
    # Initialisiert den Container
    container = st.container()
    with container:
        # Zeige Inhalt basierend auf dem aktuellen Tab
        if st.session_state['current_tab'] == 'Aktuelle Vertragsdaten':
            display_vertragsdaten()
        elif st.session_state['current_tab'] == 'Risikoinformationen':
            display_risiko_information()
        elif st.session_state['current_tab'] == 'Ausschreibung':
            display_ausschreibung()
        elif st.session_state['current_tab'] == 'Renewalergebnis':
            display_renewal_ergebnis()
        elif st.session_state['current_tab'] == 'Abarbeitung des Renewals':
            display_abarbeitung_renewal()
        elif st.session_state['current_tab'] == 'Bemerkung':
            display_bemerkung()
        elif st.session_state['current_tab'] == 'Dropdown bearbeiten':
            display_dropdown_edit()
        elif st.session_state['current_tab'] == 'Datensatz kopieren':
            display_copy_function()
                  
mdb_path = "manuelle_daten.db"
tdb_path = "technische_daten.db"
none_var = None

logo_path =  "favicon.ico"
im = Image.open(logo_path)
image_path = r"header.png"
st.set_page_config(
    page_title="Praxisprojekt Eingabemaske Marsh",
    page_icon=im,
    layout="wide"
)

# Laden der Datensätze
if 'md' not in st.session_state:
    st.session_state['md'] = load_sqlite_data('manuelle_daten', mdb_path)
if 'td' not in st.session_state:
    st.session_state['td'] = load_sqlite_data('technische_daten', tdb_path)

st.markdown("""<style>.element-container:has(#button-after) + div button {/
    border: 4px solid #009de0;
    color: white; /* Weiße Textfarbe */
    background-color: #002c77;}</style>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()  