# Simple position loss app 
# Dataset created by Pavlyn Jankov (Director of Research, CTU)

import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        df  = df[df["Rep"].notna()]
        df["Rep"] = df["Rep"].astype(int)
        df["Senate"] = df["Senate"].astype(int)
        df["ERSB"] = df["ERSB"]
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None

# Streamlit app title
def main():

    # Load data

    df = load_data()
    if df is None:
        return

    # Set page configuration

    st.set_page_config(
        page_title="CPS Position Loss Lookup", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # App title

    st.markdown("<h1>CPS Position Loss Lookup</h1>", unsafe_allow_html=True)
    st.markdown(f"""<p>
CPS recently sent its district funded budget to principals. This year, CPS has increased it's student teacher ratio. This means a loss of {abs(df["Projected Core Teacher Position Loss"].sum())} core teaching positions across CPS schools. 

<b>State legislators have a choice to stop this. If they increase funding to EBF they can help stop these cuts</b>.

See more about EBF and how we can use it to fully fund out schools here. LINK

Look up your State legislative district, Chicago school board district, or school to see how many positions will be lost with CPS's and how EBF funding could help prevent this.

</p>""", unsafe_allow_html=True)

    st.markdown("<h2>Select a District or School</h2>", unsafe_allow_html=True)

    # Select a district

    rep_list = df["Rep"].unique()
    rep_list.sort()
    sen_list = df["Senate"].unique()
    sen_list.sort()
    ersb_list = ersb_list = sorted(df["ERSB"].dropna().unique().tolist())
    school_list = df["School Name"].unique()
    school_list.sort()

    grouped_rep = df.groupby("Rep")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_sen = df.groupby("Senate")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_ersb = df.groupby("ERSB")["Projected Core Teacher Position Loss"].sum().reset_index()


    select_by = st.radio("Select by:", ("State Representative District", "State Senator District", "Chicago School Board District", "School"))

    if select_by == "State Representative District":
        rep = st.selectbox("Select Illinois State Representative District:", options=rep_list,index=None, placeholder="Select a district")
        district = rep
        if rep is not None:
            df = df[df["Rep"].isin([rep])]
        text_loss = "How will CPS's Budget will Impact State Representive District "
        text_ebf = "What if schools in State Representive District "
    elif select_by == "State Senator District":
        sen = st.selectbox("Select Illinois State Senator District:", options=sen_list,index=None, placeholder="Select a district")
        district = sen
        if sen is not None:
            df = df[df["Senate"].isin([sen])]
        text_loss = "How will CPS's Budget will Impact State Senate District "
        text_ebf = "What if schools in State Senate District "
    elif select_by == "Chicago School Board District":
        ersb = st.selectbox("Select Chicago Chicago School Board District:", options=ersb_list,index=None, placeholder="Select a district")
        district = ersb
        if ersb is not None:
            df = df[df["ERSB"].isin([ersb])]
        text_loss = "How will CPS's Budget will Impact Chicago School Board District "
        text_ebf = "What if schools in Chicago School Board District "
    elif select_by == "School":
        school = st.selectbox("Select School:", options=school_list,index=None, placeholder="Select a school")
        district = school
        if school is not None:
            df = df[df["School Name"].isin([school])]


    df_ebf = df.copy()

    df = df[["School Name", "Projected Core Teacher Position Loss"]]

    if district is None:

        st.markdown(f"""
    <h4 style="margin-bottom:0.25rem;">How will CPS's Budget impact your district or school?</h4>
    <p style="margin-top:0; margin-bottom:0.75rem;"><i><span style="color:#878787;">Select a district or school to see CPS's budget impact on positions.</span></i></p>
    <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">How will a fully funded EBF impact your district or school?</h4>
    <p style="margin-top:0;"><i><span style="color:#878787;">Select a district or school to see what additional positions if your legislator increases EBF funding.</span></i></p>
    """, unsafe_allow_html=True)

    if select_by != "School" and district is not None:

        schools_losing_positions = sum(1 for x in df['Projected Core Teacher Position Loss'] if x < 0)
        total_schools = len(df['Projected Core Teacher Position Loss'])

        st.markdown(f"""
    <h4 style="margin-bottom:0.25rem;">{text_loss} {district}?</h4>
    <p style="margin-top:0; margin-bottom:0.75rem;">
    {abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))} core teacher positions will be lost.<br><br>
    {schools_losing_positions} of the {total_schools} schools will lose core teacher positions.
    </p>
    <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">{text_ebf} {district} were fully funded?</h4>
    <p style="margin-top:0;">
    No positions would be lost and there could be {str(int(df_ebf["Positions"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
    </p>
    """, unsafe_allow_html=True)

    if select_by == "School" and district is not None:

        st.markdown(f"""
        
<h3>

{district} will lose {df["Projected Core Teacher Position Loss"].values[0]} positions
</h3>.""", unsafe_allow_html=True)

    if 'button' not in st.session_state:
        st.session_state.button = False

    def click_button():
        st.session_state.button = not st.session_state.button

    st.button('Click here to learn more about how the budget process and our data', on_click=click_button)

    if st.session_state.button:
        st.markdown(f"""
    <p style="margin-top:0; margin-bottom:0.75rem;">TEXT ABOUT CALCULATIONS</p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
    
