import itertools
import re
import os
import time as pytime
from datetime import datetime
from scrapy.shell import inspect_response


import lxml.html
import scrapy

REPLY_REGEX = re.compile("\((\d+)篇回复\)")
TID_REGEX = re.compile("tid-(\d+)")
TIME_REGEX = re.compile("发表于 (.*)\t")
FORUM_PAGE = re.compile("page=(\d+)")


class S1Spider(scrapy.Spider):
    name = "s1"
    fourm_ids = [75, 51, 77, 6, 4, 48, 50, 77]

    def start_requests(self):
        yield scrapy.FormRequest("https://bbs.saraba1st.com/2b/member.php?mod=logging&action=login&loginsubmit=yes"
                                 "&infloat=yes&lssubmit=yes&inajax=1", formdata={
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
            "fastloginfield": "username",
            "quickforward": "yes",
            "handlekey": "ls"
        })


    def parse(self, response: scrapy.http.TextResponse):
        if "login" in response.url:
            pages_to_fetch = int(self.settings.get("PAGES_TO_FETCH", 10))
            for id in S1Spider.fourm_ids:
                for i in range(1, pages_to_fetch + 1):
                    yield scrapy.Request("https://bbs.saraba1st.com/2b/archiver/fid-{}.html?page={}".format(id, i))
            return
        if "fid" in response.url:
            pageno = get_page(response.url)
            fid = int(re.search("fid-(\d+)", response.url).group(1))
            for offset, item in enumerate(response.xpath("//*[@id=\"content\"]/ul[@type=1]/li")):
                html = item.get()
                matcher = REPLY_REGEX.search(html)
                if matcher:
                    replies = int(matcher.group(1)) + 1
                    thread_url = item.css("a::attr(href)").get()
                    yield {
                        "type": "thread",
                        "title": item.css("a::text").get(),
                        "tid": self._tid_from_url(thread_url),
                        "fid": fid,
                        "replies": replies,
                        "index": (pageno - 1) * 50 + offset
                    }
                    yield response.follow(thread_url, meta={
                        "replies": replies, "firstpage": True,
                        "replies_in_page": min(replies, 30),
                        "fid": fid
                    })

        else:
            body = response.css("#content").get()
            if body:
                if "cached" not in response.flags:
                    pageno = get_page(response.url)
                    posts = parse_posts(response, pageno)
                    for post in posts:
                        post["tid"] = self._tid_from_url(response.url)
                        post["type"] = "reply"
                        post["fid"] = response.meta.get("fid")
                        yield post
                else:
                    # Skip update when response is cached.
                    yield {
                        "tid": self._tid_from_url(response.url),
                        "type": "cached",
                    }
                if response.meta.get("firstpage", False):
                    replies = response.meta["replies"]
                    baseurl = response.url
                    for post_index in range(30, replies, 30):
                        pageno = post_index // 30 + 1
                        replies_in_page = min(replies - post_index, 30)
                        yield response.follow(baseurl + "?page=" + str(pageno), meta={
                            "replies_in_page": replies_in_page,
                            "fid": response.meta.get("fid")
                        })
            else:
                yield {
                    "tid": self._tid_from_url(response.url),
                    "type": "reply",
                    "authorized": False
                }

    def _tid_from_url(self, url):
        return int(TID_REGEX.search(url).group(1))


def get_page(url):
    match = FORUM_PAGE.search(url)
    if match:
        return int(match.group(1))
    else:
        return 1

def parse_posts(response: scrapy.http.TextResponse, pageno):
    nodes = response.xpath('//div[@id="content"]/*')[:-1]
    index = 0
    is_author_node = lambda x: getattr(x, "attrib", {}) == {'class': 'author'}
    result = []
    while not is_author_node(nodes[index]):
        index += 1
    while index < len(nodes):
        _, author, time = nodes[index].xpath("node()")
        author = author.xpath("text()").get()
        time = time.re(TIME_REGEX)[0] + " +0800"
        time = datetime.strptime(time, "%Y-%m-%d %H:%M %z")
        index += 1
        content_nodes = list(itertools.takewhile(lambda x: not is_author_node(x), nodes[index:]))
        index += len(content_nodes)
        content = []
        for node in content_nodes:
            root = node.root
            if isinstance(root, str):
                line = root
            else:
                line = lxml.html.tostring(node.root, method="text", encoding=str)
            if not line.isspace():
                content.append(line)
        content = "\n".join(content).replace("\t", "")
        result.append({
            "author": author,
            "time": time,
            "content": content
        })
    for offest, item in enumerate(result):
        item["index"] = (pageno - 1) * 30 + offest
    return result
