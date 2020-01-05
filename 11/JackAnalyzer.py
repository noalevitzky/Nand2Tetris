from pathlib import Path
import os
import sys
import CompilationEngine as Ce
import JackTokenizer as Jt

if __name__ == '__main__':
    source = sys.argv[1]
    path = Path(source)

    # check if directory
    if path.is_dir():
        for filename in os.listdir(source):
            # compile jack files
            name, ext = os.path.splitext(filename)
            if ext == '.jack':
                # edit outfile name
                outfile = source + '/' + name + '.xml'
                # create tokenizer
                tokenizer = Jt.JackTokenizer(source + '/' + filename)
                # compile
                Ce.CompilationEngine(tokenizer, outfile)
    else:
        # source is a single file, compile it
        outfile = source.replace('.jack', '.xml')
        tokenizer = Jt.JackTokenizer(source)
        Ce.CompilationEngine(tokenizer, outfile)
