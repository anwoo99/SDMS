from utils.config import *

def parse_fix_message(split_value, message):
    # FIX 메시지를 태그-값 쌍으로 분리
    tags_values = message.split(split_value)

    # 태그-값 쌍을 딕셔너리로 저장
    fix_dict = {}
    for tag_value in tags_values:
        if '=' in tag_value:
            tag, value = tag_value.split('=')
            fix_dict[int(tag)] = value

    return fix_dict

def dict_to_fix(split_value, data):
    try:
        fix_message = ""
        for tag, value in data.items():
            fix_message += f"{tag}={value}{split_value}"
        return fix_message.rstrip(split_value)
    except Exception as err:
        raise