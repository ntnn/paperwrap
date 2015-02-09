from fuzzywuzzy import fuzz
import logging

__all__ = ['fuzzy_find', 'find']

try:
    isinstance('string', basestring)
except NameError:
    basestring = str

logger = logging.getLogger(__name__)


def fuzzy_find(title, choices):
    """Fuzzy find for title in choices. Returns highest match.

    :type title: str
    :type choices: dict or list
    :rtype: Tag or Note or Notebook
    """
    if isinstance(choices, dict):
        choices = list(choices.values())
    top_choice = (0, None)
    for choice in choices:
        val = fuzz.ratio(choice.title, title)
        logger.info('{} to {}: {}'.format(choice.title, title, val))
        if val > top_choice[0]:
            top_choice = (val, choice)
    return top_choice[1]


def find(key, coll):
    """Finds key in given dict.

    :type key: str or int
    :type coll: dict
    :rtype: Notebook or Note or Tag or None
    """
    logger.info('Searching item for key {} of type {}'.format(
        key, type(key)))
    if isinstance(key, basestring):
        for item in coll.values():
            if key == item.title:
                return item
        logger.error('No item found for key {} of type {}'.format(
            key, type(key)))
    else:
        return coll[key]
