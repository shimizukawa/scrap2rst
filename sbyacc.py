import ply.yacc as yacc
from sblex import tokens


def p_expression_block(p):
    """expression : block
    """
    p[0] = f'%\n%\n{p[1]}%\n%\n'


def p_block_inline(p):
    """block : inline
    """
    p[0] = p[1]


def p_block_block_inline(p):
    """block : block inline
    """
    p[0] = p[1] + p[2]


def p_inline_text(p):
    """inline : TEXT
    """
    p[0] = p[1]


def p_block_bullet(p):
    """block : BULLET inline
    """
    breakpoint()
    p[0] = (' ' * (p[1] - 1) * 3) + '* ' + p[2]


def p_block_imglink(p):
    """block : IMGLINK
    """
    # FIXME: inline image must be `|name|` and `.. |name| image:: PATH`
    p[0] = f'.. image:: {p[1]}'


def p_inline_link_inline(p):
    """inline : link
    """
    sep = ' '
    if p[-1].endswith(' '):
        sep = ''
    p[0] = sep + p[1] + ' '


def p_inline_extlink(p):
    """link : EXTLINK
    """
    link, title = p[1]
    if title:
        p[0] = f'`{title} <{link}>`__'
    else:
        p[0] = link


def p_inline_inlink(p):
    """link : INLINK
    """
    label = p[1]
    link = f'https://scrapbox.io/shimizukawa/' + label.replace(' ', '_')
    p[0] = f'`{label} <{link}>`__'


def p_inline_strong(p):
    """inline : STRONG
    """
    p[0] = f' **{p[1][0]}** '


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!", p)
    parser.errok()


parser = yacc.yacc()


def test():
    from sblex import tests
    testdata = '\n'.join(tests)
    result = parser.parse(testdata)
    print(result)


if __name__ == '__main__':
    test()
