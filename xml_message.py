"""产生或解析用于网络通信的XML文本"""

import xml.etree.cElementTree as etree
import xml.dom.minidom as minidom
from io import StringIO


def _node_to_dict(_dict, node):
    """通过递归运算，将node转换成字典

        参数：
            _dict: 一个字典，用于存储node的树形结构
            node: 一个xml.dom.Element

        返回值：
            无
    """
    for n in node.childNodes:
        if n.nodeType == minidom.DocumentType.TEXT_NODE:
            ss = n.data.strip()
            if len(ss) < 1:
                continue
            _dict[node.nodeName] = ss
        elif n.nodeType == minidom.DocumentType.ELEMENT_NODE:
            if node.nodeName not in _dict.keys():
                _dict[node.nodeName] = {}
            _node_to_dict(_dict[node.nodeName], n)


class XmlMessage:
    """产生各种XML文本"""

    def __init__(self):
        self.dict_new = {'msg': {'header': {}, 'data': {}}}
        self.root = None

    def create_cmd(self, msg_type, cmd, ver, _id, data=None):
        """产生命令（或回复）消息

           参数：
               msgType: 命令 = 0， 回复 = 1
               cmd: 命令类型
               ver: 版本
               _id: ID
               data: 相关数据，字典，包括许多内容

           返回值：
               一个XML结构的文本
        """
        header = (self.dict_new['msg'])['header']
        if msg_type == 0:
            header['cmd'] = cmd.upper()
        else:
            header['ack'] = cmd.upper()
        header['ver'] = ver
        header['id'] = _id

        if data is not None:
            (self.dict_new['msg'])['data'] = data

        self.root = etree.Element('msg')
        self._dict_to_xml(self.root, self.dict_new['msg'])
        
        rough_string = etree.tostring(self.root, 'utf-8')
        reared_content = minidom.parseString(rough_string)
        
        ss = StringIO('')
        reared_content.writexml(ss, addindent=" ", newl="\n", encoding="utf-8")
        ret = ss.getvalue()
        ss.close()
        return ret

    @staticmethod
    def get_cmd(xml_string):
        """将XML文本转换为字典

            参数：
                xml_string: xml文本

            返回值：
                包括三个项目的元组，三个项目如下：
                1 -- 命令的类型： 0 - 命令； 1 - 回复
                2 -- header的相关字典
                3 -- data的相关字典
        """
        dom = minidom.parseString(xml_string)
        root = dom.documentElement
        header_node = root.getElementsByTagName('header')[0]
        data_node = root.getElementsByTagName('data')[0]
        header = {}
        data = {}
        _node_to_dict(header, header_node)
        _node_to_dict(data, data_node)

        _type = 0
        if 'ack' in header.keys():
            _type = 1

        return _type, header, data

    def _dict_to_xml(self, upper_node, the_dict):
        """将字典转换成XML结构

            参数：
                upper_node: 上一层的节点
                the_dict: 本层的字典，下一层将进行递归

            返回值：
                无
        """
        for (k, v) in the_dict.items():
            if type(v) is not dict:
                key = etree.SubElement(upper_node, k)
                key.text = v
            else:
                node_name = etree.SubElement(upper_node, k)
                self._dict_to_xml(node_name, v)


if __name__ == '__main__':
    xml_msg = XmlMessage()
    # print(xml_msg.create_cmd(0, 'LOGIN', '1.0', '1234', {'user': '0707036', 'ip': '191.1.6.103'}))
    x = xml_msg.create_cmd(1, 'LOGIN', '1.0', '1234', {'ret': 'NOK', 'error': 'Master is rejected'})
    print(x)
    print(XmlMessage.get_cmd(x))
