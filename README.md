# IPTV M3U 播放列表自动更新器

[![Update IPTV M3U Playlist](https://github.com/lfdao/vtpi-m3u/actions/workflows/update_m3u.yml/badge.svg)](https://github.com/lfdao/vtpi-m3u/actions/workflows/update_m3u.yml)

这是一个自动化工具，定期从 [iptvcat.com](https://iptvcat.com) 网站获取指定国家或地区的 IPTV M3U8 播放列表，将它们合并成一个单一的、去重的 M3U 文件，并利用 GitHub Actions 实现云端自动更新和托管。

## ✨ 功能特点

- 🌍 **多地区支持**: 支持同时抓取多个国家/地区的播放列表
- 🔄 **自动更新**: 利用 GitHub Actions 实现每日自动更新
- 🎯 **智能去重**: 基于流地址自动去除重复频道
- 📱 **即开即用**: 生成的播放列表可直接导入各种播放器
- ⚡ **高效稳定**: 内置重试机制和异常处理
- 🆓 **完全免费**: 基于 GitHub 平台，无需服务器成本

## 📺 支持的播放器

生成的 M3U 文件兼容以下播放器：
- VLC Media Player
- Kodi
- Perfect Player
- IPTV Smarters
- GSE Smart IPTV
- 以及其他支持 M3U 格式的播放器

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角的 "Fork" 按钮，将本仓库复制到您的 GitHub 账户下。

### 2. 配置地区列表

编辑 `config.json` 文件，添加您需要的地区：

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

### 3. 启用 GitHub Actions

1. 进入您 Fork 的仓库
2. 点击 "Actions" 标签页
3. 点击 "I understand my workflows, go ahead and enable them"

### 4. 手动运行测试

1. 在 Actions 页面，点击 "Update IPTV M3U Playlist" 工作流
2. 点击 "Run workflow" 按钮
3. 等待运行完成，检查是否生成了 `master.m3u` 文件

### 5. 获取播放列表链接

运行成功后，您的播放列表地址为：
```
https://raw.githubusercontent.com/lfdao/vtpi-m3u/main/master.m3u
```

将此链接添加到您的播放器中即可。

## 🌍 可用地区列表

您可以在 [iptvcat.com](https://iptvcat.com) 上查看所有可用的国家和地区。常见的地区标识符包括：

| 地区 | 标识符 | 地区 | 标识符 |
|------|--------|------|--------|
| 香港 | `hong_kong__3` | 台湾 | `taiwan__3` |
| 中国 | `china__3` | 美国 | `united_states_of_america__3` |
| 英国 | `united_kingdom__3` | 日本 | `japan__3` |
| 韩国 | `south_korea__3` | 德国 | `germany__3` |

> **获取地区标识符的方法：**
> 访问 iptvcat.com，选择目标国家/地区，观察浏览器地址栏中的标识符部分。

## 📋 配置说明

### config.json 参数详解

- `regions`: 需要抓取的地区列表（必需）
- `output_file`: 输出文件名，默认为 `master.m3u`
- `user_agent`: HTTP 请求的用户代理字符串
- `request_timeout`: 请求超时时间（秒）
- `max_retries`: 最大重试次数

### 定时更新设置

默认情况下，播放列表会在每天北京时间上午8点自动更新。您可以修改 `.github/workflows/update_m3u.yml` 中的 cron 表达式来改变更新时间：

```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 时间每天 0 点 (北京时间 8 点)
```

## 🔧 本地运行

如果您想在本地运行此程序：

```bash
# 克隆仓库
git clone https://github.com/lfdao/vtpi-m3u.git
cd vtpi-m3u

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py
```

## 📊 运行状态

您可以通过以下方式查看更新状态：

1. **Actions 页面**: 查看每次运行的详细日志
2. **徽章状态**: README 顶部的徽章显示最近的运行状态
3. **提交历史**: 每次更新都会自动提交，可查看更新频率

## ⚠️ 注意事项

1. **合规使用**: 请确保您使用播放列表的行为符合相关法律法规
2. **内容责任**: 本工具仅提供技术聚合，不对播放内容负责
3. **稳定性**: 由于依赖第三方网站，服务可能受到源站变化影响
4. **频率限制**: 避免过于频繁的更新，以免给源站造成压力

## 🐛 常见问题

### Q: 为什么某些地区没有获取到频道？
A: 可能的原因包括：
- 地区标识符错误
- 目标地区暂时没有可用频道
- 网络连接问题
检查 Actions 运行日志可以获取详细错误信息。

### Q: 如何添加更多地区？
A: 编辑 `config.json` 文件，在 `regions` 数组中添加新的地区标识符，提交更改即可。

### Q: 播放列表多久更新一次？
A: 默认每天更新一次。您可以修改 workflow 文件中的 cron 表达式来调整频率。

### Q: 生成的播放列表为什么有些频道无法播放？
A: 这是正常现象，因为：
- 部分直播源可能临时离线
- 某些源可能有地理位置限制
- 源站可能更改了直播地址

## 📄 许可证

本项目采用 MIT 许可证。详细信息请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目！

---

**⭐ 如果这个项目对您有帮助，请考虑给它一个 Star！** 