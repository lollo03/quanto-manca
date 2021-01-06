import io
from datetime import timedelta as td

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

DATA_URL = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini" \
           "-summary-latest.csv"
ITALIAN_POPULATION = 60_360_000
HIT = ITALIAN_POPULATION / 100 * 80  # We need 80% of population vaccined for herd immunity

r = requests.get(DATA_URL)
df = pd.read_csv(
    io.StringIO(r.text),
    index_col="data_somministrazione",
)
df.index = pd.to_datetime(
    df.index,
    format="%Y-%m-%d",
)
df = df.loc[df["area"] == "ITA"]
df["totale"] = pd.to_numeric(df["totale"])
# df = df[:-1]  # Ignore the last day because it's often incomplete

lastWeekData = df.loc[df.index > df.index[-1] - td(days=7)]
vaccinesPerDayAverage = sum(lastWeekData["totale"]) / 7
remainingDays = HIT / vaccinesPerDayAverage
hitDate = df.index[-1] + td(days=remainingDays)

# Generate plot
plt.ylabel("Vaccini al giorno")
plt.xlabel("Ultima settimana")
plt.grid(True)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
plt.gcf().autofmt_xdate()
plt.bar(lastWeekData.index, height=lastWeekData["totale"])
# Trendline
z = np.polyfit(range(0, 7), lastWeekData["totale"], 2)
p = np.poly1d(z)
plt.plot(lastWeekData.index, p(range(0, 7)), "r--")
plt.savefig("plot.png", dpi=300, bbox_inches='tight')

# Generate template
with open("template.html", "r+") as f:
    with open("index.html", "w+") as wf:
        for line in f.read().splitlines():
            if "<!-- totalVaccinations -->" in line:
                line = f"{sum(df['totale'])}"
            elif "<!-- totalVaccinationsLastWeek -->" in line:
                line = f"{int(vaccinesPerDayAverage*7)}"
            elif "<!-- vaccinesPerDay -->" in line:
                line = f"{int(vaccinesPerDayAverage)}"
            elif "<!-- hitDate -->" in line:
                line = f"{hitDate.strftime('%d/%m/%Y')}"
            elif "<!-- hitHour -->" in line:
                line = f"{hitDate.strftime('%H:%M:%S')}"
            elif "<!-- daysRemaining -->" in line:
                line = f"{int(remainingDays)}"
            wf.write("\n" + line)