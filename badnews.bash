rm -rf wind_forecasts_actuals || true
python -m mape_maker "mape_maker/samples/rts_gmlc/WIND_forecasts_actuals.csv" -st "actuals" -n 5 -bp "ARMA" -o "wind_forecasts_actuals" -s 1234
