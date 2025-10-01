import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Scrape the LW of a character
def get_stats(eff_res_config, idx, char_name):
    NEUTRAL = '9' # Neutral bullets are denoted by 9
    ELEMENT_ID_TO_NAME = ["", "Sun", "Moon", "Fire", "Water", "Wood", "Metal", "Earth", "Star", "No Element"] # element indices to name

    if char_name.startswith("RE"):
        is_rebirth = True
        char_name = char_name[3:]
        x = BeautifulSoup(requests.get(f"http://lostwordchronicle.com/characters/rebirths/{char_name}").text, 'html.parser')
    else:
        is_rebirth = False
        x = BeautifulSoup(requests.get(f"http://lostwordchronicle.com/characters/{char_name}").text, 'html.parser')
    y = x.find_all("div", {"class": "d-inline-flex flex-column"})
    if len(y) == 5:
        # sometimes there are only 5 entries, sometimes there are 10
        idx //= 2
    y = y[idx]

    # First parse all elements
    eles = [str(y)[x] for x in [m.end() for m in re.finditer('bullet attribute-', str(y))]]
    
    # Convert elements into effective, resist, or neutral, using the effective/weakness configuration provided
    if eff_res_config == "Primary Effective, Resist Others" or eff_res_config == "Primary Effective, Neutral Others" or eff_res_config == "All Effective":
        # Get primary element
        primary_ele = NEUTRAL
        for i in eles:
            if i != NEUTRAL:
                primary_ele = i
                break
        if primary_ele == NEUTRAL:
            for idx in range(len(eles)):
                eles[idx] = "Neu"
        else:
            for idx in range(len(eles)):
                if eles[idx] == NEUTRAL:
                    eles[idx] = "Neu"
                elif eles[idx] == primary_ele:
                    eles[idx] = "Eff"
                else:
                    if eff_res_config == "Primary Effective, Resist Others":
                        eles[idx] = "Res"
                    elif eff_res_config == "Primary Effective, Neutral Others":
                        eles[idx] = "Neu"
                    else:
                        eles[idx] = "Eff"
    else:
        for idx in range(len(eles)):
            if eff_res_config == "All Neutral":
                eles[idx] = "Neu"
            else:
                # NO lines should still be neutral
                if eles[idx] == NEUTRAL:
                    eles[idx] = "Neu"
                else:
                    eles[idx] = "Res"

    element_info = [ELEMENT_ID_TO_NAME[int(str(y)[x])] for x in [m.end() for m in re.finditer('bullet attribute-', str(y))]] # Get the element names    

    # Parse yin/yang, 2 is yang and 1 is yin
    yinyang = [str(y)[x] for x in [m.end() for m in re.finditer('yin-yang-amount-', str(y))]]
    for idx, i in enumerate(yinyang):
        yinyang[idx] = 'Yin'
        if i == '1':
            yinyang[idx] = 'Yang'
            

    # Parse bullet numbers
    scraped_nums = y.find_all("h6")
    bulletnums = []
    for i in scraped_nums:
        if str(i).find("x") != -1:
            bulletnums.append(int(str(i)[5:-5]))

    # Parse bullet powers
    z = y.text.replace("\n", "")
    pwr_idx = [m.end() for m in re.finditer('PWR', z)]
    acc_idx = [m.start() for m in re.finditer('ACC', z)]
    bulletpows = []

    for i in range(6):
        bulletpows.append(float(z[pwr_idx[i] : acc_idx[i]]))

    # Parse scalings
    y_elems = [y_elem for y_elem in y]
    bulletlines = []
    for i in range(1, 13, 2):
        bulletlines.append(y_elems[i])

    # Parse slice
    slices = []

    for line in bulletlines:
        start_idx = [m.end() for m in re.finditer(re.escape('[Slice]: '), str(line))]
        end_idx = [m.start() for m in re.finditer('% Agility Scale', str(line))]
        slices.append(0)
        if len(start_idx) == 1 and len(end_idx) == 1:
            slices[-1] = int(str(line)[start_idx[0] : end_idx[0]])

    # Parse hard
    hards = []

    for line in bulletlines:
        start_idx = [m.end() for m in re.finditer(re.escape('[Hard]: '), str(line))]
        end_idx = [m.start() for m in re.finditer('% DEF Scale', str(line))]
        hards.append(0)
        if len(start_idx) == 1 and len(end_idx) == 1:
            hards[-1] = int(str(line)[start_idx[0] : end_idx[0]])
    
    # Get bullet types
    bullet_types = []
    for line in bulletlines:
        start_idx = [m.end() for m in re.finditer(re.escape('/bullet_tag/'), str(line))]
        end_idx = [m.start() for m in re.finditer(re.escape('.png'), str(line))]
        bullet_types.append(str(line)[start_idx[0] : end_idx[0]])

    # Combine bullet types and elemnt names in a readable way
    line_info = ""
    for i in range(6):
        line_info += f"{element_info[i]}/{bullet_types[i]}"
        if i != 5:
            line_info += ", "

    # Parse stats
    a = x.find_all("div", {"class": "stat-display-value"})
    yangatk = int(a[1].text)
    yangdef = int(a[2].text)
    agi = int(a[3].text)
    yinatk = int(a[4].text)
    yindef = int(a[5].text)

    # Finally, parse dmg to eff/res
    dmgres = 0
    dmgeff = 0

    y = x.find_all("div", {"class": "card-body"})[9]
    start_idx = [m.end() for m in re.finditer(re.escape('DMG to effective  elements: +'), y.text)]

    if len(start_idx) == 1:
        z = y.text[start_idx[0] : ]
        dmgeff = float(z[ : z.find("%")])
    
    start_idx = [m.end() for m in re.finditer(re.escape('DMG to resisted  elements: +'), y.text)]

    if len(start_idx) == 1:
        z = y.text[start_idx[0] : ]
        dmgres = float(z[ : z.find("%")])

    return eles, yinyang, bulletnums, bulletpows, slices, hards, yangatk, yangdef, agi, yinatk, yindef, dmgres, dmgeff, is_rebirth, line_info

st.set_page_config(
    page_title='LostWord Tools',
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.header("Use")
    st.caption("Calculates a relative damage index gauging an attack's strength")
    st.header("Usage")
    st.caption("Fill in the table on the right")

st.header("Parse and Load Character's LW")
st.text("You still need to manually input % Card and Killer Hit (Y/N)")
char = st.text_input("Character ([RE if Rebirth] [Universe Code] [Character Name], i.e. A6 Yuyuko or RE L1 Yuyuko)")
sc_select = st.selectbox("Spell Card to Calculate", ("Spread Shot", "Focus Shot", "SC1", "SC2", "LW"), index=4)
weak_res_select = st.selectbox("Elemental Weakness/Resist Configuration", ("Primary Effective, Resist Others", "Primary Effective, Neutral Others", "All Effective", "All Neutral", "All Resist"), index=0)

if sc_select == "Spread Shot":
    sc_index = 0
elif sc_select == "Focus Shot":
    sc_index = 2
elif sc_select == "SC1":
    sc_index = 4
elif sc_select == "SC2":
    sc_index = 6
else:
    sc_index = 8

loaded_stats = False
yangatkv = 0
yangdefv = 0
agiv = 0
yinatkv = 0
yindefv = 0
dmgres = 0
dmgeff = 0
line_info = ""
is_rebirth = False
if len(char) != 0:
    char_link = char.replace(" ", "_")
    try: 
        eles, yinyang, bulletnums, bulletpows, slices, hards, yangatkv, yangdefv, agiv, yinatkv, yindefv, dmgres, dmgeff, is_rebirth, line_info = get_stats(weak_res_select, sc_index, char_link)
        st.toast(line_info, icon="💡")
        loaded_stats = True
    except:
        raise ValueError(f"{char} is not a valid character.")
st.header("Manual Input")
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
if loaded_stats:
    for i in range(6):
        df.loc[i, '# Bullets'] = bulletnums[i]
        df.loc[i, 'Power'] = bulletpows[i]
        df.loc[i, 'Eff/Neu/Res'] = eles[i]
        df.loc[i, '% Slice'] = slices[i]
        df.loc[i, '% Hard'] = hards[i]
        df.loc[i, 'Yin/Yang'] = yinyang[i]
stats = st.data_editor(df)
fullbreak = st.checkbox(label="Full Break?", value=False)
with st.expander("Character Stats"):
    eff_dmg = st.number_input(label="% Damage to Effective", value=dmgeff)
    res_dmg = st.number_input(label="% Damage to Resist", value=dmgres)
    yinatk = st.number_input(label="Yin ATK", value=yinatkv)
    yangatk = st.number_input(label="Yang ATK", value=yangatkv)
    agi = st.number_input(label="Agility", value=agiv)
    yindef = st.number_input(label="Yin DEF", value=yindefv)
    yangdef = st.number_input(label="Yang DEF", value=yangdefv)
with st.expander("Miscellaneous"):
    rebirth = st.checkbox(label="Rebirth?", value=is_rebirth)
    st.header("Buffs", divider="gray")
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
    critatkii = st.slider(label="CRIT ATK II Buffs", min_value=-10, max_value=10, value=0)
    st.header("Debuffs", divider="gray")
    yindefdown = st.slider(label="Yin DEF Debuffs", min_value=-10, max_value=10, value=(10 if fullbreak else 0))
    yindefiidown = st.slider(label="Yin DEF II Debuffs", min_value=-10, max_value=10, value=0)
    yangdefdown = st.slider(label="Yang DEF Debuffs", min_value=-10, max_value=10, value=(10 if fullbreak else 0))
    yangdefiidown = st.slider(label="Yang DEF II Debuffs", min_value=-10, max_value=10, value=0)
    critdefdown = st.slider(label="Crit DEF Debuffs", min_value=-10, max_value=10, value=0)
    critdefiidown = st.slider(label="Crit DEF II Debuffs", min_value=-10, max_value=10, value=0)
# Get the multiplier for a certain buff count
def mult(num):
    if num < 0:
        return 1 / (1 + 0.3 * max(num, -10))
    else:
        return 1 + 0.3 * min(num, 10)
def calc_line(line):
    effresneu = 0.5 * (1 + res_dmg / 100)
    if line["Eff/Neu/Res"] == "Neu":
        effresneu = 1.0
    if line["Eff/Neu/Res"] == "Eff":
        effresneu = 2.0 * (1 + eff_dmg / 100)
    
    killer = 1.0
    if line["Killer Hit (Y/N)"] == "Y":
        killer = 1.0 + mult(critatkb + critdefdown) * mult(critatkii + critdefiidown)
    cur_agi = agi * mult(agiii) / 4 * mult(agib)
    cur_yinatk = yinatk * mult(yinatkb) / 4 * mult(yinatkii)
    cur_yangatk = yangatk * mult(yangatkb) / 4 * mult(yangatkii)
    cur_yindef = yindef * mult(yindefb) / 4 * mult(yindefii)
    cur_yangdef = yangdef * mult(yangdefb) / 4 * mult(yangdefii)
    cur_yindebuff = mult(yindefdown) * mult(yindefiidown)
    cur_yangdebuff = mult(yangdefdown) * mult(yangdefiidown)
    
    if line['Yin/Yang'] == "Yin":
        line_stat = (line['% Slice'] / 100 * cur_agi + line['% Hard'] / 100 * cur_yindef + cur_yinatk) * cur_yindebuff
    else:
        line_stat = (line['% Slice'] / 100 * cur_agi + line['% Hard'] / 100 * cur_yangdef + cur_yangatk) * cur_yangdebuff
    level = 1
    if rebirth:
        level = 1.4
    return level * line["# Bullets"] * line["Power"] * (1 + line["% Card"] / 100) * effresneu * killer * line_stat / 1000

if st.button("Submit Query"):
    total_dmg = 0.0
    for i in range(6):
        total_dmg += calc_line(stats.iloc[i])
    st.success(f"Damage Index: {round(total_dmg)}", icon="✅")
    print("Query Complete") # Log a succcess message
