import os
import sys
import argparse
from pathlib import Path
from subprocess import run, PIPE

OUTFILE_FOLDER = 'out'
OUTFILE_DEFAULT_NAME = 'radon_analysis_{}.txt'

def parse_args():
    """Handle command line arguments."""
    parser = argparse.ArgumentParser(description='Run code analyses via Radon. Choose any subset of the 4 metrics, or all of them.')
    parser.add_argument('input_file', action='store', type=str, help='input file')
    parser.add_argument('--raw', '-r', action='store_true', help='raw metrics')
    parser.add_argument('--cc', '-c', action='store_true', help='cyclomatic complexity')
    parser.add_argument('--mi', '-m', action='store_true', help='maintainability index')
    parser.add_argument('--hal', '-s', action='store_true', help='halstead complexity')
    parser.add_argument('--all', '-a', action='store_true', help='all metrics')
    parser.add_argument('--out', '-o', action='store', type=str, default=None, help='file name to write analysis to (will be written to /out/)')
    args = parser.parse_args()

    # Require a metric to be specified...
    if not args.raw and args.cc and args.mi and args.raw and args.hal:
        raise RuntimeError('Must specify a metric!')

    # Allow either only all OR only a subset of the 4 analyses. Not both at the same time
    if args.all and (args.cc or args.mi or args.raw or args.hal):
        raise RuntimeError('No need to specify anything else if "--all" or "-a" is selected.')

    # Construct outfile name
    input_basename = os.path.basename(Path(args.input_file))
    outfile_name = os.path.join(OUTFILE_FOLDER, args.out if args.out else OUTFILE_DEFAULT_NAME.format(input_basename))

    return args, outfile_name


#
# Helper functions for writing to outfile
#

def write_spacer(file_obj):
    file_obj.write('\n\n')

def write_header(file_obj, header):
    file_obj.write('{0}\n{1}\n{0}\n\n'.format('-' * 30, header))


#
# Radon analysis functions. Each function (with the exception of run_command)
# will run one of the four Radon analyses.
#

def run_command(command):
    """Helper for subprocess run command. Pipes stdout back into Python for use as a string variable."""
    return run(command, shell=True, check=True, stdout=PIPE).stdout.decode('utf-8').replace('\n', '')

def run_raw_metrics(infile_name, outfile):
    write_header(outfile, 'Raw Metrics')
    outfile.write(run_command('radon raw {}'.format(infile_name)))
    write_spacer(outfile)

def run_cyclomatic_complexity(infile_name, outfile):
    write_header(outfile, 'Cyclomatic Complexity')
    outfile.write(run_command('radon cc -a {}'.format(infile_name)))
    write_spacer(outfile)

def run_maintainability_index(infile_name, outfile):
    write_header(outfile, 'Maintainability Index')
    outfile.write(run_command('radon mi {}'.format(infile_name)))
    write_spacer(outfile)

def run_halstead_complexity(infile_name, outfile):
    write_header(outfile, 'Halstead Complexity')
    outfile.write(run_command('radon hal {}'.format(infile_name)))
    write_spacer(outfile)


def main():
    args, outfile_name = parse_args()
    infile_name = args.input_file

    # Create outfile path
    dir = os.path.dirname(outfile_name)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Run Radon analyses
    with open(outfile_name, 'w') as outfile:
        if args.all or args.raw:
            run_raw_metrics(infile_name, outfile)
        if args.all or args.cc:
            run_cyclomatic_complexity(infile_name, outfile)
        if args.all or args.mi:
            run_maintainability_index(infile_name, outfile)
        if args.all or args.hal:
            run_halstead_complexity(infile_name, outfile)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)
    sys.exit(0)
