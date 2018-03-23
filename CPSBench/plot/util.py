import json
import pandas as pd
import os
import numpy as np
import seaborn as sns
import itertools
import datetime
import pytz
import matplotlib

PHONES = {
    "Motorola XT1032": {"chip": "WCN3620", "pretty_name": "Motorola Moto G"},
    "LGE Nexus 4": {"chip": "WCN3660", "pretty_name": "LG Nexus 4"},
    "Asus Nexus 7": {"chip": "WCN3660", "pretty_name": "Asus Nexus 7"},
    "LGE Nexus 5": {"chip": "BCM4339", "pretty_name": "LG Nexus 5"},
    "LGE LG-D855": {"chip": "BCM4339", "pretty_name": "LG G3"},
    "Motorola Nexus 6": {"chip": "BCM4356", "pretty_name": "Motorola Nexus 6"},
    "HTC One M9": {"chip": "BCM4356", "pretty_name": "HTC One M9"},
    "Motorola MotoE2(4G-LTE)": {"chip": "WCN3620",
                                "pretty_name": "Motorola MotoE2"},
    "LGE Nexus 5X": {"chip": "QCA6174", "pretty_name": "LG Nexus 5X"},
    "Huawei Nexus 6P": {"chip": "BCM4358", "pretty_name": "Huawei Nexus 6P"},
    "Motorola XT1033": {"chip": "WCN3620", "pretty_name": "Motorola Moto G"},
    "Samsung GT-I9305": {"chip": "BCM4330", "pretty_name": "Samsung Galaxy S3"}
}


def get_soc(phone):
    return PHONES[phone]["chip"]


def get_pretty_name(phone):
    return PHONES[phone]["pretty_name"]


# calculate ideal RSSI from distances according to log-distancese model
def calc_log_dist(distances):
    dicts = []
    rssi = -(10 * 1.2 * np.log10(distances)) - 60
    i = 0
    for d in distances:
        dic = {"Distance (m)": d, "RSSI (dBm)": rssi[i],
               "Phone Model": "Log-Distance Model"}
        dicts.append(dic)
        i += 1
    df = pd.DataFrame(dicts)
    # df["Phone Model"] = df["Phone Model"].astype("category")
    return df


# print complete dataframe
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


# walk folder structure and return dataframe
def process_folder(root_path, filter_scan_mode=None,
                   filter_replicas=None, filter_benchmark=None,
                   filter_ble_operation='scanning'):
    all_frames = []
    for dir_name, subdir_list, file_list in os.walk(root_path):
        for fname in file_list:
            if fname.endswith('.json'):
                json_data = get_json(dir_name + "/" + fname)
                if filter_benchmark == "gatt":
                    pd_frames = get_gatt_frames(
                        json_data,
                        filter_benchmark=filter_benchmark,
                        filter_scan_mode=filter_scan_mode,
                        filter_replicas=filter_replicas,
                        filter_ble_operation=filter_ble_operation)
                elif filter_benchmark == "wifi":
                    pd_frames = get_wifi_frames(
                        json_data,
                        filter_benchmark=filter_benchmark,
                        filter_scan_mode=filter_scan_mode,
                        filter_replicas=filter_replicas,
                        filter_ble_operation=filter_ble_operation)
                else:
                    pd_frames = get_pd_frames(
                        json_data,
                        filter_benchmark=filter_benchmark,
                        filter_scan_mode=filter_scan_mode,
                        filter_replicas=filter_replicas,
                        filter_ble_operation=filter_ble_operation)
                if pd_frames is not None and len(pd_frames) != 0:
                    pd_frame = pd.concat(pd_frames)
                    all_frames.append(pd_frame)
    all_frame = pd.concat(all_frames)
    return all_frame


def get_wifi_frames(json_data, filter_benchmark=None, filter_scan_mode=None,
                    filter_replicas=None, filter_ble_operation='scanning'):
    pd_frames = []
    if "benchmark_result" in json_data:
        b_result = json_data["benchmark_result"]
        benchmark_name = json_data["name"]
        benchmark_time = json_data["time"]
        benchmark_start_time = b_result["start_time"]
        model_name = b_result["model_name"]
        if "device_id" in b_result:
            device_id = b_result["device_id"]
        else:
            device_id = "unknown"
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        replicas = json_data["dongles"][0]["replicas"]
        dongle_replicas = json_data["dongles"][0]["replicas"]
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        adv_interval = json_data["dongles"][0]["steps"][0]["adv_interval_max"]
        if "connection_interval_max" in json_data["dongles"][0]["steps"][0]:
            connection_interval_max = \
                json_data["dongles"][0]["steps"][0]["connection_interval_max"]
    if (scan_mode is not filter_scan_mode and filter_scan_mode is not None) \
            and (replicas is not filter_replicas and filter_replicas is not None):
        return
    adv_interval_int = int(adv_interval, 0)
    adv_interval_ms = (adv_interval_int * 625) / 1000
    soc = get_soc(model_name)
    model_name = get_pretty_name(model_name)
    result_dicts = []
    for step in phone_steps:
        # step_time = step["time"]/1000
        ble_operation = step["ble_operation"]
        wifi_state = step["wifi_state"]
        if "phone_step_result" in step:
            phone_step_result = step["phone_step_result"]
        else:
            phone_step_result = step
        wifi_results = phone_step_result["wifi_results"]
        for w in wifi_results:
            http_code = w["http_code"]
            latency = w["latency"]
            if http_code == 200:
                http_start = w["http_start"]
                http_stop = w["http_stop"]
                d = http_stop - http_start
                d = d / 1000  # in seconds
                size = 10485760  # bytes
                throughput = size / d
            else:
                throughput = 0
            result_dict = {'Phone Model': model_name,
                           'SoC': soc,
                           'WiFi State': wifi_state,
                           'http_code': http_code,
                           'throughput': throughput,
                           'latency': latency,
                           # 'Timestamp OS (ms)': t_os-benchmark_start_time,
                           'Benchmark': benchmark_name,
                           'Advertising Interval (ms)': adv_interval_ms,
                           'Scan Mode': scan_mode, 'Replicas': dongle_replicas}
    result_dicts.append(result_dict)
    data_pd = pd.DataFrame(result_dicts)
    pd_frames.append(data_pd)
    return pd_frames


def get_pd_frames(json_data, filter_benchmark=None, filter_scan_mode=None,
                  filter_replicas=None, filter_ble_operation='scanning'):
    if "benchmark_result" in json_data:
        b_result = json_data["benchmark_result"]
        benchmark_name = json_data["name"]
        benchmark_time = json_data["time"]
        benchmark_start_time = b_result["start_time"]
        try:
            api_version = b_result["api_version"]
        except:
            print "Malformed Result"
            print b_result
            return
        try:
            model_name = b_result["model_name"]
        except:
            print "Malformed Result"
            print b_result
            return
        if "device_id" in b_result:
            device_id = b_result["device_id"]
        else:
            device_id = "unknown"
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        replicas = json_data["dongles"][0]["replicas"]
        dongle_replicas = json_data["dongles"][0]["replicas"]
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        adv_interval = json_data["dongles"][0]["steps"][0]["adv_interval_max"]
        if "connection_interval_max" in json_data["dongles"][0]["steps"][0]:
            connection_interval_max = \
                json_data["dongles"][0]["steps"][0]["connection_interval_max"]
    else:
        # legacy
        benchmark_name = json_data["benchmark"]["name"]
        benchmark_time = json_data["benchmark"]["time"]
        benchmark_start_time = float(json_data["start_time"])
        # benchmark_repetitions = json_data["benchmark"]["repetitions"]
        model_name = json_data["model_name"]
        phone_steps = json_data["benchmark"]["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        replicas = json_data["benchmark"]["dongles"][0]["replicas"]
        dongle_replicas = json_data["benchmark"]["dongles"][0]["replicas"]
        phone_steps = json_data["benchmark"]["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        adv_interval = \
            json_data["benchmark"]["dongles"][0]["steps"][0]["adv_interval_max"]
    if model_name == 'Huawei Nexus 6P':  # these results cannot be trusted...
        return
    if (scan_mode is not filter_scan_mode and filter_scan_mode is not None) \
            and (replicas is not filter_replicas and filter_replicas is not None):
        return
    soc = get_soc(model_name)
    model_name = get_pretty_name(model_name)
    # FIXME needs to be here but somehow exception does not work...
    try:
        if benchmark_name[6] == 'm':
            distance = float(benchmark_name[5])
        else:
            distance = float(benchmark_name[5:7])
    except:
        distance = 1.0
    # distance = 1.0
    # benchmark_repetitions = json_data["benchmark"]["repetitions"]
    dongle_name = "BLEva"
    adv_interval_int = int(adv_interval, 0)
    adv_interval_ms = (adv_interval_int * 625) / 1000
    t_c0 = 0.0
    t_c1 = 0.0
    t_s0 = 0.0
    # t_d0 = 0.0
    t_r0 = 0.0
    t_r1 = 0.0
    t_w0 = 0.0
    t_w1 = 0.0
    pd_frames = []
    gatt_results = []
    if filter_benchmark == "battery":
        result_dicts = []
        b = b_result["start_battery_level"] * 100
        diff = 100.0 - b
        b = b + diff
        p = 0
        t = 0.0
        result_dict = {'Phone Model': model_name, 'SoC': soc, 'Time (h)': t,
                       'Battery Level (%)': b, 'Received Packages': p,
                       'Scan Mode': scan_mode}
        result_dicts.append(result_dict)
        if "batteryResults" in b_result:
            for r in b_result["batteryResults"]:
                b = (r["battery"] * 100) + diff
                p = r["receivedPackages"]
                t = (r["time"] - benchmark_start_time) / 1000.0 / 60.0 / 60.0
                if t <= 5.1:
                    result_dict = {'Phone Model': model_name, 'SoC': soc,
                                   'Time (h)': t, 'Battery Level (%)': b,
                                   'Received Packages': p,
                                   'Scan Mode': scan_mode}
                    result_dicts.append(result_dict)
        else:
            # legacy for when we did not collect every min
            b = (b_result["stop_battery_level"] * 100) + diff
            p = 0
            t = 18000000.0 / 1000.0 / 60.0 / 60.0
            result_dict = {'Phone Model': model_name,
                           'SoC': soc,
                           'Time (h)': t,
                           'Battery Level (%)': b,
                           'Received Packages': p,
                           'Scan Mode': scan_mode}
            result_dicts.append(result_dict)
        data_pd = pd.DataFrame(result_dicts)
        pd_frames.append(data_pd)
        return pd_frames
    for step in phone_steps:
        # step_time = step["time"]/1000
        ble_operation = step["ble_operation"]
        wifi_state = step["wifi_state"]
        step_time = step['time']
        if "phone_step_result" in step:
            phone_step_result = step["phone_step_result"]
        else:
            phone_step_result = step
        if ble_operation == "scanning" and filter_benchmark is not "gatt":
            if "scan_results" in phone_step_result:
                results = phone_step_result["scan_results"]
            elif "results" in phone_step_result:
                results = phone_step_result["results"]
            else:
                raise
            result_dicts = []
            if filter_benchmark == "prr":
                for r in xrange(0, dongle_replicas):
                    r_name = dongle_name + str(0) + str(r)
                    rssis = []
                    packages = 0.0
                    found = False
                    for result in results:
                        if "mScanRecord" in result:
                            scan_record = result["mScanRecord"]
                            if "mDeviceName" in scan_record:
                                if r_name in scan_record["mDeviceName"]:
                                    t_os = result["mTimestampOSMillis"]
                                    if (t_os - benchmark_start_time) > 0:
                                        found = True
                                        rssis.append(result["mRssi"])
                                        packages = packages + 1
                        elif "device_name" in result:
                            if r_name in result["device_name"]:
                                found = True
                                t_os = float(result["timestamp_os_millis"])
                                if "rssi" in result:
                                    rssi = result["rssi"]
                                elif "mRssi" in result:
                                    rssi = result["mRssi"]
                                rssis.append(rssi)
                                packages = packages + 1.0
                    if found:
                        rssi_avg = sum(rssis) / float(len(rssis))
                        send_packages = (step_time / adv_interval_ms)  # *3 NOTE actually 3 packets are sent
                        prr = packages / send_packages * 100
                    else:
                        rssi_avg = -256
                        prr = 0.0
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'API Version': api_version,
                                   'WiFi State': wifi_state,
                                   'Peripheral Name': r_name,
                                   # 'Timestamp OS (ms)': t_os-benchmark_start_time,
                                   'RSSI Mean (dbm)': rssi_avg,
                                   'PRR (%)': prr,
                                   'Benchmark': benchmark_name,
                                   'Received Packages': packages,
                                   'Advertising Interval (ms)': adv_interval_ms,
                                   'Scan Mode': scan_mode, 'Replicas': dongle_replicas, 'Distance (m)': distance}
                    result_dicts.append(result_dict)
            else:
                for r in xrange(0, dongle_replicas):
                    found = False
                    r_name = dongle_name + str(0) + str(r)
                    if filter_benchmark == "rssi":
                        r_name = "EST"
                    for result in results:
                        t_os = 0.0
                        rssi = -256.0
                        if "rssi" in result:
                            rssi = result["rssi"]
                        elif "mRssi" in result:
                            rssi = result["mRssi"]
                        if "mScanRecord" in result:
                            scan_record = result["mScanRecord"]
                            if "mDeviceName" in scan_record:
                                if r_name in scan_record["mDeviceName"]:
                                    if filter_benchmark == "rssi":
                                        if "mDevice" in result:
                                            mDevice = result["mDevice"]
                                            if mDevice["mAddress"] == "D3:75:6A:0A:5B:83":
                                                t_os = float(result["mTimestampOSMillis"])
                                    else:
                                        t_os = float(result["mTimestampOSMillis"])
                        elif "device_name" in result:
                            if r_name in result["device_name"]:
                                t_os = float(result["timestamp_os_millis"])
                        if (t_os - benchmark_start_time) > 0:
                            found = True
                            result_dict = {'Phone Model': model_name,
                                           'Device ID': device_id,
                                           'SoC': soc,
                                           'WiFi State': wifi_state,
                                           'Peripheral Name': r_name,
                                           'OS Timestamp (ms)': t_os - benchmark_start_time,
                                           'Abs OS Timestamp (ms)': t_os,
                                           'Time of Day': get_time_of_day(t_os),
                                           'RSSI (dBm)': rssi,
                                           'Benchmark': benchmark_name,
                                           'Advertising Interval (ms)': adv_interval_ms,
                                           'Scan Mode': scan_mode,
                                           'Replicas': dongle_replicas,
                                           'Distance (m)': distance}
                            result_dicts.append(result_dict)
                            if filter_benchmark == 'first':
                                break
                            if filter_benchmark == 'distribution':
                                benchmark_start_time = t_os
            # if (not found):
                # result_dict = { 'Phone Model': model_name,
                                # 'SoC': soc,
                                # 'Peripheral Name': r_name,
                                # 'OS Timestamp (ms)': 30000,
                                # 'RSSI (dBm)': 0,
                                # 'Benchmark': benchmark_name,
                                # 'Advertising Interval (ms)': adv_interval_ms,
                                # 'Scan Mode': scan_mode,
                                # 'Replicas': dongle_replicas,
                                # 'Distance (m)': distance}
                # result_dicts.append(result_dict)
            data_pd = pd.DataFrame(result_dicts)
            # if filter_benchmark == "rssi":
                # a = data_pd["RSSI (dBm)"]
                # f = gaussian_filter(a, sigma=10)
                # data_pd["RSSI (dBm)"] = f
                # print a
                # print f
            pd_frames.append(data_pd)
        elif filter_benchmark == "gatt":
            print "GATT"
            # print step
            if "gatt_results" in phone_step_result:
                print "gatt_results"
                for result in phone_step_result["gatt_results"]:
                    print result
                    if result["time_connecting"] != 0:
                        t_c0 = result["time_connecting"]
                        # result_dict = {'Phone Model': model_name,
                                        # 'GATT Operation': "Connecting",
                                        # 'Time (ms)': 0}
                        # gatt_results.append(result_dict)
                    if result["time_connected"] != 0:
                        t_c1 = result["time_connected"]
                        result_dict = {'Phone Model': model_name,
                                       'SoC': soc,
                                       'WiFi State': wifi_state,
                                       'Operation': "Connected",
                                       'Connection Interval (s)': connection_interval_max / 1000.0,
                                       'Time (s)': (t_c1 - t_c0) / 1000.0}
                        gatt_results.append(result_dict)
                    if result["time_services_discovered"] != 0:
                        t_s0 = result["time_services_discovered"]
                        result_dict = {'Phone Model': model_name,
                                       'SoC': soc,
                                       'WiFi State': wifi_state,
                                       'Operation': "Services Discovered",
                                       'Connection Interval (s)': connection_interval_max / 1000.0,
                                       'Time (s)': (t_s0 - t_c1) / 1000.0}  # t_c0
                        gatt_results.append(result_dict)
                    # if result["time_disconnected"] != 0:
                        # t_d0 = result["time_disconnected"]
                        # result_dict = {'Phone Model': model_name,
                                        # 'GATT Operation': "Disconnected",
                                        # 'Time (ms)': t_d0-t_c0}
                        # gatt_results.append(result_dict)
                    if result["time_read_request_start"] != 0:
                        t_r0 = result["time_read_request_start"]
                        # result_dict = {'Phone Model': model_name,
                                        # 'GATT Operation': "Read Started",
                                        # 'Time (ms)': t_r0-t_c0}
                        # gatt_results.append(result_dict)
                    if result["time_read_request_done"] != 0:
                        t_r1 = result["time_read_request_done"]
                        result_dict = {'Phone Model': model_name,
                                       'SoC': soc,
                                       'WiFi State': wifi_state,
                                       'Operation': "Read",
                                       'Connection Interval (s)': connection_interval_max / 1000.0,
                                       'Time (s)': (t_r1 - t_r0) / 1000.0}  # t_c0
                        gatt_results.append(result_dict)
                    if result["time_write_request_start"] != 0:
                        t_w0 = result["time_write_request_start"]
                        # result_dict = {'Phone Model': model_name,
                                        # 'GATT Operation': "Write Started",
                                        # 'Time (ms)': t_w0-t_c0}
                        # gatt_results.append(result_dict)
                    if result["time_write_request_done"] != 0:
                        t_w1 = result["time_write_request_done"]
                        result_dict = {'Phone Model': model_name,
                                       'SoC': soc,
                                       'WiFi State': wifi_state,
                                       'Operation': "Write",
                                       'Connection Interval (s)': connection_interval_max / 1000.0,
                                       'Time (s)': (t_w1 - t_w0) / 1000.0}  # t_c0
                        gatt_results.append(result_dict)
            data_pd = pd.DataFrame(gatt_results)
            pd_frames.append(data_pd)
        else:
            print "skipped this result:"
            print model_name
            print benchmark_name
    return pd_frames


def get_gatt_frames(json_data, filter_benchmark=None, filter_scan_mode=None,
                    filter_replicas=None, filter_ble_operation='scanning'):
    if "benchmark_result" in json_data:
        b_result = json_data["benchmark_result"]
        benchmark_name = json_data["name"]
        benchmark_time = json_data["time"]
        benchmark_start_time = b_result["start_time"]
        model_name = b_result["model_name"]
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        replicas = json_data["dongles"][0]["replicas"]
        dongle_replicas = json_data["dongles"][0]["replicas"]
        phone_steps = json_data["phone"]["steps"]
        scan_mode = phone_steps[0]["scan_mode"]
        adv_interval = json_data["dongles"][0]["steps"][0]["adv_interval_max"]
        if "connection_interval_max" in json_data["dongles"][0]["steps"][0]:
            connection_interval_max = \
                json_data["dongles"][0]["steps"][0]["connection_interval_max"]
    if (scan_mode is not filter_scan_mode and filter_scan_mode is not None) \
            and (replicas is not filter_replicas and filter_replicas is not None):
        return
    soc = get_soc(model_name)
    model_name = get_pretty_name(model_name)
    try:
        if benchmark_name[6] == 'm':
            distance = float(benchmark_name[5])
        else:
            distance = float(benchmark_name[5:7])
    except:
        distance = 1.0
    # benchmark_repetitions = json_data["benchmark"]["repetitions"]
    dongle_name = "BLEva"
    adv_interval_int = int(adv_interval, 0)
    adv_interval_ms = (adv_interval_int * 625) / 1000
    t_c0 = 0.0
    t_c1 = 0.0
    t_s0 = 0.0
    # t_d0 = 0.0
    t_r0 = 0.0
    t_r1 = 0.0
    t_w0 = 0.0
    t_w1 = 0.0
    pd_frames = []
    gatt_results = []
    initial_wifi_state = ""
    for step in phone_steps:
        # step_time = step["time"]/1000
        if initial_wifi_state == "":
            wifi_state = step["wifi_state"]
            initial_wifi_state = wifi_state
        else:
            wifi_state = initial_wifi_state
        ble_operation = step["ble_operation"]
        if "phone_step_result" in step:
            phone_step_result = step["phone_step_result"]
        else:
            phone_step_result = step
        # print step
        if "gatt_results" in phone_step_result:
            for result in phone_step_result["gatt_results"]:
                if result["time_connecting"] != 0:
                    t_c0 = result["time_connecting"]
                    # result_dict = {'Phone Model': model_name,
                                    # 'GATT Operation': "Connecting",
                                    # 'Time (ms)': 0}
                    # gatt_results.append(result_dict)
                if result["time_connected"] != 0:
                    t_c1 = result["time_connected"]
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Connected",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_c1 - t_c0) / 1000.0}
                    gatt_results.append(result_dict)
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Connected Sum",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_c1 - t_c0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                if result["time_services_discovered"] != 0:
                    t_s0 = result["time_services_discovered"]
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Services Discovered",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_s0 - t_c1) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Services Discovered Sum",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_s0 - t_c0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                # if result["time_disconnected"] != 0:
                    # t_d0 = result["time_disconnected"]
                    # result_dict = {'Phone Model': model_name,
                                    # 'GATT Operation': "Disconnected",
                                    # 'Time (ms)': t_d0-t_c0}
                    # gatt_results.append(result_dict)
                if result["time_read_request_start"] != 0:
                    t_r0 = result["time_read_request_start"]
                    # result_dict = {'Phone Model': model_name,
                                    # 'GATT Operation': "Read Started",
                                    # 'Time (ms)': t_r0-t_c0}
                    # gatt_results.append(result_dict)
                if result["time_read_request_done"] != 0:
                    t_r1 = result["time_read_request_done"]
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Read",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_r1 - t_r0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Read Sum",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_r1 - t_c0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                if result["time_write_request_start"] != 0:
                    t_w0 = result["time_write_request_start"]
                    # result_dict = {'Phone Model': model_name,
                                    # 'GATT Operation': "Write Started",
                                    # 'Time (ms)': t_w0-t_c0}
                    # gatt_results.append(result_dict)
                if result["time_write_request_done"] != 0:
                    t_w1 = result["time_write_request_done"]
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Write",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_w1 - t_w0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
                    result_dict = {'Phone Model': model_name,
                                   'SoC': soc,
                                   'WiFi State': wifi_state,
                                   'Operation': "Write Sum",
                                   'Connection Interval (s)': connection_interval_max / 1000.0,
                                   'Time (s)': (t_w1 - (t_r1 - t_r0) - t_c0) / 1000.0}  # t_c0
                    gatt_results.append(result_dict)
            # calculate sum of write/read
    data_pd = pd.DataFrame(gatt_results)
    pd_frames.append(data_pd)
    return pd_frames


def get_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
        return data


def get_time_of_day(t):
    utc_dt = pytz.utc.localize(datetime.datetime.utcfromtimestamp(int(t / 1000)))
    copenhagen_dt = utc_dt.astimezone(pytz.timezone("Europe/Copenhagen"))
    hour = int(copenhagen_dt.strftime('%H'))
    if hour < 11:
        c = "Morning"
    elif hour < 15:
        c = "Noon"
    elif hour < 20:
        c = "Afternoon"
    else:
        c = "Night"
    return c


def set_style(font_scale=1.0, style_rc=None):
    # This sets reasonable defaults for font size for
    # a figure that will go in a paper
    sns.set_context("paper")
    # Set the font to be serif, rather than sans
    # sns.set(font='serif')
    # sns.set(font_scale=font_scale)
    # if style_rc != None:
    sns.set(font='serif', font_scale=font_scale, rc=style_rc)
    sns.set_style('whitegrid', {'axes.edgecolor': '.0', 'grid.linestyle': u'--',
                                'grid.color': '.8', 'xtick.color': '.15',
                                'xtick.minor.size': 3.0, 'xtick.major.size':
                                6.0, 'ytick.color': '.15', 'ytick.minor.size':
                                3.0, 'ytick.major.size': 6.0,
                                "font.family": "serif",
                                "font.serif": ["Times", "Palatino", "serif"]
                                })
    # matplot_colors = ["b", "g", "r", "c", "m", "y", "k", "w"]
    # sns.set_palette(matplot_colors)
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42


def set_hatches_box(ax):
    hatches = itertools.cycle(['//', '////', '++', '--', 'xx', '\\\\', '**', 'oo', 'OO',
                               '.'])
    for i, box in enumerate(ax.artists):
        hatch = next(hatches)
        box.set(hatch=hatch)


def set_hatches_bar(ax):
    hatches = itertools.cycle(['//', '////', '++', '--', 'xx', '\\\\', '**', 'oo', 'OO',
                               '.'])
    for i, bar in enumerate(ax.patches):
        hatch = next(hatches)
        bar.set(hatch=hatch)


def set_hatches_legend(recs):
    hatches = itertools.cycle(['//', '////', '++', '--', 'xx', '\\\\', '**', 'oo', 'OO',
                               '.'])
    for i, rec in enumerate(recs):
        hatch = next(hatches)
        rec.set_hatch(hatch)


def set_colors():
    # matplot_colors = ["b", "g", "r", "c", "m", "y", "k", "w"]
    # p = sns.color_palette("husl", 10)
    # sns.set_palette(p)
    sns.set_palette("colorblind")
