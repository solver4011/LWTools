import streamlit as st
import pandas as pd

st.set_page_config(
    page_title='LostWord Tools',
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.header("Use")
    st.caption("Calculates a relative damage index gauging an attack's strength")
    st.header("Usage")
    st.caption("Fill in the table below")

data = [
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    },
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    },
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    },
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    },
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    },
    {
        '# Bullets': 0,
        'Power': 0.0,
        '% Card': 0.0,
        'Eff/Neu/Res': "Eff",
        '% Slice': 0.0,
        '% Hard': 0.0,
        'Killer Hit (Y/N)': "N",
        'Yin/Yang': "Yang"
    }
]

df = pd.DataFrame(data)
df.index.name = "Bullet Line"

stats = st.data_editor(df)

with st.expander("Character Stats"):
    eff_dmg = st.number_input(label="% Damage to Effective", value=0)
    res_dmg = st.number_input(label="% Damage to Resist", value=0)
    yinatk = st.number_input(label="Yin ATK", value=0)
    yangatk = st.number_input(label="Yang ATK", value=0)
    agi = st.number_input(label="Agility", value=0)
    yindef = st.number_input(label="Yin DEF", value=0)
    yangdef = st.number_input(label="Yang DEF", value=0)

with st.expander("Miscellaneous"):
    rebirth = st.checkbox(label="Rebirth?", value=False)
    yinatkb = st.slider(label="Yin ATK Buffs", min_value=-10, max_value=10, value=10)
    yinatkii = st.slider(label="Yin ATK II Buffs", min_value=-10, max_value=10, value=0)
    yangatkb = st.slider(label="Yang ATK Buffs", min_value=-10, max_value=10, value=10)
    yangatkii = st.slider(label="Yang ATK II Buffs", min_value=-10, max_value=10, value=0)
    agib = st.slider(label="Agility Buffs", min_value=-10, max_value=10, value=10)
    agiii = st.slider(label="Agility II Buffs", min_value=-10, max_value=10, value=0)
    yindefb = st.slider(label="Yin DEF Buffs", min_value=-10, max_value=10, value=10)
    yindefii = st.slider(label="Yin DEF II Buffs", min_value=-10, max_value=10, value=0)
    yangdefb = st.slider(label="Yang DEF Buffs", min_value=-10, max_value=10, value=10)
    yangdefii = st.slider(label="Yang DEF II Buffs", min_value=-10, max_value=10, value=0)
    critatkb = st.slider(label="CRIT ATK Buffs", min_value=-10, max_value=10, value=10)
    # critatkii = st.slider(label="CRIT ATK II Buffs", min_value=-10, max_value=10, value=0) # Not entirely sure how this works yet

# Get the multiplier for a certain buff count
def mult(num):
    if num < 0:
        return 1 / (1 + 0.3 * num)
    else:
        return 1 + 0.3 * num

def calc_line(line):
    effresneu = 0.5 * (1 + res_dmg / 100)
    if line["Eff/Neu/Res"] == "Neu":
        effresneu = 1.0
    if line["Eff/Neu/Res"] == "Eff":
        effresneu = 2.0 * (1 + eff_dmg / 100)
    
    killer = 1.0
    if line["Killer Hit (Y/N)"] == "Y":
        killer = 1.0 + mult(critatkb)

    cur_agi = agi * mult(agiii) / 4 * mult(agib)
    cur_yinatk = yinatk * mult(yinatkb) / 4 * mult(yinatkii)
    cur_yangatk = yangatk * mult(yangatkb) / 4 * mult(yangatkii)
    cur_yindef = yindef * mult(yindefb) / 4 * mult(yindefii)
    cur_yangdef = yangdef * mult(yangdefb) / 4 * mult(yangdefii)

    line_stat = line['% Slice'] / 100 * cur_agi + line['% Hard'] / 100 * cur_yangdef + cur_yangatk
    if line['Yin/Yang'] == "Yin":
        line_stat = line['% Slice'] / 100 * cur_agi + line['% Hard'] / 100 * cur_yindef + cur_yinatk

    level = 1
    if rebirth:
        level = 1.4

    return level * line["# Bullets"] * line["Power"] * (1 + line["% Card"] / 100) * effresneu * killer * line_stat / 1000

if st.button('Submit Query'):
    total_dmg = 0.0

    for i in range(6):
        total_dmg += calc_line(stats.iloc[i])

    st.success(f"Damage Index: {round(total_dmg, 2)}")