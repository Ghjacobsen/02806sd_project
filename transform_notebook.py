#!/usr/bin/env python3
"""Transform Assignment2_Final.ipynb with upgraded visualizations."""
import json
import sys
import copy

NB_PATH = sys.argv[1] if len(sys.argv) > 1 else 'notebooks/Assignment2_Final.ipynb'

with open(NB_PATH) as f:
    nb = json.load(f)

cells = nb['cells']

def make_code_cell(source_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source_lines
    }

def make_md_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines
    }

def src(cell):
    return ''.join(cell['source'])

# ──────────────────────────────────────────────
# Cell 2: Update imports (add DualMap, patches)
# ──────────────────────────────────────────────
cells[2] = make_code_cell([
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.ticker as ticker\n",
    "import matplotlib.patches as mpatches\n",
    "import seaborn as sns\n",
    "import plotly.express as px\n",
    "import plotly.graph_objects as go\n",
    "from plotly.subplots import make_subplots\n",
    "import folium\n",
    "from folium.plugins import HeatMap, DualMap\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# Consistent style\n",
    "plt.rcParams.update({\n",
    "    'figure.facecolor': 'white',\n",
    "    'axes.facecolor': 'white',\n",
    "    'font.family': 'sans-serif',\n",
    "    'font.sans-serif': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],\n",
    "    'font.size': 11,\n",
    "    'axes.titlesize': 14,\n",
    "    'axes.labelsize': 12,\n",
    "    'axes.spines.top': False,\n",
    "    'axes.spines.right': False,\n",
    "})\n",
    "\n",
    "# Color palette — consistent across all visualizations\n",
    "PALETTE = {\n",
    "    'civil_sidewalks': '#E63946',\n",
    "    'civil_sidewalks_light': '#F4A0A8',\n",
    "    'drug_offense': '#457B9D',\n",
    "    'disorderly_conduct': '#2A9D8F',\n",
    "    'warrant': '#E9C46A',\n",
    "    'suspicious_occ': '#F4A261',\n",
    "    'larceny_theft': '#264653',\n",
    "    'prostitution': '#8E44AD',\n",
    "    'traffic_violation': '#1ABC9C',\n",
    "    'homeless_total': '#6A0572',\n",
    "    'homeless_sheltered': '#AB83A1',\n",
    "    'homeless_unsheltered': '#6A0572',\n",
    "    'annotation': '#555555',\n",
    "    'boudin_line': '#333333',\n",
    "    'policy_era': '#FFF3F3',\n",
    "}\n",
    "\n",
    "PLOTLY_COLORS = {\n",
    "    'Civil Sidewalks': '#E63946',\n",
    "    'Drug Offense': '#457B9D',\n",
    "    'Disorderly Conduct': '#2A9D8F',\n",
    "    'Warrant': '#E9C46A',\n",
    "    'Suspicious Occ': '#F4A261',\n",
    "    'Larceny Theft': '#264653',\n",
    "    'Prostitution': '#8E44AD',\n",
    "    'Traffic Violation Arrest': '#1ABC9C',\n",
    "}\n",
    "\n",
    "print('Libraries loaded.')\n",
])

# ──────────────────────────────────────────────
# Cell 11: Viz 1 section header (keep)
# ──────────────────────────────────────────────
cells[11] = make_md_cell([
    "---\n",
    "## Visualization 1: The Vanishing Crime (Static Chart)\n",
    "\n",
    "A 2-panel annotated figure. **Top:** the dramatic cliff-drop in Civil Sidewalks reports. **Bottom:** normalized trends for the top correlated crimes — showing they did *not* follow the same trajectory.\n",
])

# ──────────────────────────────────────────────
# Cell 12: Viz 1 — upgraded 2-panel static chart
# ──────────────────────────────────────────────
cells[12] = make_code_cell([
    "# --- VISUALIZATION 1: Annotated 2-panel static figure ---\n",
    "import os\n",
    "os.makedirs('../reports/figures', exist_ok=True)\n",
    "\n",
    "cs_yearly = df[df['Incident Category'] == 'Civil Sidewalks'].groupby('Year').size()\n",
    "all_years = range(2018, 2026)\n",
    "cs_yearly = cs_yearly.reindex(all_years, fill_value=0)\n",
    "\n",
    "# Top-3 correlated crimes for trend overlay\n",
    "top3 = correlated_crimes[:3]\n",
    "top3_yearly = (\n",
    "    df[df['Incident Category'].isin(top3)]\n",
    "    .groupby(['Year', 'Incident Category']).size()\n",
    "    .reset_index(name='Count')\n",
    ")\n",
    "baselines_top3 = top3_yearly[top3_yearly['Year'] == 2018].set_index('Incident Category')['Count']\n",
    "top3_yearly['Normalized'] = top3_yearly.apply(\n",
    "    lambda r: r['Count'] / baselines_top3.get(r['Incident Category'], 1), axis=1\n",
    ")\n",
    "cs_baseline = cs_yearly.get(2018, 1)\n",
    "cs_norm = cs_yearly / cs_baseline\n",
    "\n",
    "# --- Build figure ---\n",
    "fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8.5), gridspec_kw={'height_ratios': [1, 0.8]})\n",
    "fig.subplots_adjust(hspace=0.35)\n",
    "\n",
    "# ---- Top panel: Civil Sidewalks bar chart ----\n",
    "ax1.axvspan(2019.5, 2025.5, color=PALETTE['policy_era'], zorder=0)\n",
    "ax1.text(2022.5, cs_yearly.max() * 1.07, 'Post-policy shift',\n",
    "         ha='center', fontsize=9, fontstyle='italic', color=PALETTE['annotation'])\n",
    "\n",
    "bars = ax1.bar(\n",
    "    cs_yearly.index, cs_yearly.values,\n",
    "    color=[PALETTE['civil_sidewalks'] if y < 2020 else PALETTE['civil_sidewalks_light'] for y in cs_yearly.index],\n",
    "    edgecolor='white', linewidth=0.8, width=0.65, zorder=3\n",
    ")\n",
    "\n",
    "ax1.axvline(x=2019.5, color=PALETTE['boudin_line'], linestyle='--', linewidth=1.2, zorder=2)\n",
    "ax1.annotate(\n",
    "    'DA Boudin takes office\\n(January 2020)',\n",
    "    xy=(2019.5, cs_yearly.max() * 0.75),\n",
    "    xytext=(2017.2, cs_yearly.max() * 0.92),\n",
    "    fontsize=9, color=PALETTE['annotation'],\n",
    "    arrowprops=dict(arrowstyle='->', color=PALETTE['annotation'], lw=1.2, connectionstyle='arc3,rad=0.2'),\n",
    "    ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#ddd', alpha=0.9)\n",
    ")\n",
    "\n",
    "for year, count in cs_yearly.items():\n",
    "    if count > 0:\n",
    "        ax1.text(year, count + cs_yearly.max() * 0.02, f'{count:,}',\n",
    "                 ha='center', va='bottom', fontsize=8.5, color='#333', fontweight='bold')\n",
    "    else:\n",
    "        ax1.text(year, cs_yearly.max() * 0.02, '0', ha='center', va='bottom', fontsize=8.5, color='#999')\n",
    "\n",
    "ax1.set_ylabel('Number of Incidents', fontsize=11)\n",
    "ax1.set_title('\"Civil Sidewalks\" Violations Reported by SFPD',\n",
    "              fontsize=14, fontweight='bold', pad=12)\n",
    "ax1.set_xticks(list(all_years))\n",
    "ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))\n",
    "ax1.set_ylim(0, cs_yearly.max() * 1.18)\n",
    "ax1.grid(axis='y', alpha=0.25, zorder=0)\n",
    "\n",
    "# ---- Bottom panel: Normalized trend lines ----\n",
    "ax2.plot(list(all_years), [cs_norm.get(y, 0) for y in all_years],\n",
    "         color=PALETTE['civil_sidewalks'], linewidth=2.5, marker='o', markersize=6,\n",
    "         label='Civil Sidewalks', zorder=5)\n",
    "\n",
    "crime_palette = [PALETTE['drug_offense'], PALETTE['disorderly_conduct'], PALETTE['warrant']]\n",
    "for idx, crime in enumerate(top3):\n",
    "    cdata = top3_yearly[top3_yearly['Incident Category'] == crime]\n",
    "    ax2.plot(cdata['Year'], cdata['Normalized'],\n",
    "             color=crime_palette[idx % len(crime_palette)], linewidth=2, marker='s', markersize=5,\n",
    "             label=crime, zorder=4, alpha=0.85)\n",
    "\n",
    "ax2.axvspan(2019.5, 2025.5, color=PALETTE['policy_era'], zorder=0)\n",
    "ax2.axhline(y=1.0, color='#ccc', linestyle=':', linewidth=1, zorder=1)\n",
    "ax2.axvline(x=2019.5, color=PALETTE['boudin_line'], linestyle='--', linewidth=1, zorder=2)\n",
    "ax2.text(2018.1, 1.02, '2018 baseline', fontsize=8, color='#aaa', fontstyle='italic')\n",
    "\n",
    "ax2.set_xlabel('Year', fontsize=11)\n",
    "ax2.set_ylabel('Incidents (relative to 2018)', fontsize=11)\n",
    "ax2.set_title('Do related crimes follow the same drop?', fontsize=13, fontweight='bold', pad=12)\n",
    "ax2.set_xticks(list(all_years))\n",
    "ax2.legend(loc='upper right', fontsize=9, framealpha=0.9, edgecolor='#ddd')\n",
    "ax2.grid(axis='y', alpha=0.25, zorder=0)\n",
    "\n",
    "plt.savefig('../reports/figures/viz1_civil_sidewalks.png', dpi=200, bbox_inches='tight')\n",
    "plt.savefig('../reports/figures/viz1_civil_sidewalks.svg', bbox_inches='tight')\n",
    "plt.show()\n",
    "print('Saved: reports/figures/viz1_civil_sidewalks.png & .svg')\n",
])

# ──────────────────────────────────────────────
# Cell 13: Viz 1 caption
# ──────────────────────────────────────────────
cells[13] = make_md_cell([
    "**Figure 1 — Caption:** *The top panel shows the raw count of \"Civil Sidewalks\" violations — covering camping on sidewalks, aggressive panhandling, and blocking public rights-of-way — which collapsed from thousands of incidents per year to near-zero after DA Chesa Boudin took office in January 2020. The shaded region marks the post-policy-shift era. The bottom panel tests whether related crimes followed the same trajectory, normalizing each category to its 2018 level. Civil Sidewalks (red) flatlines after 2020, while correlated crimes such as Drug Offense and Disorderly Conduct show much more moderate changes. If real-world conditions had improved, we would expect all related categories to decline together. They did not.*\n",
])

# ──────────────────────────────────────────────
# Cell 14: Viz 2 section header
# ──────────────────────────────────────────────
cells[14] = make_md_cell([
    "---\n",
    "## Visualization 2: The Geography Doesn't Lie (Map)\n",
    "\n",
    "If homelessness-related activity truly disappeared, we'd expect the neighborhoods that generated Civil Sidewalks reports to also show declines in related crime. We use a **synchronized side-by-side map** (DualMap) to compare: the left panel shows Civil Sidewalks hotspots before 2020, the right panel shows correlated crimes after 2020. Pan or zoom on either side — the other follows.\n",
])

# Cells 15-16: keep geographic data prep as-is

# ──────────────────────────────────────────────
# Replace cells 17-24 (old Folium A, Folium B, save, Plotly choropleth header, GeoJSON load, ratios, choropleths)
# with: [17] DualMap header, [18] DualMap code, [19] DualMap save
# ──────────────────────────────────────────────

new_cell_17 = make_md_cell([
    "### Folium DualMap — Before vs After 2020\n",
])

new_cell_18 = make_code_cell([
    "# --- VIZ 2: Synchronized DualMap ---\n",
    "SF_CENTER = [37.7749, -122.4194]\n",
    "\n",
    "m = DualMap(location=SF_CENTER, zoom_start=12, tiles='CartoDB positron')\n",
    "\n",
    "# Left panel: Civil Sidewalks pre-2020 (red gradient)\n",
    "HeatMap(\n",
    "    cs_pre_coords,\n",
    "    radius=9, blur=11, max_zoom=13, min_opacity=0.3,\n",
    "    gradient={0.2: '#fee0d2', 0.4: '#fc9272', 0.65: '#de2d26', 0.85: '#a50f15', 1.0: '#67000d'}\n",
    ").add_to(m.m1)\n",
    "\n",
    "folium.map.Marker(\n",
    "    [37.805, -122.44],\n",
    "    icon=folium.DivIcon(html=(\n",
    "        '<div style=\"font-size:13px;font-weight:bold;color:#a50f15;'\n",
    "        'background:rgba(255,255,255,0.92);padding:6px 14px;border-radius:5px;'\n",
    "        'border:2px solid #E63946;box-shadow:0 2px 6px rgba(0,0,0,0.15);'\n",
    "        'white-space:nowrap;\">'\n",
    "        'Pre-2020: Civil Sidewalks'\n",
    "        '</div>'\n",
    "    ))\n",
    ").add_to(m.m1)\n",
    "\n",
    "# Right panel: Correlated crimes post-2020 (blue gradient)\n",
    "HeatMap(\n",
    "    corr_post_coords,\n",
    "    radius=9, blur=11, max_zoom=13, min_opacity=0.3,\n",
    "    gradient={0.2: '#deebf7', 0.4: '#9ecae1', 0.65: '#3182bd', 0.85: '#08519c', 1.0: '#08306b'}\n",
    ").add_to(m.m2)\n",
    "\n",
    "folium.map.Marker(\n",
    "    [37.805, -122.44],\n",
    "    icon=folium.DivIcon(html=(\n",
    "        '<div style=\"font-size:13px;font-weight:bold;color:#08519c;'\n",
    "        'background:rgba(255,255,255,0.92);padding:6px 14px;border-radius:5px;'\n",
    "        'border:2px solid #457B9D;box-shadow:0 2px 6px rgba(0,0,0,0.15);'\n",
    "        'white-space:nowrap;\">'\n",
    "        f'Post-2020: {\", \".join(map_crimes)}'\n",
    "        '</div>'\n",
    "    ))\n",
    ").add_to(m.m2)\n",
    "\n",
    "m\n",
])

new_cell_19 = make_code_cell([
    "# Save DualMap\n",
    "m.save('../reports/figures/viz2_dualmap.html')\n",
    "print('Saved: reports/figures/viz2_dualmap.html')\n",
])

# Replace cells 17-24 (8 cells) with 3 new cells
cells[17:25] = [new_cell_17, new_cell_18, new_cell_19]

# After replacement, cell indices shift:
# old[25] -> new[20]: Figure 2 caption
# old[26] -> new[21]: Viz 3 section header
# old[27] -> new[22]: Viz 3 data prep
# old[28] -> new[23]: Viz 3 main figure
# old[29] -> new[24]: Viz 3 save
# old[30] -> new[25]: Viz 3 caption
# old[31] -> new[26]: Narrative
# old[32] -> new[27]: Deliverables

# ──────────────────────────────────────────────
# new[20]: Viz 2 caption (was old[25])
# ──────────────────────────────────────────────
cells[20] = make_md_cell([
    "**Figure 2 — Caption:** *A synchronized side-by-side map of San Francisco. The left panel shows Civil Sidewalks violations before 2020 (red), concentrated in the Tenderloin and SoMa. The right panel shows the most geographically co-located crime categories — Drug Offense and Disorderly Conduct — after 2020 (blue). Pan or zoom either side and the other follows. The hotspots have not moved. The underlying street-level activity persists in the same neighborhoods; only the \"Civil Sidewalks\" label vanished from the reports.*\n",
])

# ──────────────────────────────────────────────
# new[21]: Viz 3 section header
# ──────────────────────────────────────────────
cells[21] = make_md_cell([
    "---\n",
    "## Visualization 3: The Full Picture (Interactive Plotly)\n",
    "\n",
    "An interactive 3-panel chart combining:\n",
    "- **Top**: Normalized yearly crime trends — Civil Sidewalks and its correlated categories (toggle in legend)\n",
    "- **Middle**: Larceny Theft arrest/citation rate over time — did enforcement keep up?\n",
    "- **Bottom**: SF's actual homeless population count (PIT data)\n",
    "\n",
    "Use the legend to toggle crime categories on/off. Hover for details.\n",
])

# ──────────────────────────────────────────────
# new[22]: Viz 3 data prep (add arrest rate)
# ──────────────────────────────────────────────
cells[22] = make_code_cell([
    "# --- VISUALIZATION 3: Data Preparation ---\n",
    "\n",
    "# Yearly counts for story categories\n",
    "story_yearly = (\n",
    "    df[df['Incident Category'].isin(story_categories)]\n",
    "    .groupby(['Year', 'Incident Category'])\n",
    "    .size()\n",
    "    .reset_index(name='Count')\n",
    ")\n",
    "\n",
    "# Normalize to 2018 baseline\n",
    "baselines = story_yearly[story_yearly['Year'] == 2018].set_index('Incident Category')['Count']\n",
    "story_yearly['Normalized'] = story_yearly.apply(\n",
    "    lambda row: row['Count'] / baselines.get(row['Incident Category'], 1), axis=1\n",
    ")\n",
    "\n",
    "# Arrest rate analysis (inspired by Gustav's exploration)\n",
    "larceny_df = df[df['Incident Category'] == 'Larceny Theft'].copy()\n",
    "larceny_df['Was_Arrested'] = larceny_df['Resolution'].str.contains('Arrest|Cite', case=False, na=False)\n",
    "arrest_yearly = (\n",
    "    larceny_df.groupby('Year')\n",
    "    .agg(Total=('Was_Arrested', 'size'), Arrested=('Was_Arrested', 'sum'))\n",
    "    .reset_index()\n",
    ")\n",
    "arrest_yearly['Arrest_Rate'] = arrest_yearly['Arrested'] / arrest_yearly['Total']\n",
    "\n",
    "print('Baseline (2018) crime counts:')\n",
    "for cat, count in baselines.items():\n",
    "    print(f'  {cat}: {count:,}')\n",
    "print(f'\\nArrest rate for Larceny Theft by year:')\n",
    "for _, r in arrest_yearly.iterrows():\n",
    "    print(f\"  {int(r['Year'])}: {r['Arrest_Rate']:.1%} ({int(r['Arrested']):,}/{int(r['Total']):,})\")\n",
])

# ──────────────────────────────────────────────
# new[23]: Viz 3 — upgraded 3-panel interactive Plotly
# ──────────────────────────────────────────────
cells[23] = make_code_cell([
    "# --- VISUALIZATION 3: Interactive 3-panel Plotly dashboard ---\n",
    "\n",
    "fig = make_subplots(\n",
    "    rows=3, cols=1,\n",
    "    row_heights=[0.45, 0.25, 0.30],\n",
    "    shared_xaxes=False,\n",
    "    vertical_spacing=0.08,\n",
    "    subplot_titles=[\n",
    "        'Crime Trends (Normalized to 2018 Baseline)',\n",
    "        'Larceny Theft Arrest / Citation Rate',\n",
    "        'SF Homeless Population (Point-in-Time Count)'\n",
    "    ]\n",
    ")\n",
    "\n",
    "# --- Top panel: Crime trend lines ---\n",
    "for crime in story_categories:\n",
    "    crime_data = story_yearly[story_yearly['Incident Category'] == crime]\n",
    "    is_cs = crime == 'Civil Sidewalks'\n",
    "    color = PLOTLY_COLORS.get(crime, '#888')\n",
    "    fig.add_trace(\n",
    "        go.Scatter(\n",
    "            x=crime_data['Year'],\n",
    "            y=crime_data['Normalized'],\n",
    "            name=crime,\n",
    "            mode='lines+markers',\n",
    "            line=dict(color=color, width=3.5 if is_cs else 2),\n",
    "            marker=dict(size=8 if is_cs else 5),\n",
    "            legendgroup='crimes',\n",
    "            legendgrouptitle_text='Crime Categories',\n",
    "            hovertemplate=(\n",
    "                f'<b>{crime}</b><br>'\n",
    "                'Year: %{x}<br>'\n",
    "                'Relative to 2018: %{y:.2f}x<br>'\n",
    "                f'Absolute: %{{customdata:,}}'\n",
    "                '<extra></extra>'\n",
    "            ),\n",
    "            customdata=crime_data['Count'],\n",
    "        ),\n",
    "        row=1, col=1\n",
    "    )\n",
    "\n",
    "# Boudin line\n",
    "fig.add_vline(x=2019.5, line_dash='dash', line_color=PALETTE['boudin_line'],\n",
    "              line_width=1.5, row=1, col=1)\n",
    "fig.add_annotation(\n",
    "    x=2020.2, y=1.08, text='Policy shift \\u2192', showarrow=False,\n",
    "    font=dict(size=10, color=PALETTE['annotation']), row=1, col=1\n",
    ")\n",
    "fig.add_hline(y=1.0, line_dash='dot', line_color='#ccc', line_width=1, row=1, col=1)\n",
    "\n",
    "# --- Middle panel: Arrest rate ---\n",
    "fig.add_trace(\n",
    "    go.Scatter(\n",
    "        x=arrest_yearly['Year'],\n",
    "        y=arrest_yearly['Arrest_Rate'],\n",
    "        name='Arrest/Citation Rate',\n",
    "        mode='lines+markers+text',\n",
    "        line=dict(color=PALETTE['larceny_theft'], width=2.5),\n",
    "        marker=dict(size=7, color=PALETTE['larceny_theft']),\n",
    "        text=[f'{r:.0%}' for r in arrest_yearly['Arrest_Rate']],\n",
    "        textposition='top center',\n",
    "        textfont=dict(size=9, color='#666'),\n",
    "        legendgroup='enforcement',\n",
    "        legendgrouptitle_text='Enforcement',\n",
    "        hovertemplate=(\n",
    "            '<b>Larceny Theft Enforcement</b><br>'\n",
    "            'Year: %{x}<br>'\n",
    "            'Arrest/Citation Rate: %{y:.1%}<br>'\n",
    "            '<extra></extra>'\n",
    "        ),\n",
    "    ),\n",
    "    row=2, col=1\n",
    ")\n",
    "\n",
    "fig.add_vline(x=2019.5, line_dash='dash', line_color=PALETTE['boudin_line'],\n",
    "              line_width=1.5, row=2, col=1)\n",
    "\n",
    "# --- Bottom panel: Homeless population ---\n",
    "for htype, color in [('Unsheltered', PALETTE['homeless_unsheltered']),\n",
    "                      ('Sheltered', PALETTE['homeless_sheltered'])]:\n",
    "    h_data = homeless_df[homeless_df['Type'] == htype]\n",
    "    fig.add_trace(\n",
    "        go.Bar(\n",
    "            x=h_data['Year'],\n",
    "            y=h_data['Count'],\n",
    "            name=htype,\n",
    "            marker_color=color,\n",
    "            legendgroup='homeless',\n",
    "            legendgrouptitle_text='Homeless PIT Count',\n",
    "            hovertemplate=f'<b>{htype}</b><br>Year: %{{x}}<br>Count: %{{y:,}}<extra></extra>',\n",
    "            width=1.5\n",
    "        ),\n",
    "        row=3, col=1\n",
    "    )\n",
    "\n",
    "# --- Layout ---\n",
    "fig.update_layout(\n",
    "    height=850, width=950,\n",
    "    template='plotly_white',\n",
    "    title=dict(\n",
    "        text=\"The Crime That Vanished \\u2014 But the Problem Didn't\",\n",
    "        font=dict(size=18, family='Helvetica Neue, Arial, sans-serif'),\n",
    "        x=0.5, xanchor='center'\n",
    "    ),\n",
    "    legend=dict(\n",
    "        orientation='v', yanchor='top', y=0.98, xanchor='left', x=1.02,\n",
    "        font=dict(size=10), bgcolor='rgba(255,255,255,0.9)',\n",
    "        bordercolor='#eee', borderwidth=1\n",
    "    ),\n",
    "    barmode='stack',\n",
    "    hovermode='x unified',\n",
    "    margin=dict(t=80, b=40, l=60, r=150),\n",
    ")\n",
    "\n",
    "fig.update_yaxes(title_text='Relative to 2018', row=1, col=1)\n",
    "fig.update_yaxes(title_text='Rate', tickformat='.0%', row=2, col=1)\n",
    "fig.update_yaxes(title_text='Population', row=3, col=1)\n",
    "fig.update_xaxes(dtick=1, row=1, col=1)\n",
    "fig.update_xaxes(dtick=1, title_text='Year', row=2, col=1)\n",
    "fig.update_xaxes(dtick=2, title_text='Year', row=3, col=1)\n",
    "\n",
    "fig.add_annotation(\n",
    "    text=\"Larceny Theft is SF's highest-volume crime \\u2014 its arrest rate<br>reflects overall enforcement intensity\",\n",
    "    xref='paper', yref='paper', x=0.01, y=0.48, showarrow=False,\n",
    "    font=dict(size=9, color='#888'), align='left'\n",
    ")\n",
    "\n",
    "fig.show()\n",
])

# ──────────────────────────────────────────────
# new[24]: Viz 3 save
# ──────────────────────────────────────────────
cells[24] = make_code_cell([
    "# Save interactive visualization\n",
    "fig.write_html('../reports/figures/viz3_interactive_trends.html', include_plotlyjs='cdn')\n",
    "print('Saved: reports/figures/viz3_interactive_trends.html')\n",
])

# ──────────────────────────────────────────────
# new[25]: Viz 3 caption
# ──────────────────────────────────────────────
cells[25] = make_md_cell([
    "**Figure 3 — Caption:** *A three-panel interactive dashboard. **Top:** incident counts for Civil Sidewalks and its most correlated crime categories, each normalized to their 2018 level (1.0 = same as 2018). Click legend items to toggle categories on and off. Civil Sidewalks (red) collapses to near-zero after 2020, while correlated crimes show much smaller changes. **Middle:** the arrest/citation rate for Larceny Theft, SF's highest-volume crime, as a proxy for overall enforcement intensity. The rate dropped from around 10% to below 5% — indicating that the policy shift affected not just what crimes are reported, but how aggressively they are pursued. **Bottom:** San Francisco's biennial Point-in-Time homeless count. The total was 8,035 in 2019 and 8,323 in 2024. The population those reports were meant to address did not shrink — the reporting did.*\n",
])

# ──────────────────────────────────────────────
# new[26]: Narrative (updated with arrest rate paragraph)
# ──────────────────────────────────────────────
cells[26] = make_md_cell([
    "---\n",
    "## Narrative Draft\n",
    "\n",
    "*(~800 words — adapted for the GitHub Pages site)*\n",
    "\n",
    "---\n",
    "\n",
    "### The Crime That Vanished — But the Problem Didn't\n",
    "\n",
    "In 2019, San Francisco police filed thousands of reports for \"Civil Sidewalks\" violations — a catch-all category covering offenses like camping on sidewalks, aggressive panhandling, and blocking public rights-of-way. These reports were concentrated in the Tenderloin, SoMa, and Mission — neighborhoods long associated with visible homelessness.\n",
    "\n",
    "By 2021, the number was close to zero. And it stayed there.\n",
    "\n",
    "If you stopped reading here, you might conclude that San Francisco had solved one of its most visible urban problems. That is the story the raw numbers appear to tell. But it is not the whole story.\n",
    "\n",
    "---\n",
    "\n",
    "**What the data actually shows**\n",
    "\n",
    "The dataset we work with is the San Francisco Police Department's Incident Reports, publicly available through [SF OpenData](https://data.sfgov.org). It covers every police-reported incident in the city from 2018 to early 2026 — hundreds of thousands of records, each tagged with a crime category, date, time, GPS coordinates, and police district.\n",
    "\n",
    "To test whether the decline in Civil Sidewalks reflects reality, we looked at which other crime categories share the most similar temporal pattern. Using Pearson correlation across yearly counts, we identified the crimes whose trends most closely tracked Civil Sidewalks before 2020. If homelessness-related activity had genuinely declined, we would expect these correlated crimes to decline in the same way.\n",
    "\n",
    "They did not. Figure 1 shows this divergence: Civil Sidewalks flatlines after 2020, while Drug Offense and Disorderly Conduct — crimes that co-occur in the same neighborhoods — show far more moderate changes.\n",
    "\n",
    "Figure 2 maps the geographic hotspots before and after 2020. The Tenderloin and SoMa remain dominant. The underlying activity persists in the same places — only the \"Civil Sidewalks\" label vanished from the data.\n",
    "\n",
    "---\n",
    "\n",
    "**What changed in 2020**\n",
    "\n",
    "In January 2020, District Attorney Chesa Boudin took office on a platform of criminal justice reform. His office deprioritized prosecution of quality-of-life offenses, including the sit/lie ordinances that generated most Civil Sidewalks reports. When prosecutors stop pursuing charges, police have less incentive to file reports.\n",
    "\n",
    "The arrest and citation rate for Larceny Theft — the city's highest-volume crime and a proxy for overall enforcement intensity — tells a similar story. It dropped from around 10% before 2020 to below 5% after, indicating a broader shift in how aggressively crimes are followed up on, not just a change in one category.\n",
    "\n",
    "Some readers might wonder about COVID-19. The timing overlaps — pandemic restrictions began in March 2020. But the pandemic ended. San Francisco reopened. By 2024 and 2025 the city was operating normally, yet Civil Sidewalks reports had not returned. A temporary disruption does not produce a permanent change. A policy shift does.\n",
    "\n",
    "---\n",
    "\n",
    "**The population the data forgot**\n",
    "\n",
    "The clearest evidence comes from outside the SFPD dataset. San Francisco conducts a biennial Point-in-Time (PIT) count of every person experiencing homelessness on a given night. In 2019, the total was 8,035 — including 5,180 unsheltered individuals. In 2024, it was 8,323. The unsheltered count has fluctuated, but the overall homeless population only grew.\n",
    "\n",
    "Homelessness did not decrease in San Francisco. The reports stopped. The problem did not.\n",
    "\n",
    "---\n",
    "\n",
    "**Why this matters**\n",
    "\n",
    "This is a concrete example of what Richardson, Schultz, and Crawford (2019) call \"dirty data\" — the insight that police datasets are not neutral measurements of crime, but reflections of enforcement priorities, political incentives, and institutional decisions. A naive analysis of SFPD data would conclude that sidewalk-related offenses were eliminated. A careful one recognizes that only the reporting was eliminated.\n",
    "\n",
    "For anyone using crime data to draw conclusions — whether evaluating policy, allocating resources, or training a predictive model — this distinction matters. The data does not lie. But it does not tell the whole truth either.\n",
    "\n",
    "---\n",
    "\n",
    "**References**\n",
    "\n",
    "1. Richardson, R., Schultz, J.M., & Crawford, K. (2019). *Dirty Data, Bad Predictions: How Civil Rights Violations Impact Police Data, Predictive Policing Systems, and Justice.* NYU Law Review, 94.\n",
    "2. San Francisco Department of Homelessness and Supportive Housing. *Homelessness Trends Dashboard.* [sf.gov](https://www.sf.gov/homelessness-trends-dashboard-inflow-and-outflow-analysis)\n",
    "3. San Francisco District Attorney's Office. Policy directives under DA Chesa Boudin, 2020–2022.\n",
    "4. Segel, E. & Heer, J. (2010). *Narrative Visualization: Telling Stories with Data.* IEEE TVCG.\n",
    "5. San Francisco Police Department. *Incident Reports (2018 to Present).* [SF OpenData](https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783).\n",
])

# ──────────────────────────────────────────────
# new[27]: Deliverables summary
# ──────────────────────────────────────────────
cells[27] = make_md_cell([
    "---\n",
    "## Deliverables Summary\n",
    "\n",
    "| # | Type | Description | File |\n",
    "|---|------|-------------|------|\n",
    "| 1 | Static (PNG/SVG) | 2-panel: Civil Sidewalks bars + correlated crime trends | `reports/figures/viz1_civil_sidewalks.png` |\n",
    "| 2 | Map (Folium DualMap HTML) | Synchronized pre/post-2020 heatmaps | `reports/figures/viz2_dualmap.html` |\n",
    "| 3 | Interactive Plotly (HTML) | 3-panel: crime trends + arrest rate + homeless pop | `reports/figures/viz3_interactive_trends.html` |\n",
    "\n",
    "**Next step:** Build GitHub Pages site at `Ghjacobsen.github.io`.\n",
])

nb['cells'] = cells
assert len(cells) == 28, f"Expected 28 cells, got {len(cells)}"

with open(NB_PATH, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"✓ Wrote {len(cells)} cells to {NB_PATH}")
