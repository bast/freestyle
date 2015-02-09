
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

    # first we find all lines that have old school
    # style continuation markers
    lines_old_markers = []
    for i, line in enumerate(sources_in_split):
        if len(line) > 6:
            if line[0:4] == '    ' and line[5] != ' ':
                lines_old_markers.append(i)

    # now for each of these we will go backwards
    # until we find a line that is a real code line
    lines_new_markers = []
    for i in lines_old_markers:
        for j in range(i-1, -1, -1):
            if len(sources_in_split[j]) > 0 and not sources_in_split[j][0] in ['!', 'C', 'c', '*', '#']:
                lines_new_markers.append(j)
                break

    # we replace old continuations by proper & just in case
    sources_temp = []
    for i, line in enumerate(sources_in_split):
        if i in lines_old_markers:
            sources_temp.append('     &' + line[6:])
        else:
            sources_temp.append(line)

    # we add continuations at the end of the lines
    sources_out = []
    for i, line in enumerate(sources_temp):
        s_temp = ''
        if i in lines_new_markers:
            for j in range(72 - len(line)):
                s_temp += ' '
            s_temp += '&'
        sources_out.append(line + s_temp)

    return '\n'.join(sources_out)

#-------------------------------------------------------------------------------

def test_convert_continuations():

    sources_in = '''
      foo,
     &raboof,
     *raboof,
     *raboof,
!
!
     *raboof
 10
#ifdef
      foo,
     &raboof'''

    sources_out = '''
      foo,                                                              &
     &raboof,                                                           &
     &raboof,                                                           &
     &raboof,                                                           &
!
!
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
