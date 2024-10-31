from prefect import flow, task, get_run_logger
import pandas as pd
import datetime
import os
import pprint

from utils import get_proposal_dir

def export_E_step(run):
    logger = get_run_logger()
    scan_index = run.start["scan_index"]
    
    E =  run.start['user_input']['E_points']

    I0 = run["primary"]["data"]["I0"].read()
    I_TEY = run["primary"]["data"]["fbratio"].read()

    if 'xs' in run.start['detectors']:
        If_1_roi1 = run["primary"]["data"]["xs_channel01_mcaroi01_total_rbv"].read()
        If_1_roi2 = run["primary"]["data"]["xs_channel01_mcaroi02_total_rbv"].read()
        If_1_roi3 = run["primary"]["data"]["xs_channel01_mcaroi03_total_rbv"].read()
        If_1_roi4 = run["primary"]["data"]["xs_channel01_mcaroi04_total_rbv"].read()

        df = pd.DataFrame(
            {
                "#Energy": E,
                "I0": I0,
                "I_TEY": I_TEY,
                "If_CH1_roi1": If_1_roi1,
                "If_CH1_roi2": If_1_roi2,
                "If_CH1_roi3": If_1_roi3,
                "If_CH1_roi4": If_1_roi4,
            }
        )
    elif 'xsmart' in run.start['detectors']:
        If_1_roi1 = run["primary"]["data"]["xssmart_channel01_mcaroi01_total_rbv"].read()
        If_2_roi1 = run["primary"]["data"]["xssmart_channel02_mcaroi01_total_rbv"].read()
        If_3_roi1 = run["primary"]["data"]["xssmart_channel03_mcaroi01_total_rbv"].read()
        If_4_roi1 = run["primary"]["data"]["xssmart_channel04_mcaroi01_total_rbv"].read()

        df = pd.DataFrame(
            {
                "#Energy": E,
                "I0": I0,
                "I_TEY": I_TEY,
                "If_CH1_roi1": If_1_roi1,
                "If_CH2_roi1": If_2_roi1,
                "If_CH3_roi1": If_3_roi1,
                "If_CH4_roi1": If_4_roi1,
            }
        )
    else:
        raise ValueError("Export_E_step only works for 'xs' and 'xssmart' detectors.  "
                         f"This run has detectors: {run.start['detectors']}")


    start = run.start
    dt = datetime.datetime.fromtimestamp(start["time"])

    file_head = {
        "beamline_id": "TES/8-BM of NSLS-II",
        "operator": start["operator"],
        "plan_name": start["plan_name"],
        "scan_id": start["scan_id"],
        "scan_title": start["scan_title"],
        "time": f"{dt.date().isoformat()} {dt.time().isoformat()}",
        "uid": start["uid"],
        "user_input": start["user_input"],
        "derived_input": start["derived_input"],
    }

    working_dir = get_proposal_dir(run) / "E_step"
    filename = f"{start['scan_title']}-{start['scan_id']}-{start['operator']}-{dt.time().strftime('%H-%M-%S')}-{scan_index}.cvs"
    filepath = working_dir / filename

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wt") as output_file:
        output_file.write(pprint.pformat(file_head, width=100))
        output_file.write("\n")
        output_file.write("\n")
        output_file.write("\n")

    df.to_csv(filepath, header=True, index=False, mode="a")
    print(f"Data exported to {filepath}")
