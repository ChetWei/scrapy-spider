# -*- coding: utf-8 -*-

import hashlib

#将url 进行md5加密，去重策略
def get_md5(url):

    if isinstance(url,str):
        url = url.encode("utf-8")

    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == "__main__":
    print(get_md5("http://jobble.com"))
