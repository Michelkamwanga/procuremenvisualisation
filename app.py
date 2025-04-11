import streamlit as st
import pandas as pd
import plotly.express as px
import os
import matplotlib.pyplot as plt
import seaborn as sns


# Configuration de la page
st.set_page_config(page_title="CARE DRC PROCUREMENT STATUS DASHBOARD", layout="wide")

# Chargement du logo
logo_path = "images.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=150)

# En-tête
st.title("CARE DRC PROCUREMENT STATUS DASHBOARD")
st.markdown("**Auteur : CARE DRC | Conception : Michel Kamwanga | Contribution technique : Bennet Shabani**")

# Chargement des données
uploaded_file = st.file_uploader("Chargez un fichier Excel extrait de Peoplesoft. Ne changez pas les noms de colonnes ", type=["xls", "csv","xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Mapping des valeurs de la colonne 'Dept ID'
    dept_mapping = {
        "CD0001": "Kinshasa", "CD0002": "Goma", "CD-SPC": "Congo SPC",
        "CD0003": "Kasongo", "CD0004": "Kindu", "CD0005": "Butembo", "CD0006": "Beni",
        "CD0007": "Lubero", "CD0008": "Kirumba", "CD0009": "Mbujimayi", "CD0010": "Kalima",
        "CD0013": "Uvira", "CD0014": "Mweneditu"
    }
    df['Dept ID'] = df['Dept ID'].map(dept_mapping)

    # Sidebar pour les filtres
    with st.sidebar:
        st.header("Filtres")
        options = df['Dept ID'].dropna().unique()
        bureau = st.multiselect("Bureau", options=options, default=options)
        projet = st.multiselect("Projet", df['Fund Code'].dropna().unique(), default=df['Fund Code'].unique())
        project_id = st.multiselect("Project ID", df['Project ID'].dropna().unique(), default=df['Project ID'].unique())
        buyer_options = df['PO Buyer'].dropna().unique()  # Supprimer les NaN
        buyer_id = st.multiselect("PO Buyer", buyer_options, default=[])
        annee = st.multiselect("Année", df['PR-Year'].dropna().unique(), default=df['PR-Year'].unique())
        statut_pr = st.multiselect("Statut du PR", df['PR Status'].dropna().unique(), default=df['PR Status'].unique())
        devise = st.multiselect("Devise", df['Currency'].dropna().unique(), default=df['Currency'].unique())
        requisition = st.multiselect("Requisition/DA", df['Requisition ID'].dropna().unique(), default=[])
        po = st.multiselect("PO/RFQ", df['RFQ ID'].dropna().unique(), default=[])
        voucher = st.multiselect("Voucher", df['Voucher ID'].dropna().unique(), default=[])
        prstatus = st.multiselect("PR Status", df['PR Status'].dropna().unique(), default=[])
        postatus = st.multiselect("PO Status", df['PO Status'].dropna().unique(), default=[])

    
    # Appliquer les filtres
    if bureau:
        df = df[df['Dept ID'].isin(bureau)]
    if projet:
        df = df[df['Fund Code'].isin(projet)]
    if project_id:
        df = df[df['Project ID'].isin(project_id)]
    if buyer_id:
        df = df[df['PO Buyer'].isin(buyer_id)]
    if annee:
        df = df[df['PR-Year'].isin(annee)]
    if statut_pr:
        df = df[df['PR Status'].isin(statut_pr)]
    if devise:
        df = df[df['Currency'].isin(devise)]
    if requisition:
        df = df[df['Requisition ID'].isin(requisition)]
    if po:
        df = df[df['RFQ ID'].isin(po)]
    if voucher:
        df = df[df['Voucher ID'].isin(voucher)]
    if prstatus:
        df = df[df['PR Status'].isin(prstatus)]
    if postatus:
        df = df[df['PO Status'].isin(postatus)]

    # Style CSS personnalisé
    st.markdown("""
        <style>
            .metric-container {
                background-color: orange;
                border: 2px solid green;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                font-weight: bold;
                color: white;
                font-size: 15px;
            }
            .metric-value {
                font-size: 30px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Fonction pour afficher les métriques avec style
    def display_metric(label, value, col):
        col.markdown(f"""
            <div class='metric-container'>
                <div class='metric-value'>{value}</div>
                <div>{label}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # OVERVIEW
    st.subheader("OVERVIEW")
    with st.container():
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        display_metric("Réquisitions", df['Requisition ID'].nunique(), col1)
        display_metric("Nombre RFQ", df['RFQ ID'].nunique(), col2)
        display_metric("Nombre PO", df['PO No.'].nunique(), col3)
        display_metric("PO Reçu", df['Receipt Nbr'].nunique(), col4)
        display_metric("Nb vouchers", df['Voucher ID'].nunique(), col5)
        display_metric("Nb Paiements", df['Vch Pymt Ref'].nunique(), col6)
        display_metric("Paiements", df['Vch Last Approver'].nunique(), col7)

    st.subheader("")
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        display_metric("Quantités commandées", f"{int(df['Quantity Ordered'].sum()):,}".replace(","," "), col1)
        display_metric("Quantités recues", f"{int(df['Quantity Received'].sum()):,}".replace(","," "), col2)
        display_metric("Balance", f"{int(df['Balance Pending to be Rcvd'].sum()):,}".replace(","," "), col3)
        display_metric("Valeurs engagées", f"${int(df['Item Total'].sum()):,}".replace(",", " "), col4)

    # Assurer que les colonnes 'PR-Year' et 'PR-Month' sont bien des entiers
    df['PR-Year'] = df['PR-Year'].astype(int)
    df['PR-Month'] = df['PR-Month'].astype(int)

    # Créer une colonne 'Date' combinant 'PR-Year' et 'PR-Month' avec un jour fixe (par exemple, 1er du mois)
    df['Date'] = pd.to_datetime(df['PR-Year'].astype(str) + '-' + df['PR-Month'].astype(str) + '-01')

    # Assurer qu'il n'y a pas de valeurs NaN dans la nouvelle colonne 'Date'
    df = df.dropna(subset=['Date'])

    with st.container():
        col1, col2 = st.columns(2)
        
        # Graphique pour les Quantités Commandées avec des barres plus grosses
        fig1 = px.bar(df, x='Date', y='Quantity Ordered', title="Quantités Commandées", labels={'Date': 'Date', 'Quantity Ordered': 'Quantité Commandée'})
        fig1.update_layout(
            xaxis_title='Mois',
            yaxis_title='Quantité Commandée',
            xaxis_tickformat="%b %Y", 
            template='plotly_dark',
            barmode='group',
            xaxis_tickangle=45,  # Angles de rotation des ticks de l'axe X
            bargap=0.2,  # Espacement entre les barres
            legend_title="Légende",  # Titre de la légende
            legend=dict(
                x=1,  # Position horizontale de la légende
                y=1,  # Position verticale de la légende
                traceorder='normal',  # Ordre des éléments de la légende
                font=dict(size=14),  # Taille de la police de la légende
                bgcolor='rgba(255, 255, 255, 0.5)',  # Couleur de fond de la légende
                bordercolor='red',  # Bordure de la légende
                borderwidth=2  # Largeur de la bordure de la légende
            )
        )
        col1.plotly_chart(fig1, use_container_width=True)

        # Graphique pour les Quantités Reçues avec des barres plus grosses
        fig2 = px.bar(df, x='Date', y='Quantity Received', title="Quantités Reçues", labels={'Date': 'Date', 'Quantity Received': 'Quantité Reçue'})
        fig2.update_layout(
            xaxis_title='Mois',
            yaxis_title='Quantité Reçue',
            xaxis_tickformat="%b %Y", 
            template='plotly_dark',
            barmode='group',
            xaxis_tickangle=40,  # Angles de rotation des ticks de l'axe X
            bargap=0.2,  # Espacement entre les barres
            legend_title="Légende",  # Titre de la légende
            legend=dict(
                x=1,  # Position horizontale de la légende
                y=1,  # Position verticale de la légende
                traceorder='normal',  # Ordre des éléments de la légende
                font=dict(size=14),  # Taille de la police de la légende
                bgcolor='rgba(215, 285, 255, 0.5)',  # Couleur de fond de la légende
                bordercolor='red',  # Bordure de la légende
                borderwidth=2  # Largeur de la bordure de la légende
            )
        )
        col2.plotly_chart(fig2, use_container_width=True)
###################################################################
        st.title("Seuil d'approbation des PO")

        threshold_1_count = df['Threshold 1'].value_counts()
        fig_threshold_1 = px.bar(threshold_1_count, x=threshold_1_count.index, y=threshold_1_count.values,
                                title="Occurrences de 'Threshold 1'", labels={'x': 'Valeur', 'y': 'Nombre d\'occurrences'})
        fig_threshold_1.update_traces(
            text=threshold_1_count.values,
            textposition='outside',
            texttemplate='%{text}'
        )

        # Créer un graphique pour 'Threshold 2'
        threshold_2_count = df['Threshold 2'].value_counts()
        fig_threshold_2 = px.bar(threshold_2_count, x=threshold_2_count.index, y=threshold_2_count.values,
                                title="Occurrences de 'Threshold 2'", labels={'x': 'Valeur', 'y': 'Nombre d\'occurrences'})
        fig_threshold_2.update_traces(
            text=threshold_2_count.values,
            textposition='outside',
            texttemplate='%{text}'
        )

        # Créer un graphique pour 'Threshold 3'
        threshold_3_count = df['Threshold 3'].value_counts()
        fig_threshold_3 = px.bar(threshold_3_count, x=threshold_3_count.index, y=threshold_3_count.values,
                                title="Occurrences de 'Threshold 3'", labels={'x': 'Valeur', 'y': 'Nombre d\'occurrences'})
        fig_threshold_3.update_traces(
            text=threshold_3_count.values,
            textposition='outside',
            texttemplate='%{text}'
        )

        # Organiser les graphiques en 3 colonnes
        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(fig_threshold_1)

        with col2:
            st.plotly_chart(fig_threshold_2)

        with col3:
            st.plotly_chart(fig_threshold_3)
###################################################################
    st.title("Visualisation des Durées des Phases d'approbation")

    columns = [
        'PR-RFQ Entry Dt', 'PR-PO EDt', 'PO-RC EDt', 'RC-VCH EDt', 'VCH-PY EDt',
        'VCH/Inv Tran Dt to PY Entry Dt', 'PR-RC EDt', 'PR-Invoice/VCH Trans Date', 
        'PR-VCH EDt', 'PR-PY EDt', 'PO-VCH EDt', 'PO-PY EDt', 'PR TotApprv T', 
        'PO TotApprv T', 'VCH TotApprv T'
    ]

    # Affichage des statistiques pour chaque colonne
    for i in range(0, len(columns), 5):  # Diviser les colonnes en groupes de 5
        cols = columns[i:i + 5]  # Prendre un sous-ensemble de colonnes
        col1, col2, col3, col4, col5 = st.columns(5)  # Créer 5 colonnes dans Streamlit

        # Affichage des statistiques pour chaque colonne dans chaque colonne de Streamlit
        for j, col in enumerate(cols):
            with [col1, col2, col3, col4, col5][j]:
                st.subheader(col)
                st.write(f"Moyenne : {df[col].mean():.0f} jours")
                st.write(f"Maximale : {df[col].max():.0f} jours")
                st.write(f"Écart-type : {df[col].std():.0f} jours")
                st.write(f"Total : {df[col].sum():.0f} jours")
                st.write("---")
    ####
    # Créer un graphique global pour toutes les colonnes
    st.header("Moyenne des Durées de jours")

    # Calculer les moyennes pour chaque colonne
    averages = df[columns].mean()

    # Créer un graphique à barres des moyennes
    fig_avg = px.bar(averages, x=averages.index, y=averages.values)

    # Ajouter les valeurs sur chaque barre
    fig_avg.update_traces(
        text=averages.values,  # Afficher les valeurs des moyennes sur les barres
        textposition='outside',  # Placer les valeurs à l'extérieur des barres
        texttemplate='%{text:.1f}',  # Formater les valeurs avec 2 décimales
        showlegend=False  # Masquer la légende
    )

    fig_avg.update_layout(xaxis_title='-', yaxis_title='Moyenne en Jours')
    st.plotly_chart(fig_avg)

    # Calculer les totaux pour chaque colonne
    totals = df[columns].sum()

    # Créer un graphique à barres empilées des totaux
    st.header("Total des Durées de jours")

    fig_total = px.bar(totals, x=totals.index, y=totals.values, color=totals.index)

    # Ajouter les valeurs sur chaque barre
    fig_total.update_traces(
        text=totals.values,  # Afficher les valeurs sur les barres
        textposition='outside',  # Placer les valeurs à l'extérieur des barres
        texttemplate='%{text:.0f}',  # Formater les valeurs avec 0 décimales
        showlegend=True  # Masquer la légende
    )

    fig_total.update_layout(xaxis_title='Nombre des jours', yaxis_title='Total en Jours')
    st.plotly_chart(fig_total)
#####################################################
    # PR STATUS - Nombre de jours
    st.subheader("MOYENNE D'AGE")
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        display_metric("Moyenne Age PR", f"{int(df['PR Aging'].mean()):,} Jour.s".replace(",", " "), col1)
        display_metric("Moyenne Age PO", f"{int(df['PO Aging'].mean()):,} Jour.s".replace(",", " "), col2)
        display_metric("Moyenne Age RC", f"{int(df['RC Aging'].mean()):,} Jour.s".replace(",", " "), col3)
        display_metric("Moyenne Age VCH", f"{int(df['VCH Aging'].mean()):,} Jour.s".replace(",", " "), col4)
    
    
    st.markdown("<br>", unsafe_allow_html=True)  # Un saut de ligne
    st.divider()
    st.header("PROCUREMENT PERFORMANCES")
    
    # Fonction pour afficher un graphique encadré
    def display_chart_with_border(fig, title):
        st.markdown(
            f"""
            <div style="
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                ">
                <h4 style="text-align: center;">{title}</h4>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)

        # Graphique 1
        fig1 = px.bar(df, x='PR Appr-RFQ Entry Dt', y='PO Buyer', title="")
        with col1:
            display_chart_with_border(fig1, "Jours entre l'approbation de PR et la saisie de RFQ")

        # Graphique 2
        fig2 = px.bar(df, x='PR Appr-RC EDt', y='PO Buyer', title="")
        with col2:
            display_chart_with_border(fig2, "Jours entre l'approbation de PR et la saisie de RD")

    with st.container():
        col1, col2 = st.columns(2)

        # Graphique 3
        fig3 = px.bar(df, x='PR Appr-PO EDt', y='PO Buyer', title="")
        with col1:
            display_chart_with_border(fig3, "Jours entre l'approbation de PR et la création de PO")

        # Graphique 4
        fig4 = px.bar(df, x='PO Appr-RC EDt', y='PO Buyer', title="")
        with col2:
            display_chart_with_border(fig4, "Jours entre l'approbation de PO et RD EDt")

    ###UPDATE######
    # Fonction pour afficher un graphique encadré avec un titre centré
    def display_chart_with_border(fig, title):
        st.markdown(
            f"""
            <div style="
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                background-color:rgb(34, 242, 117);
            ">
                <h4 style="text-align: center;">{title}</h4>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("PROCUREMENT PERFORMANCES")
    with st.container():
        col1, col2 = st.columns(2)

        fig1 = px.bar(df, x='PR Appr-RFQ Entry Dt', y='PO Buyer')
        with col1:
            display_chart_with_border(fig1, "Jours entre l'approbation de PR et la saisie de RFQ")

        fig2 = px.bar(df, x='PR Appr-RC EDt', y='PO Buyer')
        with col2:
            display_chart_with_border(fig2, "Jours entre l'approbation de PR et la saisie de RD")

    with st.container():
        col1, col2 = st.columns(2)

        fig3 = px.bar(df, x='PR Appr-PO EDt', y='PO Buyer')
        with col1:
            display_chart_with_border(fig3, "Jours entre l'approbation de PR et la création de PO")

        fig4 = px.bar(df, x='PO Appr-RC EDt', y='PO Buyer')
        with col2:
            display_chart_with_border(fig4, "Jours entre l'approbation de PO et RD EDt")

    st.subheader("FINANCES PERFORMANCES")
    with st.container():
        col1, col2 = st.columns(2)

        fig5 = px.bar(df, x='RC-VCH EDt', y='Vch Data Entered By')
        with col1:
            display_chart_with_border(fig5, "Jours entre réception de Voucher et Vch Data Entrered")

        fig6 = px.bar(df, x='VCH Appr-PY EDt', y='Vch Data Entered By')
        with col2:
            display_chart_with_border(fig6, "Jours entre VCH Appr-PY EDt")

    st.subheader("APPROBATION ET RECEPTION PERFORMANCES")
    with st.container():
        col1, col2 = st.columns(2)

        fig7 = px.bar(df, x='PO TotApprv T', y='PO Last Approver')
        with col1:
            display_chart_with_border(fig7, "Jours entre l'approbation des PO")

        fig8 = px.bar(df, x='PR-RC EDt', y='Rcpt Data Entered By')
        with col2:
            display_chart_with_border(fig8, "Jours entre la réception des articles")

    #######FINUPDATE######
  
    #################################################

        # Calcul de la balance (quantité restante)
    df["Balance"] = df["Quantity Ordered"] - df["Quantity Received"]

    # Affichage du titre
    st.title("Suivi des Commandes")

    #################
    # Sélection de l'ID de la commande
    selected_requisition_id = st.selectbox("Sélectionnez un ID de commande ou le numero de la requisition :", [None] + list(df["Requisition ID"].unique()))

    # Vérification si un ID a été sélectionné
    if selected_requisition_id is not None:
        # Filtrage des données en fonction de l'ID sélectionné
        filtered_df = df[df["Requisition ID"] == selected_requisition_id]

        # Affichage des résultats
        st.subheader(f"Détails des articles pour la commande : {selected_requisition_id}")
        st.dataframe(filtered_df[["PR Item", "Quantity Ordered", "Quantity Received", "Balance"]])

        # Récupération des informations RFQ, PO No, et PO Aging (valeurs uniques pour la commande sélectionnée)
        rfq_id = filtered_df["RFQ ID"].iloc[0] if not filtered_df.empty else "N/A"
        po_no = filtered_df["PO No."].iloc[0] if not filtered_df.empty else "N/A"
        po_aging = filtered_df["PO Aging"].iloc[0] if not filtered_df.empty else "N/A"
        pr_aging = filtered_df["PR Aging"].iloc[0] if not filtered_df.empty else "N/A"
        vch_aging = filtered_df["VCH Aging"].iloc[0] if not filtered_df.empty else "N/A"
        rfq_aging = filtered_df["RC Aging"].iloc[0] if not filtered_df.empty else "N/A"

        # Traitement pour éviter les erreurs de conversion
        rfq_id = f"00000{int(rfq_id) if pd.notna(rfq_id) and rfq_id != 'N/A' else 0}"
        po_no = f"00000{int(po_no) if pd.notna(po_no) and po_no != 'N/A' else 0}"
        pr_aging = f"{int(pr_aging) if pd.notna(pr_aging) and pr_aging != 'N/A' else 0} jours"
        po_aging = f"{int(po_aging) if pd.notna(po_aging) and po_aging != 'N/A' else 0} jours"
        rfq_aging = f"{int(rfq_aging) if pd.notna(rfq_aging) and rfq_aging != 'N/A' else 0} jours"
        vch_aging = f"{int(vch_aging) if pd.notna(vch_aging) and vch_aging != 'N/A' else 0} jours"

        # Créer 5 colonnes
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        # Affichage des valeurs dans les colonnes
        col1.metric("RFQ ID", rfq_id)
        col2.metric("PO No", po_no)
        col3.metric("PR Aging", pr_aging)
        col4.metric("PO Aging", po_aging)
        col5.metric("RFQ Aging", rfq_aging)
        col6.metric("VCH Aging", vch_aging)
    else:
        st.warning("Veuillez sélectionner un ID de commande.")

