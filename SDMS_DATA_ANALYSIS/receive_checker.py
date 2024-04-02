from SDMS_DATA_ANALYSIS.config import *

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
        return elapsed_minutes // 2 # 절대 수정하지 마세요.
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
        }
        config, class_name, data_type = formatter.classify(data)

        label["exnm"] = formatter.exch_name
        
        if data_type == "QUOTE" or data_type == "DEPTH":
            label["code"] = rc_get_code(formatter, config, data)
        else:
            label["code"] = None

        label["type"] = data_type
        label["T_class"] = rc_get_T_class()

        return label
    except Exception as err:
        raise

def rc_find_mapping(rc_data_index_map, converted_data, target, is_str2int=1):
    try:
        # 문자열을 정수로 매핑하는 딕셔너리
        if is_str2int:
            if target not in rc_data_index_map:
                rc_data_index_map[target] = {}
            
            if converted_data not in rc_data_index_map[target]:
                # 새로운 매핑을 생성하여 반환
                new_mapping = len(rc_data_index_map[target]) + 1
                rc_data_index_map[target][converted_data] = new_mapping
                return new_mapping
            else:
                # 이미 존재하는 매핑을 반환
                return rc_data_index_map[target][converted_data]
        else:
            # 정수를 문자열로 역매핑
            return [key for key, value in rc_data_index_map[target].items() if value == converted_data][0]
    except Exception as err:
        raise

def rc_encoding(converted_data_map, rc_data_index_map):
    try:
        X_real = []
        X_train = []
        scaler = StandardScaler()  # StandardScaler 객체 생성
        
        for _, converted_data in converted_data_map.items():
            exnm_encoded = rc_find_mapping(rc_data_index_map, converted_data["exnm"], "exnm", 1)
            code_encoded = rc_find_mapping(rc_data_index_map, converted_data["code"], "code", 1)
            type_encoded = rc_find_mapping(rc_data_index_map, converted_data["type"], "type", 1)
            
            if converted_data["check_count"] >= APP_INFO["receive_checker"]["classification"]:
                X_real.append([exnm_encoded, code_encoded, type_encoded, converted_data["T_class"], converted_data["receive_count"]])
            else:
                X_train.append([exnm_encoded, code_encoded, type_encoded, converted_data["T_class"], converted_data["receive_count"]])
        
        # 스케일링할 데이터 추출
        X_real = np.array(X_real)
        X_train = np.array(X_train)
        
        # # X_train 데이터로 평균과 표준 편차를 계산하여 스케일링
        # if len(X_train) > 0:
        #     X_train_scaled = scaler.fit_transform(X_train[:, :-1])  # 마지막 열인 receive_count 제외
        #     X_train_scaled = np.column_stack((X_train_scaled, X_train[:, -1]))  # receive_count 추가
        # else:
        #     X_train_scaled = []
        
        # # X_real 데이터를 이전에 계산한 평균과 표준 편차로 스케일링
        # if len(X_real) > 0:
        #     X_real_scaled = scaler.transform(X_real[:, :-1])  # 마지막 열인 receive_count 제외
        #     X_real_scaled = np.column_stack((X_real_scaled, X_real[:, -1]))  # receive_count 추가
        # else:
        #     X_real_scaled = []

        # return np.array(X_real_scaled), np.array(X_train_scaled), X_real, X_train
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

def rc_update_converted_data(converted_data_map, label):
    try:
        T_class = label["T_class"]
        if T_class not in converted_data_map:
            converted_data_map[T_class] = {}
        
        converted_data_map_T_class = converted_data_map[T_class]

        key = (label["exnm"], label["code"], label["type"], label["T_class"])
        if key in converted_data_map_T_class:
            converted_data = converted_data_map_T_class[key]
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
        converted_data_map_T_class[key] = label

    except Exception as err:
        raise

def rc_anomaly_process(rc_alerter_sock, rc_data_index_map, outlier_data):
    try:
        # 0. 이상치가 어떤 데이터인지 exnm, code 등 전부 출력
        exnm = rc_find_mapping(rc_data_index_map, outlier_data[0], "exnm", 0)
        code = rc_find_mapping(rc_data_index_map, outlier_data[1], "code", 0).strip()
        type = rc_find_mapping(rc_data_index_map, outlier_data[2], "type", 0)
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
        rc_alerter_sock.client_feeder(json_alert_data.encode())
    except Exception as err:
        raise

def rc_sleep(current_time, start_day, start_time, end_day, end_time):
    days = {"Sun": 0, "Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6}
    start_day_index = days[start_day]
    end_day_index = days[end_day]

    # Convert start_time and end_time to hours and minutes
    start_hour, start_minute = map(int, start_time.split(":"))
    end_hour, end_minute = map(int, end_time.split(":"))

    current_day = current_time.tm_wday
    current_hour = current_time.tm_hour
    current_minute = current_time.tm_min

    if current_day == start_day_index:
        if current_hour < start_hour or (current_hour == start_hour and current_minute < start_minute):
            return True
    elif current_day == end_day_index:
        if current_hour > end_hour or (current_hour == end_hour and current_minute >= end_minute):
            return True
    elif current_day > start_day_index and current_day < end_day_index:
        return True
    
    return False

def preprocess_receive_checker(formatter, data, converted_data_map):
    try:
        label = rc_get_label(formatter, data)
        rc_update_converted_data(converted_data_map, label)
    except Exception as err:
        raise


def receive_checker(process, rc_alerter_sock, model_filename, receive_checker_train_data_filename, receive_checker_anomly_data_filename, converted_data_map, rc_data_index_map):
    try:
        log(APP_NAME, MUST, f"receive_checker() start using {model_filename}..!")
        is_checked = False
        
        while process["Running"] == 1: 
            current_time = time.localtime()

            is_sleep = rc_sleep(current_time, "Sat", "09:00", "Mon", "06:00")

            if is_sleep:
                time.sleep(1)

            curr_T_class = rc_get_T_class(target_time=current_time)
    
            one_minute_before_time = time.localtime(time.mktime(current_time) - 60)
            before_T_class = rc_get_T_class(target_time=one_minute_before_time)

            two_minute_after_time = time.localtime(time.mktime(current_time) + 60 * 2)
            next_T_class = rc_get_T_class(target_time=two_minute_after_time)

            # Receiving Count of Next T Class initializing
            if next_T_class in converted_data_map:
                converted_data_map[converted_data_map]["receive_count"] = 0
    
            if before_T_class != curr_T_class:
                if not is_checked:
                    if not converted_data_map:
                        continue
                        
                    X_real, X_train = rc_encoding(converted_data_map.get(before_T_class, {}), rc_data_index_map)
                    
                    # Load the receive checker model
                    if os.path.exists(model_filename):
                        clf = joblib.load(model_filename)
                    else:
                        clf = IsolationForest(contamination=0.1, random_state=42)

                    if X_train.size > 0:
                        clf.fit(X_train)
                        rc_save_data(receive_checker_train_data_filename, X_train)

                    if X_real.size > 0:
                        Y_real = clf.predict(X_real)
        
                        for ii, y in enumerate(Y_real):
                            if y == -1:
                                rc_anomaly_process(rc_alerter_sock, rc_data_index_map, X_real[ii])

                        # 이상치 데이터 저장
                        anomalous_indices = np.where(Y_real == -1)[0]
                        rc_save_data(receive_checker_anomly_data_filename, X_real[anomalous_indices])
                        
                        # X_real 중 이상치가 아닌 데이터는 학습
                        non_anomalous_indices = np.where(Y_real != -1)[0]  # 이상치로 판별되지 않은 데이터 인덱스
                        X_real_non_anomalous = X_real[non_anomalous_indices]  # 이상치로 판별되지 않은 데이터만 선택
                        rc_save_data(receive_checker_train_data_filename, X_real_non_anomalous)
        
                        # 모델 재학습
                        clf.fit(X_real_non_anomalous)

                    # Save the updated model
                    joblib.dump(clf, model_filename)
                    is_checked = True
                else:
                    time.sleep(1)
            else:
                is_checked = False
                time.sleep(1)
        
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()