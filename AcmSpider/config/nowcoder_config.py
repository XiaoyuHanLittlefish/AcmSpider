'''
get main page url of user
'''
def get_url(id) -> str:
    url = "https://ac.nowcoder.com/acm/contest/profile/" + id + "/practice-coding/"
    return url

USER_IDS = (
    '638501054',
)

START_URLS = []
for id in USER_IDS:
    START_URLS.append(get_url(id))

