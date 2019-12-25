from pathlib import Path
import os
import sys
import CompilationEngine as ce
import JackTokenizer as jt


if __name__ == '__main__':
    source = sys.argv[1]
    path = Path(source)
    if path.is_dir():
        for filename in os.listdir(source):
            name, ext = os.path.splitext(filename)
            if ext == '.jack':
                # edit outfile name
                outfile = source + '/' + name + '.xml'
                # create tokenizer
                tokenizer = jt.JackTokenizer(source + '/' + filename)
                # compile
                ce.CompilationEngine(tokenizer, outfile)
    else:
        outfile = source.replace('.jack', '.xml')
        tokenizer = jt.JackTokenizer(source)
        ce.CompilationEngine(tokenizer, outfile)
