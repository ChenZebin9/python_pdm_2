""" 一些基础的数据类 """


class Part:
    """ 代表一个Item """

    def __init__(self, part_id, name, english_name, status, description=None, comment=None):
        self.__part_id = part_id
        self.part_id = '{:08d}'.format(part_id)
        self.name = name
        self.english_name = english_name
        self.status = status
        self.description = description
        self.comment = comment
        self.tags = []

    @staticmethod
    def get_parts(database, part_id=None, name=None, english_name=None, description=None):
        rs = database.get_parts(part_id, name, english_name, description)
        result = []
        for r in rs:
            p = Part(r[0], r[1], r[2], r[4], description=r[3], comment=r[5])
            result.append(p)
        return result

    @staticmethod
    def get_parts_from_tag(database, tag_id):
        rs = database.get_parts_2_tag( tag_id )
        result = []
        for r in rs:
            p = Part( r[0], r[1], r[2], r[4], description=r[3], comment=r[5] )
            result.append( p )
        return result

    def get_tags(self, database):
        rr = database.get_tags_2_part(self.__part_id)
        for r in rr:
            t = Tag(r[0], r[1], r[2], r[3], database=database)
            self.tags.append(t)

    def get_part_id(self):
        return self.__part_id

    def get_children(self, database):
        rs = database.get_children(self.__part_id)
        if rs is None:
            return None
        result = []
        for r in rs:
            p = Part(r[1], r[2], r[3], r[4], description=r[5], comment=r[6])
            one_r = (r[0], p, r[7], r[8], r[9])
            result.append(one_r)
        return result

    def __eq__(self, other):
        return self.part_id == self.part_id

    def __hash__(self):
        return hash(self.__part_id)


class Tag:
    """ 代表一个Tag """

    def __init__(self, tag_id, name, parent_id, sort_index, database=None):
        self.tag_id = tag_id
        self.name = name
        self.parent_id = parent_id
        self.sort_index = sort_index
        self.children = []
        self.__search = False
        self.__whole_name = name
        if database is not None and parent_id is not None:
            self.__build_whole_name(database, parent_id)

    def __build_whole_name(self, database, parent):
        ts = database.get_tags(tag_id=parent)
        t = ts[0]
        self.__whole_name = '{0} > {1}'.format(t[1], self.__whole_name)
        if t[2] is not None:
            self.__build_whole_name(database, t[2])

    def search_children(self, database):
        if self.__search:
            return
        self.__search = True
        rr = database.get_tags(parent_id=self.tag_id)
        for r in rr:
            t = Tag(r[0], r[1], r[2], r[3], database=database)
            self.children.append(t)

    @staticmethod
    def get_tags(database, tag_id=None, name=None, parent_id=None):
        rs = database.get_tags(tag_id, name, parent_id)
        result = []
        for r in rs:
            t = Tag( r[0], r[1], r[2], r[3], database=database)
            result.append( t )
        return result

    def get_whole_name(self):
        return self.__whole_name

    def __str__(self):
        return self.__whole_name
