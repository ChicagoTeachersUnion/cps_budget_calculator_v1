# Simple position loss app 
# Dataset created by Pavlyn Jankov (Director of Research, CTU)

import streamlit as st
import pandas as pd
import io
import base64

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None


def format_district_label(value):
    if value is None:
        return ""

    try:
        numeric_value = float(value)
        if numeric_value.is_integer():
            return str(int(numeric_value))
    except (TypeError, ValueError):
        pass

    return str(value)


def normalize_district_option(value):
    try:
        numeric_value = float(value)
        if numeric_value.is_integer():
            return int(numeric_value)
    except (TypeError, ValueError):
        pass

    return value

# Streamlit app title
def main():

    # Load data

    df = load_data()
    if df is None:
        return

    download_date = pd.Timestamp.now().strftime('%Y-%m-%d')

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

<b>State legislators have a choice to prevent this loss and add {df["Positions 100%"].sum()-abs(df["Projected Core Teacher Position Loss"].sum()):,.0f} teacher positions</b> by supporting state legislation (HB5409 and SB3701) to fully fund Illinois' Evidence-Based Funding (EBF) formula for K-12 schools. We can fund EBF by taxing billionaire wealth and Illinois' richest corproations and residents. 

We created this tool to help advocacy for State funding to stop CPS's proposed cuts. 

Look up your State legislative district, Chicago school board district, or your school to see how many teacher positions could be lost with CPS's proposed budget and how many positions a fully funded EBF formula could create.
</p>""", unsafe_allow_html=True)
    st.markdown("<h2>Select a District or School</h2>", unsafe_allow_html=True)

    # Select a district

    rep_list = sorted(normalize_district_option(x) for x in df["Rep"].dropna().unique())
    sen_list = sorted(normalize_district_option(x) for x in df["Senate"].dropna().unique())
    ersb_list = ersb_list = sorted(df["ERSB"].dropna().unique().tolist())
    school_list = sorted(df["School Name"].dropna().unique().tolist())

    grouped_rep = df.groupby("Rep")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_sen = df.groupby("Senate")["Projected Core Teacher Position Loss"].sum().reset_index()
    grouped_ersb = df.groupby("ERSB")["Projected Core Teacher Position Loss"].sum().reset_index()


#    select_by = st.radio("Select by:", ("State Representative or District", "State Senator District", "Chicago School Board District", "School"))
#   Removing School Board and School
    select_by = st.radio("Select by:", ("State Representative District", "State Senator District"))

    html_district_label = "District"

    if select_by == "State Representative District":
        rep = st.selectbox("Select Illinois State Representative District:", options=rep_list,index=None, placeholder="Select a district")
        district = rep
        if rep is not None:
            df = df[df["Rep"].isin([rep])]
        text_loss = "How will CPS's budget impact State Representative District "
        text_ebf = "What if schools in State Representative District "
        text_table = "Data for State Representative District "
        html_district_label = "State Representative District"
    elif select_by == "State Senator District":
        sen = st.selectbox("Select Illinois State Senator District:", options=sen_list,index=None, placeholder="Select a district")
        district = sen
        if sen is not None:
            df = df[df["Senate"].isin([sen])]
        text_loss = "How will CPS's budget impact State Senator District "
        text_ebf = "What if schools in State Senator District "
        text_table = "Data for State Senator District "
        html_district_label = "State Senator District"
    elif select_by == "Chicago School Board District":
        ersb = st.selectbox("Select Chicago Chicago School Board District:", options=ersb_list,index=None, placeholder="Select a district")
        district = ersb
        if ersb is not None:
            df = df[df["ERSB"].isin([ersb])]
        text_loss = "How will CPS's budget impact Chicago School Board District "
        text_ebf = "What if schools in Chicago School Board District "
        text_table = "Data for Chicago School Board District "
    elif select_by == "School":
        school = st.selectbox("Select School:", options=school_list,index=None, placeholder="Select a school")
        district = school
        if school is not None:
            df = df[df["School Name"].isin([school])]

    district_label = format_district_label(district) if district is not None else None

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
    <h4 style="margin-bottom:0.25rem;">{text_loss} {district_label}?</h4>
    <p style="margin-top:0; margin-bottom:0.75rem;">
    {abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))} district-provided teacher positions will be lost.<br><br>
    {schools_losing_positions} of the {total_schools} schools will lose district-provided teacher positions.
    </p>
    <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">{text_ebf} {district_label} were fully funded?</h4>
    <p style="margin-top:0;">
    No positions would be lost and there could be {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
    </p>
    """, unsafe_allow_html=True)

    if select_by == "School" and district is not None and sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0) < 0:
            
            st.markdown(f"""
        <h4 style="margin-bottom:0.25rem;">How will CPS's budget impact {district_label}?</h4>
        <p style="margin-top:0; margin-bottom:0.75rem;">
        {district_label} will lose {abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))} district-provided teacher positions.
        </p>
        <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">How will a fully funded EBF impact {district_label}?</h4>
        <p style="margin-top:0;">
        No positions would be lost and there could be {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
        </p>""", unsafe_allow_html=True)

    if select_by == "School" and district is not None and sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0) >= 0:
            
            st.markdown(f"""
        <h4 style="margin-bottom:0.25rem;">How will CPS's budget impact {district_label}?</h4>
        <p style="margin-top:0; margin-bottom:0.75rem;">
        {district_label} will fortunately not lose any district-provided teacher positions.
        </p>
        <h4 style="margin-top:0.5rem; margin-bottom:0.25rem;">How will a fully funded EBF impact {district_label}?</h4>
        <p style="margin-top:0;">
        While no positions will be lost, a fully funded EBF would bring {str(int(df_ebf["Positions 100%"].sum())-abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0)))} <b>additional</b> positions.
        </p>""", unsafe_allow_html=True)

    if 'table_button' not in st.session_state:
        st.session_state.table_button = False
    
    def click_table_button():
        st.session_state.table_button = not st.session_state.table_button

    st.markdown("""<p><b>Want to see the school-level data?</b></p>""",unsafe_allow_html=True)
    st.button('Click here', on_click=click_table_button,key="data_button")

    if st.session_state.table_button:
        if district is None:
            st.markdown(f"""
    <p style="margin-top:0; margin-bottom:0.75rem;"><i><span style="color:#878787;">Select a district or school to see table.</span></i></p>
    """, unsafe_allow_html=True)
        elif district is not None and select_by == "School":
            st.markdown(f"""<h4>Data for All Schools</h2>""",unsafe_allow_html=True)
            st.dataframe(df_all_schools,hide_index=True)

        elif district is not None and select_by != "School":
            st.markdown(f"""<h4>{text_table} {district_label}</h2>""",unsafe_allow_html=True)
            st.dataframe(df_selected_schools,hide_index=True)

    if district is not None:
        # Make download button to download html
        with open("ctu_logo.png", "rb") as logo_file:
            logo_data_uri = "data:image/png;base64," + base64.b64encode(logo_file.read()).decode("utf-8")

        district_funded_loss = abs(sum(x for x in df['Projected Core Teacher Position Loss'] if x < 0))
        additional_positions_ebf = int(df_ebf["Positions 100%"].sum())-district_funded_loss
        html_district_display = f"{html_district_label} {district_label}"

        html_one_pager = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Fully Fund Schools One-Pager</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap" rel="stylesheet">
    <style>
        @page {
            size: 8.5in 11in;
            margin: 0.4in;
        }

        :root {
            --ink: #14213d;
            --accent: #c1121f;
            --bg: #f8f9fb;
            --muted: #4a5568;
        }

        html,
        body {
            margin: 0;
            padding: 0;
            background: var(--bg);
            color: var(--ink);
            font-family: 'Open Sans', 'Segoe UI', Tahoma, Arial, sans-serif;
            line-height: 1.45;
        }

        .page {
            box-sizing: border-box;
            width: 100%;
            min-height: auto;
            margin: 0 auto;
            padding: 0.5in;
            background: #ffffff;
            border: 1px solid #dfe3ea;
            display: flex;
            flex-direction: column;
        }

        .header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 0.3in;
        }

        .logo-box {
            width: 1.2in;
            height: 1.2in;
            display: flex;
            align-items: center;
            justify-content: center;
            flex: 0 0 auto;
        }

        .brand-logo {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .header-title {
            margin: 0;
            text-align: center;
            color: var(--accent);
            font-size: 30px;
            line-height: 1.1;
            letter-spacing: 0.2px;
            flex: 1;
            min-height: 1.2in;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        h1 {
            margin: 0 0 0.3in;
            font-size: 30px;
            line-height: 1.1;
            color: var(--accent);
            letter-spacing: 0.2px;
        }

        .lede {
            margin: 0 0 0.28in;
            font-size: 20px;
            font-weight: 700;
        }

        .sub-head {
            display: block;
            font-size: 15px;
            font-weight: bold;
            text-align: center;
        }

        p {
            margin: 0 0 0.16in;
            font-size: 16px;
        }

        .highlight {
            font-weight: 700;
            color: var(--accent);
        }

        .callout {
            margin-top: 0.32in;
            padding: 0.1in 0.22in;
            border-left: 6px solid var(--accent);
            background: #fff3f3;
            font-size: 18px;
            font-weight: 700;
        }

        .footer {
            margin-top: auto;
            padding-top: 0.35in;
            font-size: 13px;
            color: var(--muted);
            letter-spacing: 0.2px;
            text-transform: uppercase;
        }

        @media screen and (max-width: 900px) {
            .page {
                width: auto;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                border: none;
            }

            h1 {
                font-size: 28px;
            }

            .header-row {
                align-items: center;
            }

            .logo-box {
                width: 0.95in;
                height: 0.95in;
            }

            .header-title {
                font-size: 24px;
                min-height: 0.95in;
            }

            .lede {
                font-size: 18px;
            }

            p {
                font-size: 14px;
            }
        }

        @media print {
            html,
            body {
                background: #ffffff;
            }

            .page {
                border: none;
                padding: 0;
                margin: 0;
                width: auto;
            }
        }
    </style>
</head>
<body>
    <main class="page">
        <div class="header-row">
            <div class="logo-box">
                <img class="brand-logo" src="__LOGO_DATA_URI__" alt="Organization logo">
            </div>
            <h1 class="header-title">Fully Fund Illinois Schools,<br>Stop CPS Cuts</h1>
        </div>

        <p class="lede">If Illinois fully funded schools, we'd have a $1 billion surplus.</p>
        <p>Instead, we are facing cuts in Chicago Public Schools again. You have a choice to fulfill Illinois' promise to fully fund schools and prevent cuts.</p>
        <p class="callout">We need your support on HB5409 and SB3701 to fully fund schools in Illinois.</p>

        <p><span class="sub-head">Context</span></p>
        <p>CPS is facing a <span class="highlight">$732 million deficit</span>. The district is proposing to close the deficit by increasing class size and cutting staff positions, such as custodial staff, interventionists, bilingual coordinators, and assistant principals.</p>
        <p>Our estimates show that CPS will lose over <span class="highlight">800 district-funded teacher positions</span> alone.</p>

        <p><span class="sub-head">Your district</span></p>
        <p>__HTML_DISTRICT_DISPLAY__ stands to lose <span class="highlight">__DISTRICT_FUNDED_LOSS__ district-funded teacher positions</span> in addition to these other cuts. <span class="highlight">18 out of 20 schools</span> in your district will lose positions.</p>
        <p>If Illinois keeps its promise to fully fund schools, your district could avoid these cuts and have <span class="highlight">__ADDITIONAL_POSITIONS_EBF__ more much-needed positions</span>. CPS could increase its staff by over 8 thousand positions.</p>

        <p><span class="sub-head">Our ask</span></p>
        <p>You have the choice to prevent these cuts and grow much-needed teacher and staff positions in CPS.</p>
        <p class="callout">Fulfill Illinois' promise to fully fund schools by supporting HB5409 and SB3701.</p>

        <footer class="footer">Chicago Teachers Union Research Department, Download date: __DOWNLOAD_DATE__</footer>
    </main>
</body>
</html>
"""

        html_one_pager = html_one_pager.replace("__LOGO_DATA_URI__", logo_data_uri)
        html_one_pager = html_one_pager.replace("__HTML_DISTRICT_DISPLAY__", html_district_display)
        html_one_pager = html_one_pager.replace("__DISTRICT_FUNDED_LOSS__", f"{district_funded_loss:,}")
        html_one_pager = html_one_pager.replace("__ADDITIONAL_POSITIONS_EBF__", f"{additional_positions_ebf:,}")
        html_one_pager = html_one_pager.replace("__DOWNLOAD_DATE__", download_date)

        safe_district = district_label.replace(" ", "_")
        # if State Senator District selected then safe_district = "State_Senator_District_" + safe_district
        # if State Representative District selected then safe_district = "State_Representative_District_" + safe_district
        if select_by == "State Senator District":
            safe_district = "State_Senate_District_" + safe_district
        elif select_by == "State Representative District":
            safe_district = "State_Representative_District_" + safe_district
        st.download_button(
            label="Download One-Pager",
            data=html_one_pager,
            file_name=f"one_pager_{safe_district}_{download_date}.html",
            mime="text/html",
            icon=":material/download:"
        )

    if 'button' not in st.session_state:
        st.session_state.button = False

    def click_button():
        st.session_state.button = not st.session_state.button

    st.markdown("""<p><b>Interested in so more context and to learn about our data?</b></p>""",unsafe_allow_html=True)
    st.button('Click here', on_click=click_button,key="context_button")

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
        file_name=f"data_dowloaded_{download_date}.xlsx",
        mime="application/vnd.ms-excel",
        icon=":material/download:"
    )

if __name__ == "__main__":
    main()
    
