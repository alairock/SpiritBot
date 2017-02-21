import random
import time
import requests
import asyncio
from fun.Instagram import Instagram
from fun import db

_USERNAME = None
_PASSWORD = None
_UNWANTED_USERS_WITH_WORD = []
_UNWANTED_USERS_WITH_WORD_DEFAULT = ['pink',
    'second', 'stuff', 'art', 'project', 'love', 'life', 'food', 'blog',
    'free', 'keren', 'photo', 'graphy', 'indo', 'travel', 'art', 'shop',
    'store', 'sex', 'toko', 'jual', 'online', 'murah', 'jam', 'kaos', 'case',
    'baju', 'fashion', 'corp', 'tas', 'butik', 'grosir', 'karpet', 'sosis',
    'salon', 'skin', 'care', 'cloth', 'tech', 'rental',  'kamera', 'beauty',
    'express', 'kredit', 'collection', 'impor', 'preloved', 'follow',
    'follower', 'gain', '.id', '_id', 'bags']

_LIKE = False
_LIKE_DATA = {}
_UNLIKE = False
_UNLIKE_DATA = {}
_FOLLOW = False
_FOLLOW_DATA = {}
_UNFOLLOW = False
_UNFOLLOW_DATA = {}
_STDOUT = False

_SESSION = requests.Session()
_DB = None


def like(
        similar_users=[],
        similar_tags=[],
        do_not_like_tags=[],
        do_not_like_users=[],
        max_tag_likes=50,
        max_user_likes=50,
        likes_per_day=(300, 350),
        likes_interval=(5, 20)):
    global _LIKE, _LIKE_DATA
    _LIKE = True
    _LIKE_DATA = {
        'similar_users': similar_users,
        'similar_tags': similar_tags,
        'do_not_like_tags': do_not_like_tags,
        'do_not_like_users': do_not_like_users,
        'max_tag_likes': max_tag_likes,
        'max_user_likes': max_user_likes,
        'likes_per_day': likes_per_day,
        'likes_interval': likes_interval,
    }


def unlike(
        do_not_unlike_users=[],
        unlikes_per_day=(300, 350),
        unlike_interval=(1, 2)):
    global _UNLIKE, _UNLIKE_DATA
    _UNLIKE = True
    _UNLIKE_DATA = {
        'do_not_unlike_users': do_not_unlike_users,
        'unlikes_per_day': unlikes_per_day,
        'unlike_interval': unlike_interval
    }


def follow(
        similar_users=[],
        similar_tags=[],
        do_not_follow_users=[],
        follows_per_day=(300, 350),
        follow_interval=(1, 2)):
    global _FOLLOW, _FOLLOW_DATA
    _FOLLOW = True
    _FOLLOW_DATA = {
        'similar_users': similar_users,
        'similar_tags': similar_tags,
        'do_not_follow_users': do_not_follow_users,
        'follows_per_day': follows_per_day,
        'follow_interval': follow_interval
    }


def unfollow(
        do_not_unfollow_users=[],
        unfollows_per_day=(300, 350),
        unfollow_interval=(1, 2)):
    global _UNFOLLOW, _UNFOLLOW_DATA
    _UNFOLLOW = True
    _UNFOLLOW_DATA = {
        'do_not_unfollow_users': do_not_unfollow_users,
        'unfollows_per_day': unfollows_per_day,
        'unfollow_interval': unfollow_interval
    }


def log_stdout():
    global _STDOUT
    _STDOUT = True

async def is_user_desirable(user_info):
    if user_info['username'] in _FOLLOW_DATA['do_not_follow_users']:
        print('DO NOT FOLLOW:', user_info['username'])
        return False
    if any(zed in user_info['username'] for zed in _UNWANTED_USERS_WITH_WORD):
        print('UNDESIREABLE:', user_info['username'])
        return False
    if await db.previously_followed(user_info['username'], user_info['id']):
        print('ALREADY FOLLOWED:', user_info['username'])
        return False
    #  TODO IF spam or super_famous SKIP
    return True


async def exceeded_follow_count(fpd=(30, 45)):
    if await db.get_follow_count() < random.randint(fpd[0], fpd[1]):
        return False
    print('We have reached our follow count limit. Sleeping')
    return True

async def follow_users(instagram, user_list):
    fpd = _FOLLOW_DATA['follows_per_day']
    if not await exceeded_follow_count(fpd):
        for user_info in user_list:
            user_wanted = await is_user_desirable(user_info)
            if (not user_info['follows_viewer']
                    and not user_info['is_verified']
                    and user_wanted):
                print('FOLLOW USER:', user_info['username'], end='', flush=True)
                r = instagram.follow_user(user_info['id'])
                await db.insert_follow_count()
                await db.add_user_to_followed(user_info['username'],
                                              user_info['id'])
                fi = _FOLLOW_DATA['follow_interval']
                time.sleep(int(random.randint(fi[0], fi[1])) *
                           random.randint(20, 60) / random.randint(3, 5))
    #  TODO Save list to temp location, in case we exit or break

async def follow_program(instagram):
    #  TODO: Currently going off username suggestions.
    #  Tags will be the next step and is a better way to reach more
    #  followers without over harvesting usernames
    while True:
        for username in _FOLLOW_DATA['similar_users']:
            try:
                user_list = instagram.get_followers(username)
                await follow_users(instagram, user_list)
            except:
                print('Issue running {username}, skipping.'
                      .format(username=username))


async def asyncrunner():
    global _UNWANTED_USERS_WITH_WORD_DEFAULT, _UNWANTED_USERS_WITH_WORD
    _UNWANTED_USERS_WITH_WORD = _UNWANTED_USERS_WITH_WORD_DEFAULT + \
        _UNWANTED_USERS_WITH_WORD
    instagram = Instagram()
    instagram.login(_USERNAME, _PASSWORD)
    # print('I:', instagram.logged_in_user)
    if _LIKE:
        instagram.like_media('')
    if _UNLIKE:
        instagram.unlike_media('')
    if _FOLLOW:
        await follow_program(instagram)
    if _UNFOLLOW:
        instagram.unfollow_user('')
    if _STDOUT:
        print('std out')


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncrunner())


