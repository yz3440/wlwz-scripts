# /Users/yfz/Developer/GitHub/video-subtitles-extract/video/yt
# /Users/yfz/Developer/GitHub/video-subtitles-extract/video/local


yt_url_str = """
https://www.youtube.com/watch?v=8rcFoN1Ding
https://www.youtube.com/watch?v=IstU4uhe6fQ
https://www.youtube.com/watch?v=bg-ngY9ozuo
https://www.youtube.com/watch?v=IlEJ_1WS63g
https://www.youtube.com/watch?v=oxF5rF5x3Ug
https://www.youtube.com/watch?v=z_zCQNArRcY
https://www.youtube.com/watch?v=lA6UH766xKg
https://www.youtube.com/watch?v=VSesXzrzfVw
https://www.youtube.com/watch?v=71rLg8_EMpk
https://www.youtube.com/watch?v=3KW3O0YD7KA
https://www.youtube.com/watch?v=p2oPnWzWPmI
https://www.youtube.com/watch?v=NKmIaLC3Bcw
https://www.youtube.com/watch?v=tbF7JD-dzo4
https://www.youtube.com/watch?v=Fs0Zc-Yi7Jc
https://www.youtube.com/watch?v=EeGdEPzI32g
https://www.youtube.com/watch?v=tZ-Xvrl09e0
https://www.youtube.com/watch?v=LZl2HSjSaLY
https://www.youtube.com/watch?v=G6ZJIwLQaIg
https://www.youtube.com/watch?v=bWVV6jPUrAo
https://www.youtube.com/watch?v=TQRP0Izap30
https://www.youtube.com/watch?v=wibs858Zbm0
https://www.youtube.com/watch?v=dE9CFg6pb50
https://www.youtube.com/watch?v=fdYQFAZ1g7Q
https://www.youtube.com/watch?v=Jf39SMLODyg
https://www.youtube.com/watch?v=bzm6Hiy93UI
https://www.youtube.com/watch?v=mJ2S6_4KQf0
https://www.youtube.com/watch?v=JvSAqrW9KJ0
https://www.youtube.com/watch?v=Leo4mG037e8
https://www.youtube.com/watch?v=dn4UovpT3bo
https://www.youtube.com/watch?v=xyyWCh7S7RQ
https://www.youtube.com/watch?v=7u6jyBU7n0w
https://www.youtube.com/watch?v=59KLnNwE7Zs
https://www.youtube.com/watch?v=gDMmLxSELvc
https://www.youtube.com/watch?v=FAs9TvGfWFc
https://www.youtube.com/watch?v=34R-Ywm_qjQ
https://www.youtube.com/watch?v=Wy3AFtgafPQ
https://www.youtube.com/watch?v=IROLSJ-QTTU
https://www.youtube.com/watch?v=ISbqeVSB5IQ
https://www.youtube.com/watch?v=Z7nzCOF-SWo
https://www.youtube.com/watch?v=PRn6N5PUb1Q
https://www.youtube.com/watch?v=kmLw3GxSmR4
https://www.youtube.com/watch?v=aYoweEquq-c
https://www.youtube.com/watch?v=0palScyx7Ng
https://www.youtube.com/watch?v=5focg6pWDhc
https://www.youtube.com/watch?v=TuxMAzOXs90
https://www.youtube.com/watch?v=jEGU_HEshgg
https://www.youtube.com/watch?v=3ams8Zyy14I
https://www.youtube.com/watch?v=NeypdebEMSg
https://www.youtube.com/watch?v=iGdxzX1tSPk
https://www.youtube.com/watch?v=iHSTb0MsX4k
https://www.youtube.com/watch?v=gHk9V163coc
https://www.youtube.com/watch?v=QS8BQL7O_JA
https://www.youtube.com/watch?v=AFID7LMSOZA
https://www.youtube.com/watch?v=RzkoR36-6Sg
https://www.youtube.com/watch?v=_4Y30IpLm6s
https://www.youtube.com/watch?v=amEuDQfXRDU
https://www.youtube.com/watch?v=Zf0lXW4D0VY
https://www.youtube.com/watch?v=g0mdgY1fQvY
https://www.youtube.com/watch?v=emhHjO6yI-w
https://www.youtube.com/watch?v=2wKNIpZV_18
https://www.youtube.com/watch?v=QfT4aJoMT6U
https://www.youtube.com/watch?v=sK9aj1OM9Hk
https://www.youtube.com/watch?v=X9irjuO_BMM
https://www.youtube.com/watch?v=hbKlbMBCS0I
https://www.youtube.com/watch?v=MRtvcfY6GRk
https://www.youtube.com/watch?v=tZuGsMGgq-w
https://www.youtube.com/watch?v=gLavrxCD-og
https://www.youtube.com/watch?v=jJ8rVK25yGM
https://www.youtube.com/watch?v=Hjk9oyAHT8U
https://www.youtube.com/watch?v=WMEFahJ5UQs
https://www.youtube.com/watch?v=1_ATPc42jo0
https://www.youtube.com/watch?v=mMJjWKd_MG4
https://www.youtube.com/watch?v=IoHYfmnjSFQ
https://www.youtube.com/watch?v=TlDS2-6ERpI
https://www.youtube.com/watch?v=IeUP6BBzNVA
https://www.youtube.com/watch?v=D8XYDtn2Q7Q
https://www.youtube.com/watch?v=z7ee_Yyr9nw
https://www.youtube.com/watch?v=9kTVSGJIFPY
https://www.youtube.com/watch?v=5eGTFQTjB5g
https://www.youtube.com/watch?v=Rrj3pn9VM0s
"""

yt_urls = yt_url_str.split("\n")
yt_urls = [url.strip() for url in yt_urls if url.strip()]
import os

# recursively find all the webm files
webm_files = []
for root, dirs, files in os.walk("./video"):
    for file in files:
        if file.endswith(".webm"):
            webm_files.append(os.path.join(root, file))

print(webm_files)


video_meta = []

for file in webm_files:
    # filename
    filename = os.path.basename(file)
    # file name looks like episode-10.webm, get the episode number
    episode_number = filename.split("-")[1].split(".")[0]
    print(episode_number)

    # use opencv to read the video and get dimensions
    import cv2

    cap = cv2.VideoCapture(file)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    youtube_url = yt_urls[int(episode_number) - 1]

    local_path = f"./video/episode-{episode_number}.webm"
    video_meta.append(
        {
            "episode_number": episode_number,
            "youtube_url": youtube_url,
            "local_path": local_path,
            "width": width,
            "height": height,
            "subtitle_boundingbox": {"x": 37, "y": 399, "w": 493, "h": 30},
        }
    )

# sort video meta by episode number
video_meta.sort(key=lambda x: int(x["episode_number"]))

print(video_meta)

# save video meta to json
import json

with open("video_meta.json", "w") as f:
    json.dump(video_meta, f, indent=2, ensure_ascii=False)
