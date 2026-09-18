from pathlib import Path
import numpy as np
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'
def app():
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not at.exception
    return at

def test_empty_department_and_forecast_sensitivity():
    at=app()
    selected=at.multiselect[0].value
    at.multiselect[0].set_value([]).run()
    assert not at.exception
    assert any('No records' in e.value for e in at.info)
    at.multiselect[0].set_value(selected).run()
    at.slider[0].set_value(.10).run()
    detail=at.dataframe[0].value
    np.testing.assert_allclose(detail.scenario_forecast,detail.forecast*1.1)
