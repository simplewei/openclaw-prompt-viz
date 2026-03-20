# 文档存储配置（2026-03-20）

## 默认目标目录

**目录ID**：`1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2`  
**目录链接**：https://alidocs.dingtalk.com/i/nodes/1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2  
**指定时间**：2026-03-20 02:56 UTC  
**指定人**：小酷容

## 已迁移/生成文档

| 文档标题 | 文档ID | 链接 |
|---------|--------|------|
| 机器人&AI硬件决策简报（2026） | QPGYqjpJYrlev9qkIo2zem6w8akx1Z5N | [查看](https://alidocs.dingtalk.com/i/nodes/QPGYqjpJYrlev9qkIo2zem6w8akx1Z5N) |
| 文档目录配置规范 | 14dA3GK8gjg2mnK3t7Pk1dR2J9ekBD76 | [查看](https://alidocs.dingtalk.com/i/nodes/14dA3GK8gjg2mnK3t7Pk1dR2J9ekBD76) |

## 技术实现

### 创建文档时指定父目录

```python
# 使用 dingtalk-docs 技能
create_doc_under_node(
    name="文档标题",
    parentDentryUuid="1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2"  # 固定为此目录
)
```

### CLI 脚本用法

```bash
# 创建到目标目录（需修改脚本或传递参数）
python create_doc.py "标题" "内容" --parent 1R7q3QmWee9XZaQbfXGzMRQmWxkXOEP2
```

---

**生效状态**：✅ 已生效  
**后续文档**：将全部保存到此目录