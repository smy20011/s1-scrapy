# Install

```bash
git clone this repository
pip3 install scrapy
```

# Usage

```bash
export USERNMAE=your_s1_user_name
export PASSWORD=your_s1_password
cd s1
scrapy crawl s1
```

# Output

A file in current directory in format of jsonlines. It contains two type of output.

Thread json example.

```
{"type": "thread", "title": "【S1移动客户端汇总 2020/7/7】", "tid": 1486168, "fid": 75, "replies": 193, "index": 351}
```

Reply json exmaple.
```
{"author": "星野心叶", "time": "2020-07-01 15:08:00", "content": "\r\n软件bug吧，我x和xr都遇到过，后来更新到某一版ios以后就没遇见过了", "index": 2, "tid": 1944844, "type": "reply", "fid": 51}
```

You need to split these two type of jsons later.

# Spider settings

PAGES\_TO\_FETCH: Number of pages to fetch for each forum. Default 100

To change this setting, pass it to the scrapy command lines.

```
scrapy crawl s1 -s PAGES_TO_FETCH=100
```

To change the target forums, change the list named fourm\_ids in s1/s1/spiders/spider.py
