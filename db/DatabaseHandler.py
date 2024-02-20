from abc import abstractmethod, ABCMeta


class DatabaseHandler( metaclass=ABCMeta ):

    @abstractmethod
    def get_database_type(self):
        """
        获取数据库的类型名称
        :return: str; MSSQL 或 SQLite
        """
        pass

    @abstractmethod
    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
        pass

    @abstractmethod
    def get_parts_by_config(self, part_id=None, name=None, english_name=None, description=None, column_config=None):
        """
        根据column_config数组，使用更加复杂的算法，获取零件信息。
        :param part_id:
        :param name:
        :param english_name:
        :param description:
        :param column_config: [0:5] 原有的标志位；[5:-1] 可配置的标志位；[-1:] 原有的备注标志位
        :return:
        """
        pass

    @abstractmethod
    def get_tag_id(self, name, parent_name=None):
        """
        获取给定名称的tag的id，以便于进一步判断
        :param name:
        :param parent_name:
        :return: int or None
        """
        pass

    @abstractmethod
    def get_tags(self, tag_id=None, name=None, parent_id=None):
        pass

    @abstractmethod
    def get_tags_2_part(self, part_id):
        pass

    @abstractmethod
    def get_sub_tag_by_part_and_tag_name(self, part_id, tag_name):
        """ 通过part_id，及一个tag_name，查找其子tag """
        pass

    @abstractmethod
    def get_parts_2_tag(self, tag_id):
        pass

    @abstractmethod
    def get_files_2_part(self, part_id):
        pass

    @abstractmethod
    def get_thumbnail_2_part(self, part_id, ver=None):
        pass

    @abstractmethod
    def generate_a_image(self, part_id, ver=None):
        """
        在系统临时目录下，生成一个JPG格式的图片
        :param part_id:
        :param ver:
        :return: 图片目录
        """

    @abstractmethod
    def get_children(self, part_id):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def save_change(self):
        """ 实际上就是 database_connection 的 commit """
        pass

    @abstractmethod
    def sort_one_tag_to_index(self, tag_id, target_index):
        """ 改变一个 tag 的顺序 """
        pass

    @abstractmethod
    def set_tag_parent(self, tag_id, parent_id):
        """ 设置一个 tag 的parent """
        pass

    @abstractmethod
    def create_one_tag(self, name, parent_id):
        """ 新建一个Tag，返回新Tag的id """
        pass

    @abstractmethod
    def del_one_tag(self, tag_id):
        """ 删除一个Tag """
        pass

    @abstractmethod
    def rename_one_tag(self, tag_id, tag_name):
        """ 重命名一个Tag """
        pass

    @abstractmethod
    def set_tag_2_part(self, tag_id, part_id):
        pass

    @abstractmethod
    def del_tag_from_part(self, tag_id, part_id):
        pass

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def get_parents(self, part_id):
        pass

    @abstractmethod
    def get_pick_record_throw_erp(self, erp_id, which_company=1, top=2):
        """
        通过一个ERP物料编号，查找以往的领料记录；
        which_company=1表示巨轮智能，=2表示巨轮中德；
        top= 仅获取记录的前几条，当top<=0时，获取所有记录
        输出格式：[[单号，数量，总去税金额，日期]] 或 None
        """
        pass

    @abstractmethod
    def get_price_from_self_record(self, part_id, top=2):
        """
        获取PDM中所保存的价格信息
        :param part_id: 零件号
        :param top: 仅获取记录的前几条，当top<=0时，获取所有记录
        :return: [[单号，含税总金额，其它金额（含税），税率，数量，日期，供应商名称]] 或 None
        """
        pass

    @abstractmethod
    def get_erp_data(self, erp_code):
        """ 通过中德物料编码获取其它信息 """
        pass

    @abstractmethod
    def search_thr_erp_id(self, id_str: str, is_zd=True):
        """
        通过erp的物料编码进行检索
        :param id_str: 物料编码数据段
        :param is_zd: 是中德的仓库
        :return:
        """
        pass

    @abstractmethod
    def search_thr_erp_description(self, des_str: str, is_zd=True):
        """
        通过erp的物料描述进行搜索
        :param des_str: 物料描述数据段
        :param is_zd: 是中德的仓库
        :return:
        """
        pass

    @abstractmethod
    def get_storing(self, part_id=None, position=None):
        """
        通过零件号和仓位代号，获取仓储数据
        :param position: 一个列表 list，代表一个或多个仓位代码
        :param part_id: 零件号
        :return: 仓储数据 [零件号，仓位代码，数量，最近修改日期，单价]
        """
        pass

    @abstractmethod
    def get_all_storing_position(self):
        """
        获取所有的仓位
        :return: list，仓位清单
        """
        pass

    @abstractmethod
    def clear_storing_position(self, storage_position):
        """
        清除仓储位置的库存
        :param storage_position:
        :return:
        """
        pass

    @abstractmethod
    def update_part_storing(self, part_id, qty, storage_position, _date, unit_price):
        """
        更新仓储数据
        :param unit_price:
        :param part_id:
        :param qty:
        :param storage_position:
        :param _date:
        :return:
        """
        pass

    @abstractmethod
    def update_zd_erp_foundation_info(self, _data):
        """
        更新中德的ERP基础物料数据
        :param _data: [(erp_id, description, _unit)]
        :return: 处理的统计结果
        """
        pass

    @abstractmethod
    def update_jo_erp_foundation_info(self, _data):
        """
        更新钜欧的ERP基础物料数据
        :param _data: [(erp_id, description, _unit)]
        :return: 处理的统计结果
        """
        pass

    @abstractmethod
    def get_products_by_id(self, product_id):
        """
        通过产品编号，获取产品的记录
        :param product_id: str，产品编号
        :return: list，有关产品的记录
        """
        pass

    @abstractmethod
    def get_erp_info(self, erp_code, which_erp=0):
        """
        通过物料编码，获取物料信息
        :param which_erp: 0 - 中德，1 - 巨轮，2 - 钜欧
        :param erp_code: 物料编码，一个“00.00.00.0000”格式的字符串
        :return: [物料编码，物料描述，单位] or None
        """
        pass

    @abstractmethod
    def get_require_bill(self, prefix=None, bill_num=None):
        """
        根据给定的抬头，查找相应的需求清单
        :param bill_num: 完整的清单编号
        :param prefix:清单编号的前缀
        :return:
        """
        pass

    @abstractmethod
    def get_available_supply_operation_bill(self, prefix=None):
        """
        根据给定的抬头，查找下一个可用的操作清单名称
        :param prefix: 例如：B200402
        :return: str
        """
        pass

    @abstractmethod
    def insert_requirements(self, bill_data, items_data):
        """
        将需求的数据写入数据库
        :param bill_data: list, [清单号, 日期, 操作者]
        :param items_data:  二维数组, [list], [[PartId, ErpId, Qty, Comment]]
        :return:
        """
        pass

    @abstractmethod
    def select_process_data(self, process_type=1):
        """
        查询处于某些阶段（根据process_type的数值）的过程数据
        :param process_type: 1=可投料，2=可派工，3=可入库，4=可领料
        :return: 数量, None（或者数据）
        """
        pass

    @abstractmethod
    def create_supply_operation(self, data):
        """
        创建物料操作的数据库记录
        :param data:{}, 里面包括：部分BillName - str, Operator - str, DoingDate - str, BillType - str, NextProcess - int,
        Items - [LinkItem - int, Qty - float, Comment - str]
        :return: 最终确定的 BillName
        """
        pass

    @abstractmethod
    def create_picking_record(self, data, mark):
        """
        创建出库记录
        :param mark: {}，里面包括：record - int
        :param data:{}，里面包括：BillName - str, Operator - str, DoingDate - str, BillType - str, FromStorage - str,
        Items - [Contract - str, PartId - int, ErpId - str, Qty - float, RecordIndex - int]
        :return:
        """
        pass

    @abstractmethod
    def next_available_part_id(self):
        """
        下一个可用的Part Id地址
        :return:
        """
        pass

    @abstractmethod
    def set_part_id_2_prepared(self, part_id):
        """
        将 Part ID 的状态修改为 StatusType=10
        :return:
        """
        pass

    @abstractmethod
    def create_a_new_part(self, part_id, name, english_name, description, comment, tag_dict):
        """
        新建一个 Part
        :param part_id: int-零件号
        :param name: str-名称
        :param english_name: str-英文名称
        :param description: str-描述
        :param comment: str-备注
        :param tag_dict: {}-标签
        :return:
        """
        pass

    @abstractmethod
    def update_part_info(self, part_id, name, english_name, description, comment):
        """
        更新一个 Part 的数据
        :param part_id:
        :param name:
        :param english_name:
        :param description:
        :param comment:
        :return:
        """
        pass

    @abstractmethod
    def get_part_info_quick(self, part_id):
        """
        利用 PartDetail2 视图，快速获取PART的信息
        :param part_id:
        :return:[name, description, brand&standard, foreign_code, erp_code, comment, type]
        """
        pass

    @abstractmethod
    def get_pick_material_record(self, begin_date, end_date):
        """
        获取领料记录
        :param begin_date: 起始日期
        :param end_date: 结束日期
        :return:
        """
        pass

    @abstractmethod
    def create_put_back_material_record(self, bill_name, operator, when, data):
        """
        创建退料的操作数据
        :param when: str，日期
        :param bill_name: str，单号
        :param operator: str，操作者
        :param data: 数据 [退料所倚靠的单号]
        :return:
        """
        pass

    @abstractmethod
    def cancel_material_requirement(self, item_id, cancel_qty, change_doing=False):
        """
        将物料需求（JJStorage.KbnSupplyItem）作废
        :param change_doing: 是否改变doing字段的值？
        :param cancel_qty: 要作废的数量
        :param item_id: 需求编号
        :return:
        """
        pass

    @abstractmethod
    def cancel_supply_operation(self, record_id, cancel_qty):
        """
        将需求处理操作（JJStorage.SupplyOperationRecord）删除，并更新相关的物料需求（JJStorage.KbnSupplyItem）
        :param record_id: 需求处理操作编号
        :param cancel_qty: 要作废的数量
        :return:
        """
        pass

    @abstractmethod
    def set_part_thumbnail(self, part_id, image_data):
        """
        设置零件的缩略图
        :param part_id: 零件号
        :param image_data: 图像数据
        :return:
        """
        pass

    @abstractmethod
    def clean_part_thumbnail(self, part_id):
        """
        清楚零件的缩略图
        :param part_id:
        :return:
        """
        pass

    @abstractmethod
    def get_last_supply_record_link(self, this_id):
        """
        获取上个一连接的Id
        :param this_id:
        :return:
        """
        pass

    @abstractmethod
    def update_part_relation(self, relation_id, index_id, parent_id, child_id, sum_qty, actual_qty, relation_comment):
        """
        更新或新近一个新的零件关联
        :param relation_id: 关联ID，可能为None
        :param index_id: 关联的index，代表在子项目中的排序
        :param parent_id: 父ID
        :param child_id: 子ID
        :param sum_qty: 统计数量
        :param actual_qty: 实际数量
        :param relation_comment: 关联备注
        :return:
        """
        pass

    @abstractmethod
    def remove_part_relation(self, relation_id):
        """
        移除原先的关联
        :param relation_id: 关联ID
        :return:
        """
        pass

    @abstractmethod
    def replace_part_relation(self, relation_id, part_id):
        """
        将relaition_id下的关联项目，代替为所给的part_id
        :param relation_id: 关联的 ID
        :param part_id: 新的零件 ID
        :return:
        """
        pass

    @abstractmethod
    def get_part_hyper_link(self, part_id):
        """
        获取项目的采购链接
        :param part_id: 项目编号
        :return:
        """
        pass

    @abstractmethod
    def set_part_hyper_link(self, part_id, the_link):
        """
        设置项目的采购链接
        :param part_id:
        :param the_link:
        :return:
        """
        pass

    @abstractmethod
    def add_file_link_2_part(self, part_id, file_path):
        """
        将文件路径添加至零件的链接
        :param part_id:
        :param file_path:
        :return:
        """
        pass

    @abstractmethod
    def remove_file_link_from_part(self, part_id, file_path):
        """
        从零件中移除文件链接
        :param part_id:
        :param file_path:
        :return:
        """
        pass

    @abstractmethod
    def get_identical_parts(self, _id, mode=1, keep_original=False):
        """
        获取同质单元
        :param keep_original: 当 mode=1 时，是否保留原零件
        :param mode: 1=id 代表零件号，0=id代表功能号
        :param _id:
        :return: 当mode=1时，([PartID], (ID, Description, StatusType))；当mode≠1时，[PartID]
        """
        pass

    @abstractmethod
    def get_identical_description(self, filter_text):
        """
        根据所给的字符，获取同质单元的描述
        :param filter_text: 关键字
        :return:
        """
        pass

    @abstractmethod
    def set_identical_description(self, fun_description, fun_id=-1):
        """
        创建或更新同质单元描述
        :param fun_description: 描述文本
        :param fun_id: -1：创建并返回新Id，>0：更新同质描述
        :return:
        """
        pass

    @abstractmethod
    def delete_identical_description(self, fun_id):
        """
        删除同质单元描述
        :param fun_id:
        :return:
        """
        pass

    @abstractmethod
    def edit_part_to_identical_group(self, fun_id, part_id, grade=6,add_action=True):
        """
        一个零件对于同质组的操作，加入或移除
        :param grade: 评分，1-10，仅作为参考
        :param fun_id:
        :param part_id:
        :param add_action: True - 加入，False - 移除
        :return:
        """
        pass

    @abstractmethod
    def link_part_image(self, part_id, ref_part_id) -> int:
        """
        将两个零件的图形，互为链接
        :param part_id: 要沿用其它零件的图形的ID
        :param ref_part_id: 要被沿用图形的零件
        :return: 真正被引用的图形对应的零件号
        """
        pass

    @abstractmethod
    def roll_back(self):
        """
        回滚
        :return:
        """
        pass

    @abstractmethod
    def suppress_part(self, part_id):
        """
        抑制零件，即将零件设置为未启用状态
        :param part_id:
        :return:
        """
        pass
