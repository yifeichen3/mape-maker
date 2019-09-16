rm -rf wind_forecasts_actuals2 || true
python -m mape_maker "mape_maker/samples/rts_gmlc/WIND_forecasts_actuals.csv" -st "actuals" -n 2 -bp "iid" -o "wind_forecasts_actuals2" -s 1234
