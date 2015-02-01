#!/usr/bin/env python3

from paperworks.models import Paperwork, Note
import os
import sys
import logging
import yaml
import argparse
import tempfile

if str(sys.version[0]) < '3':
    input = raw_input

logger = logging.getLogger('paperworkcli')

pw = None


def login():
    """Creates Paperwork instance.
    Reads credentials from rc-file or prompts."""
    global pw
    rc = os.environ.get('HOME')+'/.paperworkrc'
    if os.path.exists(rc):
        with open(rc, 'r') as f:
            conf = yaml.load(f)
        host = conf['host']
        user = conf['user']
        passwd = conf['pass']
    else:
        from getpass import getpass
        host = input('Host:')
        user = input('User:')
        passwd = getpass('Password:')
    pw = Paperwork(user, passwd, host)
    if not pw.authenticated:
        print('User/password not valid or host not reachable.')
        sys.exit()


def download():
    """Fills Paperwork instance with information from server."""
    pw.download()


def update():
    """Synchronizes local and remote information."""
    pw.update()


def print_all():
    for nb in pw.get_notebooks():
        print(nb.title)
        for note in nb.get_notes():
            print("- {}".format(note.title))


def print_notes():
    for note in pw.get_notes():
        print(note.title)


def choose_note(title):
    return pw.fuzzy_find_note(title)


def choose_notebook(title):
    return pw.fuzzy_find_notebook(title)


def choose_tag(title):
    return pw.fuzzy_find_tag(title)


def prompt(text, important=False):
    """Prompts user for confirmation.
    If important is true, pressing 'Enter' means no."""
    answers = ('y', 'Y', 'yes', 'Yes', 'YES')
    if important:
        text = text + ' y/N'
    else:
        text = text + ' Y/n'
        answers += ('',)
    answer = input(text + ' ')
    if answer in answers:
        return True
    return False


def edit(title):
    """Edit note with title."""
    note = choose_note(title)
    logger.info('Getting $EDITOR')
    editor = os.environ.get('EDITOR')

    tmpfile = tempfile.NamedTemporaryFile()

    logger.info('Writing content to temporary file')
    with open(tmpfile, 'w') as f:
        f.write(note.content)

    logger.info('Launching system editor')
    os.system("{} '{}'".format(editor, tmpfile.name))

    logger.info('Reading contents of temporary file')
    with open(tmpfile, 'r') as f:
        note.content = f.read()

    logger.info('Removing temporary file')
    tmpfile.close()


def delete(args):
    """Delete note or notebook, depending on input."""
    if ' in ' in args:
        args = args.split(' in ')
        note = choose_note(args[0])
        notebook = choose_notebook(args[1])
        if prompt('Delete note {} in {}?'.format(note.title, notebook.title)):
            note.delete()
    else:
        notebook = choose_notebook(args)
        if prompt('Delete notebook {}?'.format(notebook.title)):
            pw.delete_notebook(notebook)


def move(args):
    """Move a note to another notebook."""
    args = args.split('to')
    note = choose_note(args[0])
    notebook = choose_notebook(args[1])
    if prompt('Move note {} to {}?'.format(note.title, notebook.title)):
        note.move_to(notebook)


def create(args):
    """Creates note or notebook, depending on input."""
    if ' in ' in args:
        args = args.split(' in ')
        note_title = args[0]
        notebook = choose_notebook(args[1])
        if prompt('Create note {} in {}?'.format(note_title, notebook.title)):
            notebook.create_note(note_title)
    else:
        nb_title = args
        if prompt('Create notebook {}?'.format(nb_title)):
            pw.create_notebook(nb_title)


def tags():
    """Lists tags."""
    for tag in pw.get_tags():
        print(tag.title)


def tag(args):
    """Create a tag or tag a note with a tag, depending on input."""
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
    """Print notes tagged with tag."""
    tag = choose_tag(tag_title)
    print('Notes tagged with {}'.format(tag.title))
    for note in tag.notes:
        print(note.title)


def print_help():
    print("""The commands are self-explanatory. Notes, tags and notebooks are chosen through a fuzzy search.

update                      Pushes local changes to the remote host
ls                          List notebooks and notes
edit $note                  edit note
delete $notebook            delete notebook
delete $note in $notebook   delete note in notebook
move $note to $notebook     move note to notebook
create $note in $notebook   create note in notebook
create $notebook            create notebook
tags                        list tags
tag $note with $tag         tag note with tag
tag $tag                    create $tag
tagged $tag                 print notes tagged with $tag
exit                        exit application
"""
          )

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
    parser.add_argument(
        "-v", "--verbose", help="verbose output", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
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
            print('{} unknown'.format(cmd))
        cmd = input('>')

if __name__ == "__main__":
    main()
