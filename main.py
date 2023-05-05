from flask import Flask, render_template
import pandas as pd

app = Flask("My Website")

stations_data = pd.read_csv("data_small/stations.txt", skiprows=17)

stations = stations_data[['STAID', 'STANAME']].sort_values(by=['STANAME'])
stations = stations[(stations['STAID'] >= 0)]


@app.route("/")
def home():
    return render_template("home.html", data=stations.to_html(index=False))


@app.route("/api/v1/<station>/<date>")
def home_page(station, date):
    """
    :param station: is the station id
    :param date: is the date in YYYYMMDD format
    :return: dictionary

    :filename: accessing the files with weather data
    :df: data frame with parsed collection of dates
    :temperature: converted to Celsius temperatures for each date
    :stations_file: collection of available stations with skipped metadata
    """

    filename = "data_small/TG_STAID" + str(station).zfill(6) + ".txt"
    df = pd.read_csv(filename, skiprows=20, parse_dates=['    DATE'])
    temperature = df.loc[df['    DATE'] == date]['   TG'].squeeze() / 10

    stations_file = pd.read_csv("data_small/stations.txt", skiprows=17)
    station_name = stations_file[stations_file['STAID'] == int(station)]['STANAME'].item()

    unavailable_temperature_message = """The data for this day is unavailable.
    For different stations the available data can vary.
    Try to find data between Jan 1 1860 - Dec 31 2003."
    For extensive stations try with until May 31 2022."""

    wrap = {'station name': station_name.strip(),
            "station_id": station,
            "date": f"Month: {date[4:6]} Day: {date[6:8]} Year: {date[:4]}",
            "date_api_format": date,
            'temperature': temperature if temperature != -999.9
            else unavailable_temperature_message}

    return wrap


@app.route("/api/v1/<station>")
def all_data(station):
    filename = "data_small/TG_STAID" + str(station).zfill(6) + ".txt"
    df = pd.read_csv(filename, skiprows=20, parse_dates=['    DATE'])

    df["   TG"] = [temp/10 for temp in df["   TG"]]

    result = df.to_dict(orient='records')
    return result


if __name__ == "__main__":
    app.run(debug=True)
