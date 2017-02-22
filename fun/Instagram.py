import requests
import random
import time
import json


class Instagram:
    url = 'https://www.instagram.com/'
    url_tag = 'https://www.instagram.com/explore/tags/'
    url_like = 'https://www.instagram.com/web/likes/%s/like/'
    url_unlike = 'https://www.instagram.com/web/likes/%s/unlike/'
    url_comment = 'https://www.instagram.com/web/comments/%s/add/'
    url_follow = 'https://www.instagram.com/web/friendships/%s/follow/'
    url_unfollow = 'https://www.instagram.com/web/friendships/%s/unfollow/'
    url_query = 'https://www.instagram.com/query/'
    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'
    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
    url_user_detail = 'https://www.instagram.com/%s/?__a=1'
    user_agent = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36")
    accept_language = 'en-US;q=0.6,en;q=0.4'
    csrftoken = None
    user_id = None
    user_infos = {}
    logged_in_user = None

    def __init__(self, proxy=""):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        if proxy != "":
            proxies = {
                'http': 'http://' + proxy,
                'https': 'http://' + proxy,
            }
            self.session.proxies.update(proxies)

    def login(self, username, password):
        print('Trying to login as {}...\n'.format(username))
        self.session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                                     'ig_vw': '1920', 'csrftoken': '',
                                     's_network': '', 'ds_user_id': ''})
        self.session.headers.update({'Accept-Encoding': 'gzip, deflate',
                                     'Accept-Language': self.accept_language,
                                     'Connection': 'keep-alive',
                                     'Content-Length': '0',
                                     'Host': 'www.instagram.com',
                                     'Origin': 'https://www.instagram.com',
                                     'Referer': 'https://www.instagram.com/',
                                     'User-Agent': self.user_agent,
                                     'X-Instagram-AJAX': '1',
                                     'X-Requested-With': 'XMLHttpRequest'})
        r = self.session.get(self.url)
        self.session.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(2 * random.random())
        login = self.session.post(self.url_login, data={'username': username,
                                                        'password': password},
                                  allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())
        if login.status_code == 200:
            r = self.session.get(self.url)
            finder = r.text.find(username)
            if finder != -1:
                self.logged_in_user = self.get_user_info(username)
                print('Login Succeeded')
            else:
                print('Login error! Check your login data!')
        else:
            print('Login error! Connection error!')

    def get_user_info(self, username):
        if username not in self.user_infos:
            url_info = self.url_user_detail % username
            info = self.session.get(url_info)
            data = json.loads(info.text)
            self.user_infos[username] = data
            return data
        return self.user_infos[username]

    def get_followers_payload(self, user_info, cursor=None):
        q = 'ig_user(%s) {' % user_info['user']['id']
        qcursor = ' followed_by.first(20) {'
        if cursor is not None:
            qcursor = ' followed_by.after(%s, 20) {' % cursor
        q += qcursor + '''
            count,
            page_info {
              end_cursor,
              has_next_page
            },
            nodes {
                id,
                is_verified,
                followed_by {count},
                follows {count},
                followed_by_viewer,
                follows_viewer,
                requested_by_viewer,
                full_name,
                profile_pic_url,
                username
                }
            }
        }
        '''
        data = {'q': q, 'ref': 'relationships::follow_list'}
        r = self.session.post(self.url_query, data=data).json()
        follow_list = r['followed_by']['nodes']
        page_info = r['followed_by']['page_info']
        return follow_list, page_info['end_cursor'], page_info['has_next_page']

    def get_followers(self, username):
        user_info = self.get_user_info(username)
        page_limit = 0
        cursorz = None
        follow_list = []
        get_next = True
        while get_next and page_limit < 10:
            ulist, cursorz, get_next = self.get_followers_payload(
                user_info=user_info,
                cursor=cursorz)
            follow_list = follow_list + ulist
            page_limit += 1
            print('.', end='', flush=True)
            time.sleep(random.randint(1, 5))
        print(' ')
        return follow_list

    def get_random_media_by_tag(self, tag):
        pass

    def __post_event(self, url):
        try:
            response = self.session.post(url)
            if response.status_code == 200:
                print('... Complete:', flush=True)
            else:
                print('... ERROR on ' + url, flush=True)
                print(response.text)
            return response
        except:
            print('... Error!:', flush=True)

    def follow_user(self, user_id):
        url_follow = self.url_follow % user_id
        self.__post_event(url_follow)

    def unfollow_user(self, user_id):
        url_unfollow = self.url_unfollow % user_id
        self.__post_event(url_unfollow)

    def like_media(self, media_id):
        url_like = self.url_like % media_id
        self.__post_event(url_like)

    def unlike_media(self, media_id):
        url_unlike = self.url_unlike % media_id
        self.__post_event(url_unlike)
