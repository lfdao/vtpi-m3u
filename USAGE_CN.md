# IPTV M3U 播放列表自动更新器 - 使用说明

## 📋 项目概述

这是一个基于 Python 的自动化工具，可以从 iptvcat.com 网站抓取指定地区的 IPTV 播放列表，合并去重后生成统一的 M3U 文件，并通过 GitHub Actions 实现定时自动更新。

## 🎯 核心功能

1. **多地区抓取**: 支持同时抓取多个国家/地区的播放列表
2. **智能合并**: 自动合并多个 M3U 文件并去除重复频道
3. **定时更新**: 每天自动更新播放列表
4. **云端托管**: 利用 GitHub 免费托管和 CDN 加速
5. **即插即用**: 生成的播放列表可直接在各种播放器中使用

## 🚀 快速部署

### 步骤 1: 准备 GitHub 仓库

1. **Fork 本仓库** 或者 **创建新仓库并上传文件**
2. 确保仓库是公开的（这样生成的 M3U 文件才能被外部访问）

### 步骤 2: 配置地区列表

编辑 `config.json` 文件，设置您需要的地区：

```json
{
  "regions": [
    "hong_kong__3",
    "taiwan__3",
    "china__3"
  ],
  "output_file": "master.m3u",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "request_timeout": 30,
  "max_retries": 3
}
```

**获取地区标识符的方法:**
1. 访问 [iptvcat.com](https://iptvcat.com)
2. 点击您想要的国家/地区
3. 观察浏览器地址栏，例如：`https://iptvcat.com/hong_kong__3`
4. 复制 `hong_kong__3` 这部分作为标识符

### 步骤 3: 启用自动化

1. 进入您的 GitHub 仓库
2. 点击 `Actions` 标签页
3. 如果是第一次，点击 `I understand my workflows, go ahead and enable them`
4. 找到 `Update IPTV M3U Playlist` 工作流
5. 点击 `Run workflow` 进行首次手动运行

### 步骤 4: 获取播放列表

运行成功后，您的播放列表地址为：
```
https://raw.githubusercontent.com/lfdao/vtpi-m3u/main/master.m3u
```

## 📱 播放器配置

### VLC Media Player
1. 打开 VLC
2. 媒体 → 打开网络串流
3. 输入您的播放列表 URL
4. 点击播放

### Kodi
1. 安装 PVR IPTV Simple Client 插件
2. 配置 → PVR 客户端 → PVR IPTV Simple Client
3. 设置播放列表路径为您的 URL

### 移动端播放器
- **IPTV Smarters**: 添加播放列表 → 输入 URL
- **GSE Smart IPTV**: 添加远程播放列表 → 输入 URL

## ⚙️ 高级配置

### 修改更新频率

编辑 `.github/workflows/update_m3u.yml`，修改 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'    # 每天 UTC 0点 (北京时间 8点)
  - cron: '0 12 * * *'   # 每天 UTC 12点 (北京时间 20点)
```

### 添加更多地区

在 `config.json` 的 `regions` 数组中添加更多地区标识符：

```json
{
  "regions": [
    "hong_kong__3",
    "taiwan__3", 
    "china__3",
    "japan__3",
    "south_korea__3",
    "united_states_of_america__3"
  ]
}
```

### 自定义输出文件名

修改 `config.json` 中的 `output_file` 字段：

```json
{
  "output_file": "my_iptv_list.m3u"
}
```

## 🔧 本地运行

如果您想在本地测试：

```bash
# 克隆仓库
git clone https://github.com/lfdao/vtpi-m3u.git
cd vtpi-m3u

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py
```

## 📊 监控和维护

### 查看运行状态
1. 在 GitHub 仓库的 `Actions` 页面查看运行历史
2. 绿色勾号表示成功，红色 X 表示失败
3. 点击具体的运行记录可查看详细日志

### 常见问题排查

**问题**: 某些地区没有获取到频道
**解决**: 
- 检查地区标识符是否正确
- 查看 Actions 日志中的错误信息
- 该地区可能暂时没有可用频道

**问题**: 播放列表无法访问
**解决**:
- 确保仓库是公开的
- 检查文件路径是否正确
- 等待几分钟让 GitHub CDN 更新

**问题**: GitHub Actions 没有运行
**解决**:
- 确保已启用 Actions
- 检查 YAML 文件语法是否正确
- 仓库可能需要有活动才能触发定时任务

## 🌍 支持的地区

常见地区标识符：

| 地区 | 标识符 | 地区 | 标识符 |
|------|--------|------|--------|
| 香港 | `hong_kong__3` | 台湾 | `taiwan__3` |
| 中国大陆 | `china__3` | 澳门 | `macao__3` |
| 美国 | `united_states_of_america__3` | 加拿大 | `canada__3` |
| 英国 | `united_kingdom__3` | 德国 | `germany__3` |
| 法国 | `france__3` | 意大利 | `italy__3` |
| 日本 | `japan__3` | 韩国 | `south_korea__3` |
| 泰国 | `thailand__3` | 新加坡 | `singapore__3` |
| 马来西亚 | `malaysia__3` | 印度尼西亚 | `indonesia__3` |
| 印度 | `india__3` | 澳大利亚 | `australia__3` |

> 完整列表请访问 [iptvcat.com](https://iptvcat.com) 查看

## ⚠️ 重要提醒

1. **合法使用**: 仅用于技术学习和个人使用，请遵守相关法律法规
2. **内容责任**: 本工具仅提供技术手段，不对播放内容承担责任
3. **稳定性**: 依赖第三方网站，可能受源站变化影响
4. **更新频率**: 建议不要过于频繁更新，避免给源站造成压力

## 🤝 技术支持

如遇到问题，请：
1. 查看 GitHub Actions 的运行日志
2. 检查本使用说明是否遗漏步骤
3. 在仓库中提交 Issue 描述问题

---

**祝您使用愉快！** 