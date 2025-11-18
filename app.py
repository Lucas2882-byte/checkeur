import streamlit as st
import pandas as pd
import time
from io import BytesIO

st.set_page_config(page_title="Vérificateur d'avis Google", page_icon="⭐", layout="wide")

st.title("🔍 Vérificateur d'avis Google Maps")
st.markdown("Analysez votre fichier Excel et marquez manuellement les avis présents ou supprimés")

if 'status_edits' not in st.session_state:
    st.session_state.status_edits = {}

if 'master_df' not in st.session_state:
    st.session_state.master_df = None

uploaded_file = st.file_uploader("📁 Téléchargez votre fichier Excel", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        
        if st.session_state.master_df is None or st.button("🔄 Recharger le fichier (efface les modifications)"):
            st.session_state.master_df = df.copy()
            st.session_state.status_edits = {}
            st.rerun()
        
        df = st.session_state.master_df.copy()
        
        st.success(f"✅ Fichier chargé avec succès: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        
        required_columns = ['GMB listings link', 'Review Links']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Colonnes manquantes: {', '.join(missing_columns)}")
        else:
            st.markdown("---")
            st.subheader("🔎 Recherche par GMB Listing")
            
            gmb_listings = df['GMB listings link'].dropna().unique().tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                search_method = st.radio(
                    "Méthode de recherche:",
                    ["Sélectionner dans la liste", "Recherche par texte"]
                )
            
            selected_gmb = None
            search_text = ""
            
            with col2:
                if search_method == "Sélectionner dans la liste":
                    selected_gmb = st.selectbox(
                        "Choisir un GMB listing:",
                        options=["Tous"] + gmb_listings
                    )
                else:
                    search_text = st.text_input(
                        "Rechercher un GMB listing (Ctrl+F):",
                        placeholder="Entrez une partie du lien..."
                    )
            
            if search_method == "Sélectionner dans la liste" and selected_gmb and selected_gmb != "Tous":
                filtered_df = df[df['GMB listings link'] == selected_gmb].copy()
            elif search_method == "Recherche par texte" and search_text:
                filtered_df = df[df['GMB listings link'].str.contains(search_text, case=False, na=False)].copy()
            else:
                filtered_df = df.copy()
            
            st.markdown("---")
            st.subheader(f"📊 Résultats: {len(filtered_df)} avis trouvés")
            
            if len(filtered_df) > 0:
                if 'Statut' not in filtered_df.columns:
                    filtered_df['Statut'] = '⚪ À vérifier'
                
                for idx, row in filtered_df.iterrows():
                    review_link = row.get('Review Links', '')
                    if review_link and review_link in st.session_state.status_edits:
                        filtered_df.at[idx, 'Statut'] = st.session_state.status_edits[review_link]
                
                st.info("""
                💡 **Comment utiliser:**
                1. Cliquez sur un lien "Review Links" pour ouvrir l'avis dans votre navigateur
                2. Vérifiez si l'avis existe toujours sur Google Maps
                3. Modifiez le "Statut" en double-cliquant sur la cellule :
                   - Tapez: **✅** si l'avis est présent
                   - Tapez: **❌** si l'avis est supprimé
                4. Téléchargez le fichier Excel mis à jour avec vos vérifications
                """)
                
                display_columns = ['GMB listings link', 'GMB listings Name ', 'Review Links', 'Name', 'Date', 'Statut', 'Content']
                available_columns = [col for col in display_columns if col in filtered_df.columns]
                
                edited_df = st.data_editor(
                    filtered_df[available_columns],
                    use_container_width=True,
                    hide_index=True,
                    key="data_editor",
                    column_config={
                        "Review Links": st.column_config.LinkColumn(
                            "Review Links",
                            help="Cliquez pour ouvrir l'avis dans votre navigateur",
                            max_chars=100
                        ),
                        "GMB listings link": st.column_config.LinkColumn(
                            "GMB listings link",
                            help="Lien vers la page Google Maps Business",
                            max_chars=100
                        ),
                        "Statut": st.column_config.TextColumn(
                            "Statut",
                            help="Modifiez: ✅ (présent) ou ❌ (supprimé) ou ⚪ (à vérifier)",
                            max_chars=50
                        ),
                        "Name": st.column_config.TextColumn(
                            "Nom",
                            help="Auteur de l'avis"
                        ),
                        "Date": st.column_config.TextColumn(
                            "Date",
                            help="Date de l'avis"
                        ),
                        "Content": st.column_config.TextColumn(
                            "Contenu",
                            help="Contenu de l'avis",
                            width="large"
                        )
                    },
                    num_rows="fixed"
                )
                
                for _, row in edited_df.iterrows():
                    review_link = row.get('Review Links', '')
                    if review_link and pd.notna(review_link):
                        new_status = row.get('Statut', '⚪ À vérifier')
                        st.session_state.status_edits[review_link] = new_status
                
                st.markdown("---")
                
                full_df_with_edits = st.session_state.master_df.copy()
                if 'Statut' not in full_df_with_edits.columns:
                    full_df_with_edits['Statut'] = '⚪ À vérifier'
                for idx, row in full_df_with_edits.iterrows():
                    review_link = row.get('Review Links', '')
                    if review_link and review_link in st.session_state.status_edits:
                        full_df_with_edits.at[idx, 'Statut'] = st.session_state.status_edits[review_link]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_all = len(full_df_with_edits)
                present_all = len(full_df_with_edits[full_df_with_edits['Statut'].str.contains('✅', na=False)])
                deleted_all = len(full_df_with_edits[full_df_with_edits['Statut'].str.contains('❌', na=False)])
                pending_all = len(full_df_with_edits[full_df_with_edits['Statut'].str.contains('⚪', na=False)])
                edited_count = len(st.session_state.status_edits)
                
                col1.metric("📊 Total (fichier)", total_all)
                col2.metric("✅ Présents", present_all)
                col3.metric("❌ Supprimés", deleted_all)
                col4.metric("⚪ À vérifier", pending_all)
                col5.metric("✏️ Modifications", edited_count)
                
                st.markdown("---")
                
                full_export_df = st.session_state.master_df.copy()
                if 'Statut' not in full_export_df.columns:
                    full_export_df['Statut'] = '⚪ À vérifier'
                
                for idx, row in full_export_df.iterrows():
                    review_link = row.get('Review Links', '')
                    if review_link and review_link in st.session_state.status_edits:
                        full_export_df.at[idx, 'Statut'] = st.session_state.status_edits[review_link]
                
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    full_export_df.to_excel(writer, index=False)
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Télécharger les résultats (Excel)",
                    data=buffer,
                    file_name=f"verification_avis_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
                
                st.info("💾 N'oubliez pas de télécharger vos résultats avant de fermer la page !")
                
            else:
                st.warning("⚠️ Aucun résultat trouvé pour cette recherche")
                
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier: {str(e)}")
else:
    st.info("👆 Veuillez télécharger un fichier Excel pour commencer")
    
    with st.expander("ℹ️ Guide d'utilisation"):
        st.markdown("""
        ### Comment utiliser cette application:
        
        1. **Téléchargez votre fichier Excel** contenant les colonnes:
           - `GMB listings link`: Lien vers la page Google Maps Business
           - `Review Links`: Liens vers les avis individuels
           - Autres colonnes: `Name`, `Date`, `Content` (optionnelles)
           
        2. **Recherchez un GMB listing spécifique**:
           - Utilisez la liste déroulante pour sélectionner un listing
           - Ou utilisez la recherche par texte (style Ctrl+F) pour filtrer
           
        3. **Vérifiez les avis manuellement**:
           - Cliquez sur chaque lien "Review Links" pour ouvrir l'avis dans votre navigateur
           - Vérifiez si le message "Cet avis n'est plus disponible" apparaît
           
        4. **Marquez le statut**:
           - Double-cliquez sur la cellule "Statut"
           - Tapez **✅** si l'avis est présent
           - Tapez **❌** si l'avis est supprimé
           - Laissez **⚪** si vous n'avez pas encore vérifié
           
        5. **Téléchargez vos résultats**:
           - Cliquez sur "Télécharger les résultats (Excel)"
           - Vous aurez un fichier avec tous vos statuts enregistrés
           
        ### Raccourcis clavier utiles:
        
        - **Double-clic** sur une cellule pour modifier
        - **Tab** pour passer à la cellule suivante
        - **Entrée** pour valider et passer à la ligne suivante
        - **Ctrl+C / Ctrl+V** pour copier/coller
        
        ### Conseils:
        
        - Travaillez par GMB listing pour plus de clarté
        - Vérifiez régulièrement (par exemple, tous les mois)
        - Gardez un historique de vos vérifications précédentes
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 Workflow recommandé pour votre check mensuel:
    
    1. 📁 Téléchargez votre fichier Excel du mois dernier (ou créez-en un nouveau)
    2. 🔍 Sélectionnez le premier GMB listing à vérifier
    3. 🖱️ Cliquez sur chaque lien "Review Links" pour vérifier les avis
    4. ✍️ Marquez ✅ ou ❌ selon ce que vous voyez
    5. 💾 Téléchargez le fichier Excel mis à jour
    6. 🔁 Répétez pour les autres GMB listings le mois prochain
    """)
