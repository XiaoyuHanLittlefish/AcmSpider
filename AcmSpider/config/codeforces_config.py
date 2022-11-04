'''
get main page url of user
'''
def get_url(id) -> str:
    url = "https://codeforces.com/profile/" + id + "/"
    return url

USER_IDS = (
    'XiaoyuHan',
)

START_URLS = []
for id in USER_IDS:
    START_URLS.append(get_url(id))

