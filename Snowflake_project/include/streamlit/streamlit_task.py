import streamlit as st
from snowflake.snowpark import Session

# Get the current credentials
session = Session.builder.configs(
    st.secrets["snowflake"]
).create()
databases = session.sql("SHOW DATABASES").collect()
db_names = [db["name"] for db in databases]

# Create "confirm" value to flag true/false state of pressed button "Execute SQL"
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

# Refresh logic for the button "Refresh SQL"
def refresh_button():
    st.session_state.target_db = ""
    st.session_state.source_db = db_names[0]
    st.session_state.owner_role = "ACCOUNTADMIN"
    st.session_state.confirmed = False

# Create variables
st.title("❄️ Snowflake DB Clone Tool")
target_db = st.text_input("Target DB name", placeholder="YOUR_DB_NAME_WITH_YOUR_NAME", key="target_db")
source_db = st.selectbox("Clone from DB",db_names, key="source_db")
owner_role = st.selectbox("Owner role", ["ACCOUNTADMIN", "PUBLIC", "DEVELOPMENT"], key="owner_role")

# Need to specify read only status for below roles, otherwise empty
if owner_role in ["PUBLIC", "DEVELOPMENT"]:
    read_only_role = "read_only_role"
else:
    read_only_role = ""
read_only_role = st.text_input("Read-only role", value=read_only_role)

# Refresh button empty fields
st.button("Refresh SQL", icon=":material/refresh:", on_click=refresh_button)
    
st.write("Generated SQL")
st.write("Please, always check db names you set up!")

new_database = session.sql("SHOW DATABASES").to_pandas()
st.dataframe(new_database)

# Create the Execute SQL button to DB Clone
if st.button("🚀 Execute SQL"):

    # First click
    if target_db.upper() in [db.upper() for db in db_names] and not st.session_state.confirmed:
        st.warning(
            f"Database '{target_db}' already exists (owner: {owner_role})."
            "It will be dropped and recreated if you proceed."
        )
        st.session_state.confirmed = True

    # Second click
    else:        
        st.success("Executing DB ...")

        session.sql(f"DROP DATABASE IF EXISTS {target_db};").collect()
        session.sql(f"CREATE DATABASE {target_db} CLONE {source_db};").collect()        
        
        if read_only_role:
            session.sql(f"GRANT USAGE ON DATABASE {target_db} TO ROLE {owner_role};").collect()
            session.sql(f"GRANT USAGE ON ALL SCHEMAS IN DATABASE {target_db} TO ROLE {owner_role};").collect()
            session.sql(f"GRANT USAGE ON ALL TABLES IN DATABASE {target_db} TO ROLE {owner_role};").collect()
            session.sql(f"GRANT SELECT ON ALL TABLES IN DATABASE {target_db} TO ROLE {owner_role};").collect()
        else:
            session.sql(f"GRANT OWNERSHIP ON DATABASE {target_db} TO ROLE {owner_role} COPY CURRENT GRANTS;").collect()
        st.success(f"Database {target_db} created successfully.")

        st.session_state.confirmed = False


