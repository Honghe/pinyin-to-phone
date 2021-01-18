# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
from typing import List

import pandas as pd
from pypinyin import lazy_pinyin, Style


def check_element_repeat(l: List):
    '''
    检测是否有连续的相同元素。
    比如: 'ii i1 j iu3 er4 er4'中的'er4 er4'
    :param l:
    :return:
    '''
    for x, y in zip(l[1:], l[:-1]):
        if x == y:
            return True
    return False


def check_phone_initial_final(lexicon_file: str):
    '''
    检查声韵母, 清理不是一个拼音对应强制"声母韵母"的模式
    示例：er4的强制"声母韵母"的模式为: "ee er4"
    :return:
    '''
    result = []
    with open(lexicon_file) as lexiconfile:
        spamreader = csv.reader(lexiconfile, delimiter=' ')
        for row in spamreader:
            # 使用偶数计算，
            if len(row[1:]) % 2 != 0:
                print(f'odd: {row[0]}: {" ".join(row[1:])}')
            # 同时再过滤相同音，如er4 er4
            elif check_element_repeat(row[1:]):
                print(f'repeat: {row[0]}: {" ".join(row[1:])}')
            else:
                result.append(row)
    return result

    # 偶数计算：有如下几行中间的"二"没有用双音素"ee er"
    # 四百二十三: s iy4 b ai3 er4 sh ix2 s an1
    # 一千二百二十七: ii i4 q ian1 ee er4 b ai3 er4 sh ix2 q i1
    # 一九六二: ii i1 j iu3 l iu4 er4
    # 一九八二: ii i1 j iu3 b a1 er4
    # 一百二十六: ii i4 b ai3 er4 sh ix2 l iu4
    # 二百二十八: ee er4 b ai3 er4 sh ix2 b a1

    # 相同音：er4 er4
    # 一九二二 ii i1 j iu3 er4 er4


def parse_initial_finale(lexicon_list: List[List[str]]):
    df = pd.DataFrame([[row[0], row[1:]] for row in lexicon_list], columns=['grapheme', 'phoneme'])
    df['pinyin'] = [lazy_pinyin(x, Style.TONE3, neutral_tone_with_five=True) for x in df['grapheme']]
    print(df.head())
    # 拼音与声韵母对应
    pinyin_map = defaultdict(set)
    for index, row in df.iterrows():
        for i, x in enumerate(row['pinyin']):
            _phoneme = tuple(row['phoneme'][i * 2: i * 2 + 2])
            pinyin_map[x].add(_phoneme)

    # 带声调的音节数为1259
    print(f'带声调的音节数: {len(pinyin_map)}')
    # 不带声调的音节数为403，语音识别的书中是409个
    print(f'不带声调的音节数: {len(set([x[:-1] for x in pinyin_map]))}')
    # 带声调的声韵母为226，语音识别的书中是227个
    initials = set()  # 声母28个
    finals = set()  # 带声调的韵母189个
    for index, row in df.iterrows():
        for i, x in enumerate(row['phoneme']):
            if i % 2 == 0:
                initials.add(x)
            else:
                finals.add(x)
    print(f'声母数: {len(initials)}')
    print(f'带声调韵母数: {len(finals)}')
    # 不带声调的声韵母为66，语音识别的教材中一般是65-67个
    finals_without_tone = set()  # 不带声调的韵母39个
    for x in finals:
        if x[-1].isnumeric():
            x = x[:-1]
        finals_without_tone.add(x)

    print(f'不带声调的韵母数: {len(finals_without_tone)}')
    print('声母', sorted(initials))
    print('韵母', sorted(finals_without_tone))

    # 不带声调的拼音与声韵母对应
    pinyin_map_with_tone = defaultdict(set)
    for k in pinyin_map:
        assert str.isnumeric(k[-1])
        k_with_tone = k[:-1]
        for v in pinyin_map[k]:
            initial, final = v
            assert str.isnumeric(final[-1])
            assert str.isalpha(initial[-1])
            v_with_tone = (initial, final[:-1])
            pinyin_map_with_tone[k_with_tone].add(v_with_tone)

    # for k in sorted(pinyin_map_with_tone.keys()):
    #     print(k, ' '.join([' '.join(x) for x in pinyin_map_with_tone[k]]))

if __name__ == '__main__':
    lexicon_file = 'lexicon.txt'
    lexicon_list = check_phone_initial_final(lexicon_file)
    parse_initial_finale(lexicon_list)
