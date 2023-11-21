import streamlit as st
import requests
import bs4
import re

#### APP FORMATTING ####
st.set_page_config(
    page_title='LostWord Tools',
    layout="wide",
    initial_sidebar_state="expanded"
)

query = st.text_area("Killers")

with st.sidebar:
    st.title("About")
    st.caption("More tools maybe coming soon™")
    st.header("Use")
    st.caption("Fetches all units hit by a certain set of killers.")
    st.header("Usage")
    st.caption("Enter each killer name in a separate line. Uppercase/lowercase doesn't matter, just make sure the killer name exactly matches the in-game name.")

if st.button('Submit Query'):
    if len(query) == 0:
        e = RuntimeError('Type a non-zero number of killers before submitting a query.')
        st.exception(e)

    killers = query.strip().split("\n")

    killers_hit = set()
    for i in killers:
        # Try to scrape lostwordchronicle for killer data
        try:
            # Format killer name as a page name
            name = i.strip().replace(" ", "_").title()

            # Certain words should be lowercase
            LOWERCASE = ["No", "Of", "The"]

            for should_lowercase in LOWERCASE:
                name = name.replace(f"_{should_lowercase}_", f"_{should_lowercase.lower()}_")

            # Query page
            page = f"http://lostwordchronicle.com/character_tag/{name}"
            tag_data = bs4.BeautifulSoup(requests.get(page).text, 'html.parser').get_text()

            # Parse data
            SKIP_NUM = 15
            start_idx = tag_data.find("Members") + SKIP_NUM
            end_idx = tag_data.find("Killers")
            assert start_idx <= end_idx, f"Error with scraping data from ({name})"

            tag_data = tag_data[start_idx : end_idx]
            tag_data = re.split("\n\n\n\n\n\n", tag_data)

            # Get rid of space before all units' names
            for idx in range(len(tag_data)):
                tag_data[idx] = tag_data[idx].strip()

            killer_set = set(tag_data)

            # Update killers hit set
            killers_hit = killers_hit | killer_set
        except requests.exceptions.RequestException as e:
            # Throw error if page not found
            raise RuntimeError(f"Killer {i} was not found")

    # Remove empty string from killer set
    killers_hit.remove("")

    # Print calculated answer
    st.success(f"{len(killers_hit)} units hit by set of killers provided.")
    with st.expander("List of Units Hit by Killers"):
        output = ", ".join(killers_hit)

        st.success(output)
