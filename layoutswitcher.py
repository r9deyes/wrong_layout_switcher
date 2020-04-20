#! python3
import re
import sys
import fileinput

TAG = "russian"
opened_tag = '<{}>'.format(TAG)
closed_tag = '</{}>'.format(TAG)
TOO_MUCH_INTO_TAG = 5
rus_low_case = 'йцукенгшщзхъфывапролджэячсмитьбю'
eng_low_case = "qwertyuiop[]asdfghjkl;'zxcvbnm,."
rus_up_case =  'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'
eng_up_case =  'QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>'
trans_table = str.maketrans(eng_low_case + eng_up_case,
                            rus_low_case + rus_up_case)


def switch(text):
    # type: (str) -> str
    """

    :param str text: str
    :return str:
    """
    return text.translate(trans_table)


def get_tag_text(line, start=0, finish=-1):
    """

    :param finish:
    :param start:
    :type line: str
    :return str:
    """
    result = []
    start_switch = len(opened_tag) + start
    finish_switch = len(closed_tag) + finish
    if start >= 0 and finish >= 0:
        result = [
            line[:start],
            switch(line[start_switch: finish]),
            # line[finish_switch:],
        ]
    elif start >= 0 > finish:
        result = [
            line[:start],
            switch(line[start_switch:]),
        ]
    elif start < 0 and finish < 0:
        result = [
            switch(line),
        ]
    elif start < 0 <= finish:
        result = [
            switch(line[:finish]),
            line[finish_switch:]
        ]
    return ''.join(result)


def edit_file(*args, **kwargs):
    """

    :param args:
    :param kwargs:
    :return None:
    """
    into_tag = False
    tag_lines_count = 0
    tag_pattern = re.compile(
        r'(:?' + re.escape(opened_tag) + r'.*?' + re.escape(closed_tag) + r')',
        flags=re.U
    )
    for _line in fileinput.input(
            inplace=True,
            mode='rb',
    ):
        line = str(_line, encoding='utf-8')
        result = ''
        inner_list = tag_pattern.split(line)
        for tag in inner_list:
            o_tag_index = tag.find(opened_tag)
            c_tag_index = tag.find(closed_tag)
            # 1. line like '<TAG>%</TAG>'
            if o_tag_index >= 0 and c_tag_index >= 0:
                result += get_tag_text(tag, o_tag_index, c_tag_index)
                continue
            # 2. line like '%<TAG>%'
            elif o_tag_index >= 0 > c_tag_index:
                into_tag = True
            if into_tag:
                tag_lines_count += 1
                if tag_lines_count > TOO_MUCH_INTO_TAG:
                    raise IOError(
                        'TOO MUCH INTO TAG: {}:{}'.format(
                            fileinput.filename(),
                            fileinput.filelineno(),
                        )
                    )
                # 3. line like '%</TAG>%'
                if c_tag_index >= 0:
                    into_tag = False
                    tag_lines_count = 0
                result += get_tag_text(tag, o_tag_index, c_tag_index)
            # 4. line like '%'
            else:
                result += tag
        sys.stdout.buffer.write(result.encode())
    fileinput.close()
    return None


if __name__ == '__main__':
    edit_file(*sys.argv[1:])
