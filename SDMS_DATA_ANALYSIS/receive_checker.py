from SDMS_DATA_ANALYSIS.config import *

######################
# 절대 수정하지 마세요.
TIME_CLASS = 2
######################

def rc_get_code(formatter, config, data):
    try:
        format = formatter.format
        code = None

        if format == "old" or format == "ext":
            code = formatter.parser(config, data, "code")
        elif format == "hana":
            code = formatter.parser(config, data, "inst_code")
        else:
            raise

        if code is None:
            raise

        return code
    except Exception as err:
        raise


def rc_get_T_class(target_time=None):
    try:
        if target_time is None:
            target_time = time.localtime()
        elapsed_minutes = target_time.tm_hour * 60 + target_time.tm_min
        return elapsed_minutes // TIME_CLASS
    except Exception as err:
        raise


def rc_get_wday(target_time=None):
    try:
        if target_time is None:
            target_time = time.localtime()
        return target_time.tm_wday
    except Exception as err:
        raise


def rc_get_update_date(target_time=None):
    try:
        if target_time is None:
            target_time = time.localtime()
        year = target_time.tm_year
        month = target_time.tm_mon
        day = target_time.tm_mday
        return year * 10000 + month * 100 + day
    except Exception as err:
        raise


def rc_get_update_datetime(target_time=None):
    try:
        if target_time is None:
            target_time = time.localtime()

        year = target_time.tm_year
        month = target_time.tm_mon
        day = target_time.tm_mday
        hour = target_time.tm_hour
        minute = target_time.tm_min
        second = target_time.tm_sec

        update_datetime = f"{year}/{month:02d}/{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
        return update_datetime
    except Exception as err:
        raise


def rc_get_label(formatter, data):
    try:
        label = {
            "exnm": "",
            "code": "",
            "type": "",
            "T_class": 0,
            "T_wday": -1,
        }
        config, class_name, data_type = formatter.classify(data)

        label["exnm"] = formatter.exch_name

        if data_type == "QUOTE" or data_type == "DEPTH":
            label["code"] = rc_get_code(formatter, config, data)
        else:
            label["code"] = None

        label["type"] = data_type
        label["T_class"] = rc_get_T_class()
        label["T_wday"] = rc_get_wday()

        return label
    except Exception as err:
        raise


def rc_int2str(number):
    string = ""

    while number > 0:
        remainder = number % 100
        ch = chr(remainder)
        string = ch + string
        number //= 100
    return string


def rc_str2int(string):
    value = 0
    for index, ch in enumerate(string.upper()):
        value += ord(ch) * (10 ** ((len(string) - index - 1) * 2))
    return value


def rc_encoding(rc_conv_data_map):
    try:
        X_real = []
        X_train = []

        for _, converted_data in rc_conv_data_map.items():
            exnm_encoded = rc_str2int(converted_data["exnm"])
            if converted_data["code"] is None:
                code_encoded = 0
            else:
                code_encoded = rc_str2int(converted_data["code"].strip())
            type_encoded = rc_str2int(converted_data["type"])

            if converted_data["check_count"] >= APP_INFO["receive_checker"]["classification"]:
                X_real.append([exnm_encoded, code_encoded, type_encoded, converted_data["T_class"],
                              converted_data["T_wday"], converted_data["receive_count"]])
            else:
                X_train.append([exnm_encoded, code_encoded, type_encoded, converted_data["T_class"],
                               converted_data["T_wday"], converted_data["receive_count"]])

        # 스케일링할 데이터 추출
        X_real = np.array(X_real)
        X_train = np.array(X_train)

        return X_real, X_train
    except Exception as err:
        raise


def rc_save_data(data_filename, data):
    try:
        if os.path.exists(data_filename):
            existing_data = np.load(data_filename)
            all_combined_data = np.concatenate((existing_data, data), axis=0)
        else:
            all_combined_data = data

        np.save(data_filename, all_combined_data)

        return all_combined_data
    except Exception as err:
        raise


def rc_update_converted_data(rc_conv_data_map, label):
    try:
        T_class = label["T_class"]
        if T_class not in rc_conv_data_map:
            rc_conv_data_map[T_class] = {}

        rc_conv_data_map_T_class = rc_conv_data_map[T_class]

        key = (label["exnm"], label["code"], label["type"],
               label["T_class"], label["T_wday"])
        if key in rc_conv_data_map_T_class:
            converted_data = rc_conv_data_map_T_class[key]
            curr_update_date = rc_get_update_date()
            converted_data["receive_count"] += 1

            if curr_update_date != converted_data["update_date"]:
                converted_data["check_count"] += 1
                converted_data["receive_count"] = 1
                converted_data["update_date"] = curr_update_date
            return converted_data

        label["check_count"] = 1
        label["receive_count"] = 1
        label["update_date"] = rc_get_update_date()
        rc_conv_data_map_T_class[key] = label

    except Exception as err:
        raise


def rc_anomaly_process(alerter_sock, outlier_data):
    try:
        # 0. 이상치가 어떤 데이터인지 exnm, code 등 전부 출력
        exnm = rc_int2str(outlier_data[0])
        code = rc_int2str(outlier_data[1])
        type = rc_int2str(outlier_data[2])
        T_class = outlier_data[3]
        receive_count = outlier_data[4]
        error_datetime = rc_get_update_datetime()

        if code is None:
            desc = RCV_ERROR_CODE["desc"] + type
        else:
            desc = RCV_ERROR_CODE["desc"] + code

        alert_data = {
            "error_code": RCV_ERROR_CODE["code"],
            "error_desc": desc,
            "error_time": error_datetime,
            "exnm": exnm,
            "code": code,
            "type": type,
        }

        # 1. Outlier Data에 대하여 진짜 이상치가 맞는지 추가 검증 로직 추가

        # 2. Alert 전달
        json_alert_data = json.dumps(alert_data) + '\0'
        alerter_sock.client_feeder(json_alert_data.encode())
    except Exception as err:
        raise


def preprocess_receive_checker(formatter, data, rc_conv_data_attr, thread):
    try:
        label = rc_get_label(formatter, data)
        rc_update_converted_data(rc_conv_data_attr["data"], label)

        try:
            if not thread.is_alive():
                thread.start()
        except Exception: 
            pass

    except Exception as err:
        raise


def receive_checker(process, alerter_sock, formatter, rc_conv_data_attr):
    try:
        log(APP_NAME, MUST, f"receive_checker() start for {formatter.id}..!")
        is_checked = False

        model_filename = os.path.join(
            DATA_MODEL_DIR, f"RECV_CHK_MODEL_{formatter.id}.pk1")
        receive_checker_train_data_filename = os.path.join(
            DATA_NUMP_DIR, f"receive_checker_train_combined_data_{formatter.id}.npy")
        receive_checker_anomly_data_filename = os.path.join(
            DATA_NUMP_DIR, f"receive_checker_anomly_combined_data_{formatter.id}.npy")

        rc_conv_data_filename = rc_conv_data_attr["filename"]
        rc_conv_data_map = rc_conv_data_attr["data"]

        while process["Running"] == 1:
            current_time = time.localtime()
            curr_T_class = rc_get_T_class(target_time=current_time)

            one_minute_before_time = time.localtime(
                time.mktime(current_time) - 60)
            before_T_class = rc_get_T_class(target_time=one_minute_before_time)

            two_minute_after_time = time.localtime(
                time.mktime(current_time) + 60 * 2)
            next_T_class = rc_get_T_class(target_time=two_minute_after_time)

            # Receiving Count of Next T Class initializing
            if next_T_class in rc_conv_data_map:
                rc_conv_data_map[next_T_class]["receive_count"] = 0

            if before_T_class != curr_T_class:
                if not is_checked:
                    if not rc_conv_data_map:
                        continue

                    X_real, X_train = rc_encoding(
                        rc_conv_data_map.get(before_T_class, {}))

                    # Load the receive checker model
                    if os.path.exists(model_filename):
                        clf = joblib.load(model_filename)
                    else:
                        clf = IsolationForest(n_estimators=ISOLATION_FOREST["n_estimators"],
                                              max_samples=ISOLATION_FOREST["max_samples"],
                                              contamination=ISOLATION_FOREST["contamination"],
                                              max_features=ISOLATION_FOREST["max_features"],
                                              bootstrap=ISOLATION_FOREST["bootstrap"],
                                              n_jobs=ISOLATION_FOREST["n_jobs"],
                                              random_state=ISOLATION_FOREST["random_state"],
                                              verbose=ISOLATION_FOREST["verbose"],
                                              warm_start=ISOLATION_FOREST["warm_start"]
                                              )

                        if os.path.exists(receive_checker_train_data_filename):
                            existing_data = np.load(
                                receive_checker_train_data_filename)

                            if existing_data.size > 0:
                                clf.fit(existing_data)

                    if X_train.size > 0:
                        clf.fit(X_train)
                        rc_save_data(
                            receive_checker_train_data_filename, X_train)

                    if X_real.size > 0:
                        Y_real = clf.predict(X_real)

                        for ii, y in enumerate(Y_real):
                            if y == -1:
                                rc_anomaly_process(alerter_sock, X_real[ii])

                        # 이상치 데이터 저장
                        anomalous_indices = np.where(Y_real == -1)[0]
                        rc_save_data(
                            receive_checker_anomly_data_filename, X_real[anomalous_indices])

                        # X_real 중 이상치가 아닌 데이터는 학습
                        non_anomalous_indices = np.where(
                            Y_real != -1)[0]  # 이상치로 판별되지 않은 데이터 인덱스
                        # 이상치로 판별되지 않은 데이터만 선택
                        X_real_non_anomalous = X_real[non_anomalous_indices]
                        rc_save_data(
                            receive_checker_train_data_filename, X_real_non_anomalous)

                        # 모델 재학습
                        clf.fit(X_real_non_anomalous)

                    # Save the updated model
                    joblib.dump(clf, model_filename)
                    is_checked = True

                    dump_data_to_file(rc_conv_data_map, rc_conv_data_filename)
                else:
                    time.sleep(1)
            else:
                is_checked = False
                time.sleep(1)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        dump_data_to_file(rc_conv_data_map, rc_conv_data_filename)
        sys.exit()
