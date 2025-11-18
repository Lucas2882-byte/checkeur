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
        
        # Ajouter une colonne pour le numéro de ligne Excel (index + 2 car ligne 1 = en-têtes)
        df['Excel_Row'] = df.index + 2
        
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
            
            # Filtre par numéro de ligne Excel (les numéros verts à gauche)
            st.markdown("---")
            st.subheader("🔢 Filtrer par numéro de ligne Excel")
            
            # Vérifier si la colonne "Excel_Row" existe
            has_excel_row = 'Excel_Row' in filtered_df.columns
            
            if has_excel_row and len(filtered_df) > 0:
                min_row = int(filtered_df['Excel_Row'].min())
                max_row = int(filtered_df['Excel_Row'].max())
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    start_line = st.number_input(
                        "Ligne Excel de début:",
                        min_value=min_row,
                        max_value=max_row,
                        value=min_row,
                        step=1,
                        help="Numéro de ligne Excel (colonne verte à gauche)"
                    )
                
                with col2:
                    end_line = st.number_input(
                        "Ligne Excel de fin:",
                        min_value=min_row,
                        max_value=max_row,
                        value=max_row,
                        step=1,
                        help="Numéro de ligne Excel (colonne verte à gauche)"
                    )
                
                with col3:
                    st.write("")
                    st.write("")
                    if st.button("🔄 Réinitialiser le filtre"):
                        st.rerun()
                
                # Appliquer le filtre basé sur la colonne "Excel_Row"
                if start_line <= end_line:
                    filtered_df = filtered_df[
                        (filtered_df['Excel_Row'] >= start_line) & 
                        (filtered_df['Excel_Row'] <= end_line)
                    ].copy()
            elif len(filtered_df) > 0:
                st.info("ℹ️ Impossible de déterminer les numéros de ligne Excel. Filtre désactivé.")
            
            st.markdown("---")
            st.subheader(f"📊 Résultats: {len(filtered_df)} avis trouvés")
            
            if len(filtered_df) > 0:
                st.info("""
                💡 **Comment utiliser:**
                1. Cliquez sur un lien pour ouvrir l'avis dans votre navigateur
                2. Vérifiez si l'avis existe toujours sur Google Maps
                3. Cliquez sur **✅** si l'avis est présent ou **❌** s'il est supprimé
                4. Téléchargez le fichier Excel mis à jour avec vos vérifications
                """)
                
                for idx, row in filtered_df.iterrows():
                    review_link = row.get('Review Links', '')
                    name = row.get('Name', 'N/A')
                    content = row.get('Content', 'Pas de contenu')
                    
                    current_status = st.session_state.status_edits.get(review_link, '⚪ À vérifier')
                    
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"**{name}**")
                        if review_link and pd.notna(review_link):
                            st.markdown(f"🔗 [Ouvrir l'avis]({review_link})")
                        st.markdown(f"_{content}_")
                        
                        if current_status == '✅ Présent':
                            st.success("✅ Marqué comme présent")
                        elif current_status == '❌ Supprimé':
                            st.error("❌ Marqué comme supprimé")
                    
                    with col2:
                        st.write("")
                        if st.button("✅", key=f"present_{idx}", help="Marquer comme présent"):
                            st.session_state.status_edits[review_link] = '✅ Présent'
                            st.rerun()
                        if st.button("❌", key=f"deleted_{idx}", help="Marquer comme supprimé"):
                            st.session_state.status_edits[review_link] = '❌ Supprimé'
                            st.rerun()
                    
                    st.markdown("---")
                
                # Récapitulatif de la recherche en cours
                filtered_status_counts = {
                    'present': 0,
                    'deleted': 0,
                    'pending': 0,
                    'total': len(filtered_df)
                }
                
                for idx, row in filtered_df.iterrows():
                    review_link = row.get('Review Links', '')
                    current_status = st.session_state.status_edits.get(review_link, '⚪ À vérifier')
                    
                    if '✅' in current_status:
                        filtered_status_counts['present'] += 1
                    elif '❌' in current_status:
                        filtered_status_counts['deleted'] += 1
                    else:
                        filtered_status_counts['pending'] += 1
                
                # Afficher le récap uniquement si tous les avis sont vérifiés
                if filtered_status_counts['pending'] == 0 and filtered_status_counts['total'] > 0:
                    st.markdown("---")
                    st.success("🎉 Tous les avis de cette recherche ont été vérifiés !")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("📊 Total vérifié", filtered_status_counts['total'])
                    col2.metric("✅ Avis présents", filtered_status_counts['present'])
                    col3.metric("❌ Avis supprimés", filtered_status_counts['deleted'])
                    
                    # Texte à copier-coller
                    st.markdown("### 📋 Texte à copier-coller")
                    
                    gmb_name = filtered_df.iloc[0].get('GMB listings Name ', 'votre fiche') if len(filtered_df) > 0 else 'votre fiche'
                    
                    # Créer la liste des avis présents uniquement
                    present_reviews = []
                    review_number = 1
                    for idx, row in filtered_df.iterrows():
                        review_link = row.get('Review Links', '')
                        current_status = st.session_state.status_edits.get(review_link, '')
                        
                        if '✅' in current_status:
                            name = row.get('Name', 'N/A')
                            content = row.get('Content', 'Pas de contenu')
                            present_reviews.append(f"{review_number}. {review_link} - {name} - {content}")
                            review_number += 1
                    
                    # Nombre d'avis présents
                    num_present = len(present_reviews)
                    
                    copy_text = f"Voici les {num_present} avis déposés sur votre fiche {gmb_name} ⭐:\n\n" + "\n".join(present_reviews)
                    
                    st.markdown("**Cliquez sur l'icône de copie en haut à droite du bloc ci-dessous :**")
                    st.code(copy_text, language=None)
                
                st.markdown("---")
                
                # Métriques pour la recherche en cours (filtered_df)
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("📊 Total (recherche)", filtered_status_counts['total'])
                col2.metric("✅ Présents", filtered_status_counts['present'])
                col3.metric("❌ Supprimés", filtered_status_counts['deleted'])
                col4.metric("⚪ À vérifier", filtered_status_counts['pending'])
                
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
