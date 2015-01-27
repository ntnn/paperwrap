#!/usr/bin/env python3

from paperworks import models
from getpass import getpass
import os, sys
import logging
from fuzzywuzzy import fuzz
import yaml
import argparse

if str(sys.version[0]) < '3':
    input = raw_input

logger = logging.getLogger('paperwork')

pw = None

def login():
    global pw
    rc = os.environ.get('HOME')+'/.paperworkrc'
    if os.path.exists(rc):
        with open(rc, 'r') as f:
            conf = yaml.load(f)
        host = conf['host']
        user = conf['user']
        passwd = conf['pass']
    else:
        host = input('Host:')
        user = input('User:')
        passwd = getpass('Password:')
    pw = models.Paperwork(user, passwd, host)

def download():
    pw.download()

def update():
    pw.update()

def print_all():
    for nb in pw.notebooks:
        print(nb.title)
        for note in nb.notes:
            print("- {}".format(note.title))

def print_notes():
    for note in pw.get_notes():
        print(note.title)

def choose(title, choices):
    top_choice = (0, None)
    for choice in choices:
        val = fuzz.ratio(choice.title, title)
        if val > top_choice[0]:
            top_choice = (val, choice)
    logger.info('Fuzzy chose {} as top choice'.format(top_choice[1]))
    return top_choice[1]

def choose_note(title):
    return choose(title, pw.get_notes())

def choose_notebook(title):
    return choose(title, pw.notebooks)

def choose_note_and_notebook(title):
    return choose(title, pw.get_notes() + pw.get_notebooks())

def choose_tag(title):
    return choose(title, pw.tags)

def prompt(text, important = False):
    answers = ('y', 'Y', 'yes', 'Yes', 'YES')
    if important:
        text = text + ' y/N'
    else:
        text = text + ' Y/n'
        answers += ('',)
    answer = getpass(text)
    if answer in answers:
        return True
    return False

def edit(title):
    note = choose_note(title)
    logger.info('Getting $EDITOR')
    editor = os.environ.get('EDITOR')

    tempfile = '/tmp/paperwork-{}'.format(note.title)

    logger.info('Writing content to temporary file')
    with open(tempfile, 'w') as f:
        f.write(note.content)

    logger.info('Launching system editor')
    os.system("{} '{}'".format(editor, tempfile))

    logger.info('Reading contents of temporary file')
    with open(tempfile, 'r') as f:
        note.content = f.read()

    logger.info('Removing temporary file')
    os.remove(tempfile)

def delete(title):
    elem = choose_note_and_notebook(title)
    elem_type = 'note' if isinstance(elem, models.Note) else 'notebook'
    if prompt('Delete {} {}?'.format(elem_type, elem.title), True):
        logging.info('Deleting elem {}'.format(elem))
        elem.delete()

def move(args):
    args = args.split('to')
    note = choose_note(args[0])
    notebook = choose_notebook(args[1])
    if prompt('Move note {} to {}?'.format(note.title, notebook.title)):
        note.move_to(notebook)

def create(args):
    if ' in ' in args:
        args = args.split(' in ')
        note_title = args[0]
        notebook = choose_notebook(args[1])
        if prompt('Create note {} in {}?'.format(note_title, notebook.title)):
            notebook.create_note(note_title)
    else:
        nb_title = args
        if prompt('Create notebook {}?'.format(nb_title)):
            pw.add_notebook(nb_title)

def tags():
    for tag in pw.tags:
        print(tag.title)

def tag(args):
    if ' with ' in args:
        args = args.split(' with ')
        note = choose_note(args[0])
        tag = choose_tag(args[1])
        if prompt('Tag note {} with {}?'.format(note.title, tag.title)):
            note.add_tag(tag)
    else:
        tag_title = args
        if prompt('Create tag {}?'.format(tag_title)):
            pw.add_tag(tag_title)

def tagged(tag_title):
    tag = choose_tag(tag_title)
    print('Notes tagged with {}'.format(tag.title))
    for note in tag.notes:
        print(note.title)

def print_help():
    print("""The commands are self-explanatory. Notes and notebooks are chosen through a fuzzy search.

update
ls
edit $note
delete $title - takes effect on notes and notebooks
move $note to $notebook
create $note in $notebook - keyword 'in'
create $notebook
tags - print tags
tag $note with $tag - tag $note with $tag
tag $tag - create $tag
tagged $tag - print notes tagged with $tag
exit
""")

cmd_dict = {
        'update': update,
        'ls': print_all,
        'edit': edit,
        'delete': delete,
        'move': move,
        'create': create,
        'tags': tags,
        'tag': tag,
        'tagged': tagged,
        'help': print_help
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level = logging.INFO)
    login()
    download()

    cmd = input('>')
    while (cmd != 'exit'):
        logger.info(cmd)
        if ' ' in cmd:
            cmd = cmd.split(' ', 1)
            args = cmd[1]
            cmd = cmd[0]
        else:
            args = None
        if cmd in cmd_dict.keys():
            if args:
                cmd_dict[cmd](args)
            else:
                cmd_dict[cmd]()
        else:
            logger.info('Invalid command')
            print('{} unkown'.format(cmd))
        cmd = input('>')

if __name__ == "__main__":
    main()
