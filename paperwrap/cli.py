"""Terminal client for paperwork.py"""

from . import models
from .utils import fuzzy_find
import os
import sys
import logging
import argparse
import tempfile

if str(sys.version[0]) < '3':
    input = raw_input

LOGGER = logging.getLogger(__name__)

PW = models.Paperwork(input('Host: '))
if not PW.authenticated:
    print('User/password not valid or host not reachable.')
    sys.exit()

SEP_NOTE_ATTACH = ' to '
SEP_NOTE_NB = ' in '


def download():
    """Fills Paperwork instance with information from server."""
    PW.download()


def update():
    """Synchronizes local and remote information."""
    PW.update()


def print_all():
    """Prints notebook and notes in alphabetical order."""
    for notebook in PW.get_notebooks():
        print(notebook.title)
        for note in notebook.get_notes():
            print("- {}".format(note.title))
            for attachment in note.attachments:
                print("-- {}".format(attachment.title))


def split(args, splitter):
    """Splits string with splitter and returns the resulting strings,

    if the splitter is in the string. If not None and the string is returned.
    :type args: str
    :type splitter: str
    :rtype: list or None and str
    """
    if splitter in args:
        return args.split(splitter, 1)
    else:
        return None, args


def split_args(args):
    """Splits sring into attachment, note and notebook string.

    :type args: str
    :rtype: list
    """
    attachment, args = split(args, SEP_NOTE_ATTACH)
    note, notebook = split(args, SEP_NOTE_NB)
    return attachment, note, notebook


def split_and_search_args(args):
    """Parses attachment, note and notebook.

    Returns a list of three items with [attachment, note, notebook]
    :type args: str
    :param bool search: If true the method searches for objects and
        returns them instead of strings.
    :rtype: list
    """
    attachment, note, notebook = split_args(args)
    notebook = fuzzy_find(notebook, PW.notebooks)
    if note:
        note = fuzzy_find(note, notebook.notes)
    if attachment:
        attachment = fuzzy_find(attachment, note.attachments)
    return attachment, note, notebook


def prompt(text, important=False):
    """Prompts user for confirmation.

    :type text: str
    :param bool important: If true the default answer is false.
    :rtype: bool
    """
    answers = ('y', 'Y', 'yes', 'Yes', 'YES')
    text += ' y/N' if important else ' Y/n'
    if not important:
        answers += ('',)
    answer = input(text + ' ')
    if answer in answers:
        return True
    return False


def edit(title):
    """Edit note with title.

    :type title: str
    """
    note = split_and_search_args(title)[1]
    LOGGER.info('Getting $EDITOR')
    editor = os.environ.get('EDITOR')

    tmpfile = tempfile.NamedTemporaryFile()

    LOGGER.info('Writing content to temporary file')
    with open(tmpfile, 'w') as f:
        f.write(note.content)

    LOGGER.info('Launching system editor')
    os.system("{} '{}'".format(editor, tmpfile.name))

    LOGGER.info('Reading contents of temporary file')
    with open(tmpfile, 'r') as f:
        note.content = f.read()

    LOGGER.info('Removing temporary file')
    tmpfile.close()

    LOGGER.info('Updating remote note')
    note.update()


def delete(args):
    """Delete note, notebook or attachment, depending on input.

    :type args: str
    """
    attachment, note, notebook = split_and_search_args(args)
    if attachment:
        if prompt('Delete attachment {} to {} in {}?'.format(
                attachment.title, note.title, notebook.title)):
            attachment.delete()
    elif note:
        if prompt('Delete note {} in {}?'.format(
                note.title, notebook.title)):
            note.delete()
    else:
        if prompt('Delete notebook {}?'.format(notebook.title)):
            PW.delete_notebook(notebook)


def move(args):
    """Move a note to another notebook.

    :type args: str
    """
    # splits off the new notebook at the end first, so it
    # doesn't mess with the split_args function
    args, notebook = split(args, ' to ')
    notebook = fuzzy_find(notebook, PW.notebooks)
    note = split_and_search_args(args)[1]
    if prompt('Move note {} to {}?'.format(note.title, notebook.title)):
        note.move_to(notebook)


def create(args):
    """Creates note or notebook, depending on input.

    :type args: str
    """
    if SEP_NOTE_NB in args:
        note, notebook = split_args(args)[1:]
        notebook = fuzzy_find(notebook, PW.notebooks)
        if prompt('Create note {} in {}?'.format(note, notebook.title)):
            notebook.create_note(note)
    else:
        if prompt('Create notebook {}?'.format(args)):
            PW.create_notebook(args)


def tags():
    """Lists tags."""
    for tag in PW.get_tags():
        print(tag.title)


def tag(args):
    """Create a tag or tag a note with a tag, depending on input.

    :type args: str
    """
    if ' with ' in args:
        # Again, split tag before
        args, tag = split(args, ' with ')
        tag = fuzzy_find(tag, PW.tags)
        note = split_and_search_args(args)[1]
        if prompt('Tag note {} with {}?'.format(note.title, tag.title)):
            note.add_tags([tag])
    else:
        if prompt('Create tag {}?'.format(args)):
            PW.add_tag(args)


def tagged(tag_title):
    """Print notes tagged with tag.

    :type tag_title: str
    """
    tag = fuzzy_find(tag_title, PW.tags)
    print('Notes tagged with {}'.format(tag.title))
    for note in tag.notes:
        print(note.title)


def upload(args):
    """Uploads a file as attacment to a note.

    :type args: str
    """
    filepath, note, notebook = split_args(args)
    notebook = fuzzy_find(notebook, PW.notebooks)
    note = fuzzy_find(note, notebook.notes)
    note.upload_file(filepath)


def print_help():
    """Prints commands and their usage to terminal."""
    print("""The commands are self-explanatory.
Notes, tags and notebooksare chosen through a fuzzy search.

update                                      Pushes local changes to the remote host
ls                                          List notebooks and notes
edit $note                                  edit note
delete $notebook                            delete notebook
delete $note in $notebook                   delete note in notebook
delete $attachment to $note in $notebook    Delete attachment to note in notebook
upload $filepath to $note in $notebook      Upload file at $filepath as attachment to note in notebook
move $note to $notebook                     move note to notebook
create $note in $notebook                   create note in notebook
create $notebook                            create notebook
tags                                        list tags
tag $note with $tag                         tag note with tag
tag $tag                                    create $tag
tagged $tag                                 print notes tagged with $tag
exit                                        exit application
"""
          )


CMD_DICT = {
    'update': update,
    'ls': print_all,
    'edit': edit,
    'delete': delete,
    'move': move,
    'create': create,
    'tags': tags,
    'tag': tag,
    'tagged': tagged,
    'help': print_help,
    'upload': upload
    }


def main():
    """Main function for terminal client.

    Awaits user input and executes the functions.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument(
        "--threading", help="enable multi-threading", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.threading:
        models.use_threading = True

    download()

    cmd = input('>')
    while cmd != 'exit':
        LOGGER.info(cmd)
        cmd, args = split(cmd, ' ')
        if cmd and cmd in CMD_DICT:
            CMD_DICT[cmd](args)
        elif args in CMD_DICT:
            CMD_DICT[args]()
        else:
            LOGGER.info('Invalid command')
            print('{} {} unknown'.format(cmd, args))
        cmd = input('>')

if __name__ == "__main__":
    main()
