from shellParser import shellParser
parser = shellParser('show 192.168.0.1 http status')
print parser.command()
