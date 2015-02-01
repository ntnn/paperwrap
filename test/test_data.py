notebook_id = '1'
notebook2_id = '2'
new_notebook_id = '2'
notebook_title = 'notebook title'
notebook_type = '0'
notebook = {
    'id': notebook_id,
    'title': notebook_title,
    'type': notebook_type
    }
notebook2 = {
    'id': notebook2_id,
    'title': notebook_title,
    'type': notebook_type
    }
notebooks = [
    notebook,
    notebook2
    ]

version_id = '10'
version2_id = '11'
version = {
    'id': version_id
    }
version2 = {
    'id': version2_id
    }
versions = [
    version,
    version2
    ]

attachment_id = '55'
attachment2_id = '56'
attachment_file = 'attached.pdf'
attachment = {
    'id': attachment_id,
    'file': attachment_file
    }
attachment2 = {
    'id': attachment2_id,
    'file': attachment_file
    }
attachments = [
    attachment,
    attachment2
    ]

tag_id = '42'
tag2_id = '43'
tag_title = 'some_tag'

tag = {
    'id': tag_id,
    'title': tag_title,
    'visibility': 0
    }
tag2 = {
    'id': tag2_id,
    'title': tag_title,
    'visibility': 0
    }
tags = [
    tag,
    tag2
    ]

note_title = 'note title'
content = 'some content'
note_id = '4'
note2_id = '5'
note_updated_at = '2014-09-20 19:43:59'
note2_updated_at = '2014-09-19 19:43:59'

note = {
    'id': note_id,
    'title': note_title,
    'content': content,
    'notebook_id': notebook_id,
    'updated_at': note_updated_at,
    'tags': [
        tag
        ],
    'versions': [
        version
        ]
    }
note2 = {
    'id': note2_id,
    'title': note_title,
    'content': content,
    'notebook_id': notebook_id,
    'updated_at': note2_updated_at,
    'tags': [
        tag2
        ],
    'versions': [
        version2
        ]
    }
notes = [
    note,
    note2
    ]

keyword = 'test keyword'
keyword_b64 = 'dGVzdCBrZXl3b3Jk'

user = 'testuser'
passwd = 'testpassword'
upasswd = 'dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'
uri = 'demo.paperwork.rocks'
uri_correct = 'http://{}'.format(uri)
agent = 'dummy agent'

move = [{
        'notebook': notebook,
        'id': note_id,
        'notebook_id': notebook_id,
        'version_id': version_id
        }]

tagged = [
    note
    ]

search = [
    note2
    ]

i18n = {
    'holy': 'moly',
    'giant': 'dict'
    }

i18nkey = {
    'giant': 'dict'
    }

ret = {
    'notebooks':   notebooks,
    'notebook':    notebook,
    'notes':       notes,
    'note':        note,
    'move':        move,
    'versions':    versions,
    'version':     version,
    'attachments': attachments,
    'attachment':  attachment,
    'tags':        tags,
    'tag':         tag,
    'tagged':      tagged,
    'search':      search,
    'i18n':        i18n,
    'i18nkey':     i18n
    }
