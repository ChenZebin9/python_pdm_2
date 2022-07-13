# coding=gbk
from Part import Tag


class Product:
    """ 代表一个产品 """

    def __init__(self, product_id, actual_status, product_comment, status_comment, config):
        self.product_id = product_id
        self.actual_status = actual_status
        self.product_comment = product_comment
        self.status_comment = status_comment
        self.config = config
        self.tags = []
        self.children = []

    @staticmethod
    def get_products(database, product_id=None, product_comment=None, status_comment=None, config=None, top=False):
        rs = database.get_products( product_id, product_comment, status_comment, config, top )
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            t_children = pp.get_children( database )
            if t_children is not None:
                pp.children.extend( t_children )
            result.append( pp )
        return result

    def get_children(self, database, mode=0):
        """
        mode = 0: 查找子清单
        mode = 1: 查找父清单
        """
        rs = None
        if mode == 0:
            rs = database.get_children( self.product_id )
        elif mode == 1:
            rs = database.get_parent( self.product_id )
        if rs is None:
            return None
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            result.append( pp )
        return result

    def get_tags(self, database):
        self.tags.clear()
        rr = database.get_tags_2_product( self.product_id )
        for r in rr:
            t = Tag( r[0], r[1], r[2], r[3], database=database )
            self.tags.append( t )

    @staticmethod
    def get_products_from_tag(database, tag_id):
        rs = database.get_products_2_tag( tag_id )
        result = []
        for r in rs:
            pp = Product( r[0], r[2], r[7], r[8], r[9] )
            result.append( pp )
        return result

    def __eq__(self, other):
        return self.product_id == other.product_id

    def __hash__(self):
        return hash( self.product_id )
