# A marimo notebook: the Southampton section of the exploration notebook, reactive.
#
# Run it with:  uv run marimo edit notebooks/2.0-jt-marimo-southampton.py
#
# How marimo differs from Jupyter:
#   - The notebook is a plain Python file, so git diffs are readable.
#   - Cells are linked by the variables they use. Change the dropdown below and
#     every cell that depends on it re-runs automatically.
#   - You cannot run cells out of order, so there is no hidden state.

import marimo

__generated_with = "0.26.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd

    from manager_tenure.config import SPELLS_FILE

    return SPELLS_FILE, mo, pd, plt


@app.cell
def _(mo):
    mo.md("""
    # Southampton managers, 1991 to 2025

    Each row in the cleaned table is one **spell**: one manager at one club.
    This notebook follows Southampton's spells. Pick a manager below, and the chart
    and tables update to show them.
    """)


@app.cell
def _(SPELLS_FILE, pd):
    # Load the cleaned table and keep only Southampton, in date order.
    spells = pd.read_parquet(SPELLS_FILE)
    sot = spells[spells["club"] == "Southampton"].sort_values("start_date").reset_index(drop=True)
    return (sot,)


@app.cell
def _(mo, sot):
    # A dropdown of every Southampton manager. Its value feeds the cells below.
    manager = mo.ui.dropdown(
        options=sorted(sot["name"].unique()),
        value="Ralph Hasenhüttl",
        label="Pick a manager",
    )
    manager
    return (manager,)


@app.cell
def _(manager, mo, sot):
    # Everything about the chosen manager, at Southampton.
    chosen = sot[sot["name"] == manager.value]
    total_years = chosen["tenure_days"].sum() / 365.25
    pl_years = chosen["pl_tenure_days"].sum() / 365.25
    mo.md(
        f"""
        ### {manager.value}

        - **Spells at Southampton:** {len(chosen)}
        - **Total time in charge:** {total_years:.1f} years
        - **Premier League time:** {pl_years:.1f} years

        *Premier League time uses the "Years in League" labels, which are not fully
        reliable. See the notebook section on that question.*
        """
    )
    return (chosen,)


@app.cell
def _(chosen, plt, sot):
    # The timeline: every Southampton spell as a bar. The chosen manager is red, the rest grey.
    fig, ax = plt.subplots(figsize=(10, 8))
    for i, row in enumerate(sot.itertuples()):
        is_chosen = row.name == chosen["name"].iloc[0] if len(chosen) else False
        ax.barh(
            y=i,
            width=(row.end_date - row.start_date).days,
            left=row.start_date,
            height=0.7,
            color="tab:red" if is_chosen else "lightgrey",
            hatch="//" if row.is_caretaker else None,
            edgecolor="white",
        )
    ax.set_yticks(range(len(sot)))
    ax.set_yticklabels(sot["name"], fontsize=8)
    ax.invert_yaxis()
    ax.xaxis_date()
    ax.set_title("Southampton spells (red = chosen manager, hatched = caretaker)")
    plt.tight_layout()
    fig


@app.cell
def _(mo, sot):
    # One row per manager, sorted by total time in charge.
    summary = (
        sot.groupby("name")
        .agg(
            spells=("name", "size"),
            total_years=("tenure_days", lambda d: round(d.sum() / 365.25, 1)),
            pl_years=("pl_tenure_days", lambda d: round(d.sum() / 365.25, 1)),
            first_start=("start_date", "min"),
        )
        .sort_values("total_years", ascending=False)
        .reset_index()
    )
    mo.ui.table(summary, label="Southampton managers, by total time in charge")


@app.cell
def _(mo):
    mo.md("""
    ## Questions to think about

    1. Does a long stay at Southampton go with better results? We don't have results
       data yet, so this can't be answered from this notebook.
    2. Which spells look wrong to you? Compare them with what you remember.
    """)


if __name__ == "__main__":
    app.run()
