import ply.lex as lex

# List of token names.   This is always required
tokens = (
    "IMGLINK",
    "EXTLINK",
    "INLINK",
    "TEXT",
    "STRONG",
    "BULLET",
)

# Regular expression rules for simple tokens
def t_BULLET(t):
    r'^\s+'
    t.value = len(t.value)
    return t


t_TEXT = r'[^\[\n]+'


def t_IMGLINK(t):
    r'\[(?P<link>(https://gyazo.com/.*|https?://.*\.(jpg|png|gif)))\]'
    t.value = t.lexer.lexmatch.group('link')
    return t


url = r'(https?://[^\]\s]+)'
extlink_label = r'[^\]]+'
extlink = r'\[(?P<link>' + url + r')\s?(?P<label>' + extlink_label + r')?\]'


@lex.TOKEN(extlink)
def t_EXTLINK(t):
    t.value = (
        t.lexer.lexmatch.group('link'),
        t.lexer.lexmatch.group('label'),
    )
    return t


def t_INLINK(t):
    r'\[(?P<label>[^*\]][^\]]+)\]'
    t.value = lexer.lexmatch.group('label')
    return t


def t_STRONG(t):
    r'\[(?P<level>\*+)\s+(?P<label>[^\]][^\]]+)\]'
    level = lexer.lexmatch.group('level')
    label = lexer.lexmatch.group('label')
    t.value = (label, len(level))
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


tests = {
    'テキスト Body': [
        ('TEXT', 'テキスト Body')],
    '内部リンク[入り]文章': [
        ('TEXT', '内部リンク'),
        ('INLINK', '入り'),
        ('TEXT', '文章')],
    '外部リンク1[http://url]文章': [
        ('TEXT', '外部リンク1'),
        ('EXTLINK', ('http://url', None)),
        ('TEXT', '文章')],
    '外部リンク2[http://url 入り]文章': [
        ('TEXT', '外部リンク2'),
        ('EXTLINK', ('http://url', '入り')),
        ('TEXT', '文章')],
    '外部リンク3[http://url 入り です]文章': [
        ('TEXT', '外部リンク3'),
        ('EXTLINK', ('http://url', '入り です')),
        ('TEXT', '文章')],
    '強調1[* 強い1]文章': [
        ('TEXT', '強調1'),
        ('STRONG', ('強い1', 1)),
        ('TEXT', '文章')],
    '強調2[** 強い2]文章': [
        ('TEXT', '強調2'),
        ('STRONG', ('強い2', 2)),
        ('TEXT', '文章')],
    '強調3[*** 強い3]文章': [
        ('TEXT', '強調3'),
        ('STRONG', ('強い3', 3)),
        ('TEXT', '文章')],
    '外部画像 [https://pbs.twimg.com/media/EPqd_7xXkAA7jVB.jpg] です': [
        ('TEXT', '外部画像 '),
        ('IMGLINK', 'https://pbs.twimg.com/media/EPqd_7xXkAA7jVB.jpg'),
        ('TEXT', ' です')],
    'GYAZO画像 [https://gyazo.com/abcdefg] です': [
        ('TEXT', 'GYAZO画像 '),
        ('IMGLINK', 'https://gyazo.com/abcdefg'),
        ('TEXT', ' です')],
    ' 箇条書き1': [
        ('BULLET', 1),
        ('TEXT', '箇条書き1')],
    '\t 箇条書き2': [
        ('BULLET', 2),
        ('TEXT', '箇条書き2')],
}


def test():
    # data = '\n'.join(tests)
    # # Tokenize
    # lexer.input(data)
    # for tok in lexer:
    #     print(tok)

    from itertools import zip_longest

    print('Testing ', end='')
    for text, expects in tests.items():
        lexer.input(text)
        for tok, expect in zip_longest(lexer, expects):
            try:
                assert (tok.type, tok.value) == expect
                print('.', end='')
            except AssertionError as e:
                print('\nFailed:', '\n  Actual:', (tok.type, tok.value), '\n  Expect:', expect)
    print()


if __name__ == '__main__':
    test()
