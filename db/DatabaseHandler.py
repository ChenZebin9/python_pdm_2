from abc import abstractmethod, ABCMeta


class DatabaseHandler(metaclass=ABCMeta):

    @abstractmethod
    def get_parts(self, part_id=None, name=None, english_name=None, description=None):
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
    def copy(self):
        pass

    @abstractmethod
    def get_parents(self, part_id):
        pass
