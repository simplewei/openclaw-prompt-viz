import re
import requests
from urllib.parse import urlparse, parse_qs

# 从文档内容中提取的图片URL（从上面的mcporter输出获取）
image_urls = [
    # 周边一公里
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/31a86158-1ddf-4e43-a59f-2e9a1087fc80.png",
    # 周边2公里 (6张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/38cef4d2-8eb9-4838-b254-6e203c58ee20.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/25988c6d-9698-448f-975a-48b1499447d7.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/1e3747a6-d0dd-40ce-998a-d03e4e3ee666.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/16ee1a47-66ec-4460-b226-28a9f0e5f568.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/3d3c3b52-0a3b-4983-b210-2f3b1795e30e.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/8f1c23d0-0e39-42c7-b2f2-723747db2350.png",
    # 周边3公里 (3张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/eb568327-6b59-4861-a9ff-24f8a4f014b5.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/f9ea1358-4414-42a7-9531-00abdc8146a1.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/8dd0afd0-deca-41bd-8efd-670be1ba721d.png",
    # 大众点评评分
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/e9944cd8-8fbc-4cf4-89ea-0d304b7bcd29.jpeg",
    # 轻拍羽毛球馆
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/d86b1772-ddcb-4579-877d-ddece0b51570.jpeg",
    # 项目周边羽毛球馆
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/2f90552e-941a-4c2a-aca7-e0cc7790d099.jpeg",
    # 李煮厨&尤尼克斯羽毛球馆 (2张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/5e888ee9-155f-4222-9054-7b5f8330af3c.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/b9c270f3-97c0-4b2a-9d59-c4f741d6943d.jpeg",
    # GAPS 梦立方羽毛球馆 (2张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/65b0f81c-f30c-4bb8-8218-381ab658a8bb.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/c35a9183-3b73-41bb-971b-c31c3f940085.jpeg",
    # 瑞怡羽毛球馆 (2张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/e7fe07a6-2a61-4073-a452-e0a56fc8ffe2.jpeg",
    # LYB羽毛球运动中心 (2张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/13783871-a899-4f95-946c-ed7aecb01da2.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/41305c55-c9e9-4442-9517-e3b83ab9871e.jpeg",
    # 瑞怡羽毛球馆 (additional)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/03ab8e8c-7fb1-4f89-b58b-6ee1bdba048e.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/11f11488-a8fc-4186-b75e-01befc08bd81.jpeg",
    # 五星体育系列 (多张)
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/c6c0377a-f8fd-4e3e-a8e7-c8205fe3bc3f.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/18170a71-1ecf-44aa-afb7-6e21885dabf7.png",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/5cf21f96-af72-4dbb-8366-fac5530ef8e2.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/b90ae208-03a1-4947-b64b-dd8009498bc4.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/f46e264a-3b4b-4eec-8c22-4d15e7c64115.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/402bf1b4-a4b9-432e-bcd0-9ada7a8a789e.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/4dad67cf-0b4b-4a1c-b3a1-82eb9b747f4a.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/4804da5b-3aac-4a6c-a0d3-7596e04d34df.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/d016ca88-e554-4afa-8a2f-9a69605ee7bb.jpeg",
    "https://alidocs2.oss-cn-zhangjiakou.aliyuncs.com/res/J9LnW6jgL2P5WlvD/img/6432aa12-02e5-4b32-87fc-3ef02f60cd96.jpeg",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

for idx, url in enumerate(image_urls, 1):
    try:
        # 生成简洁的文件名
        filename = f"{idx:02d}_{url.split('/')[-1].split('?')[0].replace('.jpeg', '.jpg').replace('.png', '.png')}"
        print(f"Downloading {idx}/{len(image_urls)}: {filename}")
        
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Saved: {filename} ({len(response.content)} bytes)")
        else:
            print(f"  ✗ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDownload complete!")
