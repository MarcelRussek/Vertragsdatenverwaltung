# Dropdown-Optionen für Marsh-Dateneingabe
# Alle möglichen Optionen werden hier definiert. Die zur Bearbeitung freigegbenen Listen werden in edit_selection.py gespeichert.
# Desweiteren sind alle Spaltennamen für die SQL-Verarbeitung, "escaped", hinterlegt.
#region ***platz_opt***
platz_opt = ['schwieriges Placement',
 'leichtes Placement',
 'normales Placement',
 'keine Platzierung gewählt']
#endregion
#region ***risiko_opt***
risiko_opt = ['schweres Risiko ',
 'leichtes Risiko',
 'mittleres Risiko',
 'keine Risikoart gewählt']
#endregion
#region ***ja_nein_opt***
ja_nein_opt =['ja', 'nein', 'keine Auswahl getroffen']
#endregion
#region ***vertragsart_opt***
vertragsart_opt = ['Primary',
'1. Layer',
'2. Layer',
'3. Layer',
'4. Layer',
'5. Layer',
'6. Layer',
'7. Layer',
'8. Layer',
'9. Layer',
'10. Layer',
'keine Vertragsart gewählt']
#endregion
#region ***ausschreibung_opt***
ausschreibung_opt = ['Ausschreibung (Marktbefragung)',
'Ausschreibung (zielgerichtet)',
'Ausschreibung (Beteiligung)',
'keine Ausschreibung', 'keine Auswahl getroffen']
#endregion
#region ***status_opt***
status_opt = ['verlängert - Angebot angenommen',
'verlängert - tacit Renewal',
'offen - Angebot liegt beim Kunden vor',
'offen - Angebot liegt dem Kunden nicht vor',
'offen - Angebot liegt beim Kunden in Teilen vor',
'offen'] # offen ist der Standardstatus
#endregion
#region ***renewal_opt***
renewal_opt = ['unverändertes Konsortium', 
'Wechsel führender Versicherer',
'Wechsel beteiligter Versicherer', 
'keine Auswahl getroffen']
#endregion
#region ***schicksal_opt***
schicksal_opt = ['Mandat gehalten',
'Mandat verloren',
'Mandat neu', 
'keine Auswahl getroffen']
#endregion
#region ***ausschreibung_opt***
ausschreibung_opt = ['Kein Auswahl getroffen',
 'Aktiv',
'Gezeichnet',
'Vorgang abgebrochen', 
'VR hat abgelehnt', 
'keine Rückmeldung vom Versicherer', 
'Angebot des VR abgelehnt', 
'Quotiert']
#endregion
#region ***sql_columns***
sql_columns = [
'ivp',
'haupt_vertragsdeckungssumme',
'selbstbehalt_attachment_point',
'`hoehe_der_courtage_lokalpolicen(in_%)`',
'`akt._jahresprogrammbeitrag(inkl._lopos)`',
'vertragsart',
'vertical_pricing',
'risiko_dialog',
'risikoinfos',
'jahresfahrplan_vom_ce_erhalten',
'ausschreibung_fuer_kommendes_renewal',
'ausschreibung_an_versicherer_1',
'vr_2',
'vr_3',
'vr_4',
'vr_5',
'vr_6',
'vr_7',
'vr_8',
'vr_9',
'vr_10',
'vr_11',
'vr_12',
'vr_13',
'vr_14',
'vr_15',
'angebotene_praemie_1',
'angebotene_praemie_2',
'angebotene_praemie_3',
'angebotene_praemie_4',
'angebotene_praemie_5',
'angebotene_praemie_6',
'angebotene_praemie_7',
'angebotene_praemie_8',
'angebotene_praemie_9',
'angebotene_praemie_10',
'angebotene_praemie_11',
'angebotene_praemie_12',
'angebotene_praemie_13',
'angebotene_praemie_14',
'angebotene_praemie_15',
'status_des_angebots_1',
'status_des_angebots_2',
'status_des_angebots_3',
'status_des_angebots_4',
'status_des_angebots_5',
'status_des_angebots_6',
'status_des_angebots_7',
'status_des_angebots_8',
'status_des_angebots_9',
'status_des_angebots_10',
'status_des_angebots_11',
'status_des_angebots_12',
'status_des_angebots_13',
'status_des_angebots_14',
'status_des_angebots_15',
'platzierungsart',
'risikoart',
'kuefri',
'status',
'renewalergebnis',
'neuer_fuehrender_versicherer',
'`neue_beteiligte_versicherer(1)`',
'`neue_beteiligte_versicherer(2)`',
'`neue_beteiligte_versicherer(3)`',
'`neue_beteiligte_versicherer(4)`',
'`neue_beteiligte_versicherer(5)`',
'`fuehrungsquote(in_%)`',
'`beteiligungsquote(in_%)_1`',
'`beteiligungsquote(in_%)_2`',
'`beteiligungsquote(in_%)_3`',
'`beteiligungsquote(in_%)_4`',
'`beteiligungsquote(in_%)_5`',
'`neuer_jahresprogrammbeitrag(100%_exkl.lopos)`',
'`neuer_jahresprogrammbeitrag(100%_inkl.lopos)`',
'pdcs',
'`allokation+rechnung`',
'mgc',
'pol',
'schicksal_des_kunden',
'wording_version',
'bemerkung'
]
#endregion
