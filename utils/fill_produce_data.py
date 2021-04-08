# coding=gbk
""" �������ӹ�������ܡ�����������󣬸�������ţ�����Ŀ��Excel�� """

import xlwings as xw
import functools

produce_suppliers = ('�е�����һ��', '�пƽ���', '�����', '��ģ��', '���ȴ�',
                     '���촴չ', '�·ᾫ��', '���', '�����ɴﾫ��', '���˾���')


class Produce:

    @staticmethod
    def __try_float(s):
        # ���Խ�ĳ����ת����float����
        try:
            if s is None:
                return None
            if isinstance( s, float ):
                return s
            if isinstance( s, str ):
                if len( s.strip() ) < 1:
                    return None
                return float( s )
        except:
            return None

    @staticmethod
    def object_creator(r):
        p = Produce.__try_float( xw.Range( f'I{r}' ).value )
        if p is not None:
            return Produce( r, p )
        return None

    def __init__(self, r, p):
        self.row = r
        t = xw.Range( f'B{r}' ).value
        if isinstance( t, int ):
            self.part_nr = t
        elif isinstance( t, float ):
            self.part_nr = int( t )
        else:
            self.part_nr = int( t.lstrip( '0' ) )
        self.blank = Produce.__try_float( xw.Range( f'G{r}' ).value )
        self.__pp = [p]
        self.__pp.append( Produce.__try_float( xw.Range( f'K{r}' ).value ) )
        self.__pp.append( Produce.__try_float( xw.Range( f'M{r}' ).value ) )
        self.__pp.append( Produce.__try_float( xw.Range( f'O{r}' ).value ) )
        self.supplier = xw.Range( f'S{r}' ).value
        self.supplier_index = produce_suppliers.index( self.supplier )
        self.produce_cost = 0.0
        for p in self.__pp:
            if p is not None:
                self.produce_cost += p


def p_cmp(a: Produce, b: Produce):
    if a.supplier_index > b.supplier_index:
        return 1
    elif a.supplier_index == b.supplier_index:
        return 0
    else:
        return -1


produce_dict = {}

for i in range( 3, 400 ):
    part_n = xw.Range( f'B{i}' ).value
    if part_n is None:
        break
    prd = Produce.object_creator( i )
    if prd is not None:
        if prd.part_nr in produce_dict:
            produce_dict[prd.part_nr].append( prd )
        else:
            produce_dict[prd.part_nr] = [prd]

for k in produce_dict:
    if len( produce_dict[k] ) > 1:
        ll = produce_dict[k]
        ll.reverse()
        produce_dict[k] = sorted( ll, key=functools.cmp_to_key( p_cmp ) )

print( '��ɼӹ����ݵ��ռ���' )
print( '������Ҫ������ݵ�Excel�ļ���' )

c = int( input( 'max row number?' ) )

if c < 1:
    exit( 0 )

for i in range( 2, c + 1 ):
    if xw.Range( f'A{i}' ).row_height <= 0:
        continue
    p_n = int( xw.Range( f'A{i}' ).value )
    if p_n not in produce_dict:
        continue
    p = produce_dict[p_n][0]
    xw.Range( f'I{i}' ).value = p.blank
    xw.Range( f'J{i}' ).value = p.produce_cost
    xw.Range( f'K{i}' ).value = p.supplier

print( '��ɻ��ӹ����ݵ���䡣' )
