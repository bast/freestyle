
"""
Script to convert fixed form Fortran files (written in Fortran 77) and
header files to free form.

Copyright (c) 2015 Radovan Bast
Licensed under the MIT License
"""

#-------------------------------------------------------------------------------

def convert_comments(sources_in):

    sources_out = []

    for line in sources_in.split('\n'):
        if len(line) > 0 and line[0] in ['C', 'c', '*']:
                sources_out.append('!' + line[1:])
        else:
            sources_out.append(line)

    return '\n'.join(sources_out)

#-------------------------------------------------------------------------------

def test_convert_comments():

    sources_in = '''
C
c
*

      foo
#
!
C'''

    sources_out = '''
!
!
!

      foo
#
!
!'''

    assert convert_comments(sources_in) == sources_out

#-------------------------------------------------------------------------------

def convert_continuations(sources_in):

    sources_in_split = sources_in.split('\n')

    lines_that_continue = []
    for i, line in enumerate(sources_in_split):
        # empty lines cannot continue
        if len(line) > 0:
            # ignore CPP lines
            if line[0] != '#':
                # last line cannot continue
                if i + 1 < len(sources_in_split):
                    # line can only continue if next line is longer than 5
                    if len(sources_in_split[i+1]) > 5:
                        # check the presence of a continuation marker which can be any ASCII character (not only '&')
                        if sources_in_split[i+1][0:4] == '    ' and sources_in_split[i+1][5] != ' ':
                            lines_that_continue.append(i)

    # we add continuations at the end of the lines
    sources_temp = []
    for i, line in enumerate(sources_in_split):
        if i in lines_that_continue:
            s_temp = ''
            for j in range(72 - len(line)):
                s_temp += ' '
            s_temp += '&'
            sources_temp.append(line + s_temp)
        else:
            sources_temp.append(line)

    # we replace continuation in next line by proper &
    sources_out = []
    for i, line in enumerate(sources_temp):
        if i-1 in lines_that_continue:
            sources_out.append('     &' + line[6:])
        else:
            sources_out.append(line)

    return '\n'.join(sources_out)

#-------------------------------------------------------------------------------

def test_convert_continuations():

    sources_in = '''
      foo,
     &raboof,
     *raboof,
     *raboof
 10
#ifdef
      foo,
     &raboof'''

    sources_out = '''
      foo,                                                              &
     &raboof,                                                           &
     &raboof,                                                           &
     &raboof
 10
#ifdef
      foo,                                                              &
     &raboof'''

    assert convert_continuations(sources_in) == sources_out

#-------------------------------------------------------------------------------

def main():

    import sys

    # exit if no argument (filename) given
    if len(sys.argv) == 1:
        print 'usage: python %s fixed-form-file > free-form-file' % sys.argv[0]
        sys.exit()

    file_name = sys.argv[1]

    with open(file_name, 'r') as fixed_file:
        fixed_sources = fixed_file.read()

    print convert_continuations(convert_comments(fixed_sources))

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
