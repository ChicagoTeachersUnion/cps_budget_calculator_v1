# Simple position loss app 
# Dataset created by Pavlyn Jankov (Director of Research, CTU)

import streamlit as st
import pandas as pd
import io

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

    df_download = df.copy()

    df_all_schools = df.copy()

    df_all_schools = df_all_schools[["School Name","Projected Core Teacher Position Loss","100% Funding","Positions 100%"]]
    df_all_schools.columns = ["School Name","Projected District-Funded Teacher Position Loss","Additional Revenue with 100% EBF Funding","Additional Positions with 100% EBF Funding"]

    # Set page configuration

    st.set_page_config(
        page_title="CPS Teacher Loss Lookup", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # App title

    st.markdown("""
<h1 style="padding-bottom:0.2rem;">CPS Teacher Loss Lookup</h1>
<h2 style="padding-top:0;">According to CPS's Proposed 2026-2027 Budget</h2>
""", unsafe_allow_html=True)
    st.markdown(f"""<p>
Chicago Public Schools' (CPS's) proposed budget could lead to a loss of {abs(df["Projected Core Teacher Position Loss"].sum()):,.0f} district-funded teacher positions.

<b>State legislators have a choice to prevent this loss and add {df["Positions 100%"].sum()-abs(df["Projected Core Teacher Position Loss"].sum()):,.0f} teacher positions</b> by supporting state legislation (HB5409 and SB3701) to fully fund Illinois' Evidence-Based Funding (EBF) formula for K-12 schools. We can fund EBF by [taxing billionaire wealth and Illinois' richest corproations and residents](https://www.illinoisrevenuealliance.org/advocacy/). 

We created this tool to help advocacy for State funding to stop CPS's proposed cuts. 

Look up your State legislative district, Chicago school board district, or your school to see how many teacher positions could be lost with CPS's proposed budget and how many positions a fully funded EBF formula could create.
</p>""", unsafe_allow_html=True)
    st.markdown("<h2>Select a District or School</h2>", unsafe_allow_html=True)

    # Select a district

    rep_list = df["Rep"].unique()
    rep_list.sort()
    sen_list = df["Senate"].unique()
    sen_list.sort()
    ersb_list = ersb_list = sorted(df["ERSB"].dropna().unique().tolist())
    school_list = sorted(df["School Name"].dropna().unique().tolist())

    grouped_rep = df.groupby("Rep")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_sen = df.groupby("Senate")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_ersb = df.groupby("ERSB")["Projected Core Teacher Position Loss"].sum().reset_index()


    select_by = st.radio("Select by:", ("State Representative District", "State Senator District", "Chicago School Board District", "School"))

    if select_by == "State Representative District":
        rep = st.selectbox("Select Illinois State Representative District:", options=rep_list,index=None, placeholder="Select a district")
        district = rep
        if rep is not None:
            df = df[df["Rep"].isin([rep])]
        text_loss = "How will CPS's budget impact State Representive District "
        text_ebf = "What if schools in State Representive District "
        text_table = "Data for State Representive District "
    elif select_by == "State Senator District":
        sen = st.selectbox("Select Illinois State Senator District:", options=sen_list,index=None, placeholder="Select a district")
        district = sen
        if sen is not None:
            df = df[df["Senate"].isin([sen])]
        text_loss = "How will CPS's budget impact State Senate District "
        text_ebf = "What if schools in State Senate District "
        text_table = "Data for State Senate District "
    elif select_by == "Chicago School Board District":
        ersb = st.selectbox("Select Chicago Chicago School Board District:", options=ersb_list,index=None, placeholder="Select a district")
        district = ersb
        if ersb is not None:
            df = df[df["ERSB"].isin([ersb])]
        text_loss = "How will CPS's budget impact Chicago School Board District "
        text_ebf = "What if schools in Chicago School Board District "
        text_table = "Data for School Board District "
    elif select_by == "School":
        school = st.selectbox("Select School:", options=school_list,index=None, placeholder="Select a school")
        district = school
        if school is not None:
            df = df[df["School Name"].isin([school])]

    df_ebf = df.copy()

    # table for look up

    df_selected_schools = df.copy()

    df_selected_schools = df_selected_schools[["School Name","Projected Core Teacher Position Loss","100% Funding","Positions 100%"]]
    df_selected_schools.columns = ["School Name","Projected District-Funded Teacher Position Loss","Additional Revenue with 100% EBF Funding","Additional Positions with 100% EBF Funding"]

    df = df[["School Name", "Projected Core Teacher Position Loss"]]

    if district is None:

        st.markdown(f"""
    <h4 style="margin-bottom:0.25rem;">How will CPS's budget impact your district or school?</h4>
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
    {abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))} district-provided teacher positions will be lost.<br><br>
    {schools_losing_positions} of the {total_schools} schools will lose district-provided teacher positions.
    </p>
    <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">{text_ebf} {district} were fully funded?</h4>
    <p style="margin-top:0;">
    No positions would be lost and there could be {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
    </p>
    """, unsafe_allow_html=True)

    if select_by == "School" and district is not None and sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0) < 0:
            
            st.markdown(f"""
        <h4 style="margin-bottom:0.25rem;">How will CPS's budget impact {district}?</h4>
        <p style="margin-top:0; margin-bottom:0.75rem;">
        {district} will lose {abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))} district-provided teacher positions.
        </p>
        <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">How will a fully funded EBF impact {district}?</h4>
        <p style="margin-top:0;">
        No positions would be lost and there could be {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
        </p>""", unsafe_allow_html=True)

    if select_by == "School" and district is not None and sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0) >= 0:
            
            st.markdown(f"""
        <h4 style="margin-bottom:0.25rem;">How will CPS's budget impact {district}?</h4>
        <p style="margin-top:0; margin-bottom:0.75rem;">
        {district} will fortunately not lose any district-provided teacher positions.
        </p>
        <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">How will a fully funded EBF impact {district}?</h4>
        <p style="margin-top:0;">
        While no positions will be lost, a fully funded EBF would bring {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
        </p>""", unsafe_allow_html=True)

    if 'table_button' not in st.session_state:
        st.session_state.table_button = False
    
    def click_table_button():
        st.session_state.table_button = not st.session_state.table_button

    st.button('Click here to see the school level data', on_click=click_table_button)

    if st.session_state.table_button:
        if district is None:
            st.markdown(f"""
    <p style="margin-top:0; margin-bottom:0.75rem;"><i><span style="color:#878787;">Select a district or school to see table.</span></i></p>
    """, unsafe_allow_html=True)
        elif district is not None and select_by == "School":
            st.markdown(f"""<h4>Data for All Schools</h2>""",unsafe_allow_html=True)
            st.dataframe(df_all_schools,hide_index=True)

        elif district is not None and select_by != "School":
            st.markdown(f"""<h4>{text_table} {district}</h2>""",unsafe_allow_html=True)
            st.dataframe(df_selected_schools,hide_index=True)

    if 'button' not in st.session_state:
        st.session_state.button = False

    def click_button():
        st.session_state.button = not st.session_state.button

    st.button('Click here for more context and to learn about our data', on_click=click_button)

    if st.session_state.button:
        st.markdown(f"""<p>

<b>Context</b>

Chicago Public Schools' (CPS) 2026–2027 budget includes cuts that will directly affect classrooms. CPS has a deficit of over $700 million. A deficit means that spending (on things like teachers and curriculum) is larger than revenue.

There are two ways to address a deficit: increase revenue or cut spending. CPS is choosing to cut spending by raising the student-to-teacher ratio it uses to fund schools. That means fewer teachers. According to the Chicago Teachers Union (CTU) Research Department, CPS's proposed budget could eliminate {abs(df_download["Projected Core Teacher Position Loss"].sum()):,.0f} district-funded teachers across CPS.

Another choice is possible. We can increase revenue from the State, but only if state leaders and our elected officials take action.

<b>State legislators have a choice to stop these CPS cuts by supporting state legislation (HB5409 and SB3701) to fully fund Illinois' Evidence-Based Funding (EBF) for K–12 schools.</b>

If passed, this funding could add about {df_download["Positions 100%"].sum()-abs(df_download["Projected Core Teacher Position Loss"].sum()):,.0f} more teacher positions while preventing the expected loss of {abs(df_download["Projected Core Teacher Position Loss"].sum()):,.0f} district-funded teachers.

<b>Data</b>

CTU's Research Department created a dataset with school-level projected teacher position losses and additional state funding and positions under a fully funded Evidence-Based Funding (EBF) formula.

The projected district-funded teacher position loss is the difference between the FY27 and FY26 student-to-teacher ratio formulas. The student-to-teacher ratios were provided in a CPS budget briefing (May 2026).

Evidence-Based Funding (EBF) revenue allocates the total EBF adequacy gap based on each school's share of CPS's FY26 budget that went to the classroom. EBF data is from the Illinois State Board of Education's EBF Distribution Calculation for FY26.

</p>""", unsafe_allow_html=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_download.to_excel(writer, index=False, sheet_name="Full Data Set")
        
    buffer.seek(0)

    st.download_button(
        label="Download Full Dataset",
        data=buffer,
        file_name=f"data_dowloaded_{pd.Timestamp.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.ms-excel",
        icon=":material/download:"
    )

if __name__ == "__main__":
    main()
    
