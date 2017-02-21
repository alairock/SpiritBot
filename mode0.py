from fun import SpiritBot

SpiritBot._USERNAME = 'cowninja2299'
SpiritBot._PASSWORD = 'Fine9955'
SpiritBot._UNWANTED_USERS_WITH_WORD = ['mom']

SpiritBot.like(
    similar_users=['rstd', 'wfpg', 'tdhn', 'al4b'],
    similar_tags=['arst', 'arst', 'rstd'],
    do_not_like_tags=[],
    do_not_like_users=[],
    max_tag_likes=50,
    max_user_likes=50,
    likes_per_day=(300, 350),
    likes_interval=(1, 2)
)

SpiritBot.unlike(
    do_not_unlike_users=['rstd', 'wfpg', 'tdhn', 'al4b'],
    unlikes_per_day=(300, 350),
    unlike_interval=(1, 2)
)

SpiritBot.follow(
    similar_users=['rstd', 'wfpg', 'tdhn', 'al4b'],
    similar_tags=['arst', 'arst', 'rstd'],
    do_not_follow_users=['zac_efrain'],
    follows_per_day=(300, 350),
    follow_interval=(1, 2)
)

SpiritBot.unfollow(
    do_not_unfollow_users=['rstd', 'wfpg', 'tdhn', 'al4b'],
    unfollows_per_day=(300, 350),
    unfollow_interval=(1, 2)
)

SpiritBot.log_stdout()  # TODO: Configurable stats

SpiritBot.run()
