from pyparsing import Literal, CaselessLiteral, Word, Upcase 
from pyparsing import delimitedList, Optional, Combine, Group, Forward
from pyparsing import alphas, nums, alphanums
from pyparsing import oneOf, dblQuotedString, quotedString, ZeroOrMore, restOfLine
from pyparsing import ParseException

class SQLGrammar:

    def __init__(self):
        # define SQL tokens
        sqlStmt = Forward()
        selectToken = CaselessLiteral( "select" )
        fromToken   = CaselessLiteral( "from" )
        insertToken = CaselessLiteral( "insert" )
        intoToken   = CaselessLiteral( "into" )
        valueToken  = CaselessLiteral( "values" )
        createToken = CaselessLiteral( "create" )
        dropToken   = CaselessLiteral( "drop" )
        alterToken  = CaselessLiteral( "alter" )

        ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
        columnName     = Upcase( delimitedList( ident, ".", combine=True ) )
        columnNameList = Group( delimitedList( columnName ) )
        tableName      = Upcase( delimitedList( ident, ".", combine=True ) )
        tableNameList  = Group( delimitedList( tableName ) )
        valueName      = delimitedList( ident, ".", combine=True)
        valueNameList  = Group( delimitedList( valueName | 
            quotedString.setParseAction(self.stripQuotes) | 
            dblQuotedString.setParseAction(self.stripDblQuotes)))

        varTypeName = oneOf("""char CHAR varchar VARCHAR smallint SMALLINT numeric NUMERIC 
            tinyint TINYINT decimal DECIMAL date DATE int INT blob BLOB""") + \
            Optional("(" + Word(alphanums) + ")")

        legalPathChars = "~/_-().?,;"
        ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
        typeName       = delimitedList( ident, ".", combine=True ) 
        typeNameList   = Group( delimitedList( typeName ) )
        idName         = Upcase( delimitedList( ident, ".", combine=True ) )
        idNameList     = Group( delimitedList( idName ) )
       
        varType         = Group(ident + varTypeName)
        varTypeName     = delimitedList(varType,",")
        varTypeNameList = Group(delimitedList(varTypeName))
            
        pathident    =  Word(alphas + alphanums +  legalPathChars).setName("identifier")
        pathName     =  delimitedList( pathident,".", combine=True )
        pathNameList = Group( delimitedList( pathName ) )
            
        addCommand     = CaselessLiteral("add")
        dropCommand    = CaselessLiteral("drop column")

        whereExpression = Forward()
        
        and_ = CaselessLiteral("and")
        or_  = CaselessLiteral("or")
        in_  = CaselessLiteral("in")

        E = CaselessLiteral("E")
        binop = oneOf("= != < > >= <= eq ne lt le gt ge like", caseless=True)
        arithSign = Word("+-",exact=1)
        realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
            ( "." + Word(nums) ) ) + 
            Optional( E + Optional(arithSign) + Word(nums) ) )
        intNum = Combine( Optional(arithSign) + Word( nums ) + 
            Optional( E + Optional("+") + Word(nums) ) )

        columnRval = realNum | intNum | quotedString | columnName # need to add support for alg expressions
        whereCondition = Group(
            ( columnName + binop + columnRval ) |
            ( columnName + in_ + "(" + delimitedList( columnRval ) + ")" ) |
            ( columnName + in_ + "(" + sqlStmt + ")" ) |
            ( "(" + whereExpression + ")" )
            )
        whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression ) 

        # define the grammar
        sqlStmt << ( (selectToken.setResultsName("command") + 
            ( '*' | columnNameList ).setResultsName( "columns" ) + 
            fromToken + tableNameList.setResultsName( "tables" ) + 
            Optional( Group( CaselessLiteral("where") + whereExpression ), "" ).setResultsName("where")) | 
            ( insertToken.setResultsName("command") + intoToken + tableNameList.setResultsName("tables") +
            Optional( "(" + columnNameList.setResultsName("columns") + ")") +
            valueToken + "(" + valueNameList.setResultsName("fields") + ")" +
            Optional( Group( CaselessLiteral("where") + whereExpression ), "" ).setResultsName("where")) |
            ( (createToken | dropToken).setResultsName("command") + typeNameList.setResultsName("type") +
            Optional(oneOf("' \"") + pathNameList.setResultsName("path") + oneOf("' \""))  +
            idNameList.setResultsName("id") +
            Optional("(" + varTypeNameList.setResultsName("var") + ")") ) |
            ( alterToken.setResultsName("command") + typeNameList.setResultsName("type") +
            idNameList.setResultsName("id") +
            addCommand.setResultsName("operation") +
            varTypeNameList.setResultsName("var") )  |
            ( alterToken.setResultsName("command") + typeNameList.setResultsName("type") +
            idNameList.setResultsName("id") +
            dropCommand.setResultsName("operation") +
            idNameList.setResultsName("var") ) 
        )

        SQL = sqlStmt
        SQL.validate()

        # define Oracle comment format, and ignore them
        oracleSqlComment = "--" + restOfLine
        SQL.ignore( oracleSqlComment )

        self.grammar = SQL

    def stripDblQuotes( self, s, l, t ):
        return [ t[0].strip('"') ]

    def stripQuotes(self, s, l, t):
        return [ t[0].strip("'")]


class SQLParser:
    '''
    Test a simple select parsing:
    >>> import sqlparser
    >>> p = sqlparser.SQLParser()
    >>> p.parse("Select A, B, C from Sys.dual")
    >>> p.tokens.command
    'select'
    >>> p.tokens.tables
    (['SYS.DUAL'], {})
    >>> p.tokens.columns
    ([(['A', 'B', 'C'], {})], {})

    Test a simple insert parsing:
    >>> p.parse("Insert into sdfsdf(a,b,c) values(a,b,c)")
    >>> p.tokens.command
    'insert'
    >>> p.tokens.tables
    (['SDFSDF'], {})
    >>> p.tokens.columns
    (['A', 'B', 'C'], {})
    >>> p.tokens.fields
    (['a', 'b', 'c'], {})

    Test a simple insert parsing, with quoted values:
    >>> p.parse("Insert into sdfsdf(a,b,c) values('a','b','c')")
    >>> p.tokens.command
    'insert'
    >>> p.tokens.tables
    (['SDFSDF'], {})
    >>> p.tokens.columns
    (['A', 'B', 'C'], {})
    >>> p.tokens.fields
    (['a', 'b', 'c'], {})

    Test table create parsing:
    >>> p.parse('CREATE TABLE address_book (first_name VARCHAR(25), last_name VARCHAR(25), phone_number VARCHAR(15))')
    >>> p.tokens.command
    (['create'], {})
    >>> p.tokens.type
    (['TABLE'], {})
    >>> p.tokens.id
    (['ADDRESS_BOOK'], {})
    >>> p.tokens.var
    ([(['first_name', 'VARCHAR', '(', '25', ')'], {}), (['last_name', 'VARCHAR', '(', '25', ')'], {}), (['phone_number', 'VARCHAR', '(', '15', ')'], {})], {})

    Test database creation parsing:
    >>> p.parse("CREATE DATABASE '/desired/path/to/db'  MYDB")
    >>> p.tokens.command
    (['create'], {})
    >>> p.tokens.type
    (['DATABASE'], {})
    >>> p.tokens.path
    (['/desired/path/to/db'], {})
    >>> p.tokens.id
    (['MYDB'], {})

    Test database drop:
    >>> p = sqlparser.SQLParser("DROP DATABASE '/tmp'  testdb")
    >>> p.tokens.command
    (['drop'], {})
    >>> p.tokens.path
    (['/tmp'], {})
    >>> p.tokens.id
    (['TESTDB'], {})
    
    Test table drop:
    >>> p.parse("DROP TABLE address_book")
    >>> p.tokens.command
    (['drop'], {})
    >>> p.tokens.type
    (['TABLE'], {})
    >>> p.tokens.id
    (['ADDRESS_BOOK'], {})
    
    Test alter table add:
    >>> p.parse("ALTER TABLE Person ADD City varchar(30)")
    >>> p.tokens.command
    'alter'
    >>> p.tokens.type
    (['TABLE'], {})
    >>> p.tokens.id
    (['PERSON'], {})
    >>> p.tokens.operation
    'add'
    >>> p.tokens.var
    ([(['City', 'varchar', '(', '30', ')'], {})], {})
    
    Test alter table drop:
    >>> p.parse("ALTER TABLE Person DROP COLUMN Address")
    >>> p.tokens.command
    'alter'
    >>> p.tokens.type
    (['TABLE'], {})
    >>> p.tokens.id
    (['PERSON'], {})
    >>> p.tokens.operation
    'drop column'
    >>> p.tokens.var
    (['ADDRESS'], {})
    '''

    def __init__(self, statement=None):
        sg = SQLGrammar()
        self.grammar = sg.grammar
        self.tokens = None
        self.list_data = []
        self.dict_data = {}
        if statement:
            self.parse(statement)

    def parse(self, sql_string):
        '''
        Take a sql string and return PyParser tokens as defined in the SQLGrammar class.
        '''
        tokens = self.grammar.parseString(sql_string)
        self.tokens = tokens
        self.list_data = list(tokens)
        self.dict_data = dict(tokens)
        #return self.tokens


def _test():
    import doctest, sqlparser
    return doctest.testmod(sqlparser)

if __name__ == '__main__':
    _test()


