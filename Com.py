# coding=gbk
""" һЩͨ�õġ������Ĺ��� """


def dict_2_str(the_dict):
    """
    dict ת str, dict�е�key��value�������У���%
    :param the_dict:
    :return:
    """
    temp_list = []
    for k in the_dict:
        v = the_dict[k]
        temp_list.append( f'{k}:{v}' )
    return '#'.join( temp_list )


def str_2_dict(the_str):
    """
    str ת dict
    :param the_str:
    :return:
    """
    result_dict = {}
    temp_list = the_str.split( '#' )
    for t in temp_list:
        k_v = t.split( ':' )
        result_dict[k_v[0]] = k_v[1]
    return result_dict
