#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV M3U 播放列表自动更新器
从 iptvcat.com 获取指定地区的 M3U 播放列表并合并
"""

import json
import re
import sys
import time
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class IPTVCrawler:
    """IPTV Cat 网站爬虫类"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化爬虫
        
        Args:
            config_path: 配置文件路径
        """
        self.base_url = "https://iptvcat.com"
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式错误
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 验证必要的配置项
            if 'regions' not in config or not config['regions']:
                raise ValueError("配置文件中必须指定 'regions' 字段且不能为空")
            if 'output_file' not in config:
                raise ValueError("配置文件中必须指定 'output_file' 字段")
                
            return config
            
        except FileNotFoundError:
            print(f"错误: 配置文件 {config_path} 未找到")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件格式错误 - {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"错误: {e}")
            sys.exit(1)
            
    def _make_request(self, url: str, retries: int = None) -> Optional[requests.Response]:
        """发送HTTP请求并处理重试
        
        Args:
            url: 目标URL
            retries: 重试次数
            
        Returns:
            响应对象或None
        """
        if retries is None:
            retries = self.config.get('max_retries', 3)
            
        timeout = self.config.get('request_timeout', 30)
        
        for attempt in range(retries + 1):
            try:
                print(f"正在请求: {url} (尝试 {attempt + 1}/{retries + 1})")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"请求失败: {e}")
                if attempt < retries:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"请求 {url} 最终失败")
                    return None
                    
    def _extract_all_download_links(self, html_content: str, region: str) -> List[str]:
        """从页面HTML中提取所有频道的M3U下载链接
        
        Args:
            html_content: 页面HTML内容
            region: 地区标识
            
        Returns:
            下载链接列表
        """
        download_links = []
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 首先尝试寻找 "Download this list" 链接（整个列表的下载）
            list_download_links = soup.find_all('a', string=re.compile(r'Download this list', re.I))
            
            if list_download_links:
                print(f"找到 'Download this list' 链接")
                for link_elem in list_download_links:
                    href = link_elem.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                        download_links.append(full_url)
                        print(f"整个列表下载链接: {full_url}")
            
            # 如果没有找到整个列表的下载链接，则收集所有单个频道的下载链接
            if not download_links:
                print(f"未找到整个列表下载链接，开始收集单个频道链接...")
                
                # 寻找所有 "DOWNLOAD" 按钮或链接
                individual_links = soup.find_all('a', string=re.compile(r'DOWNLOAD', re.I))
                
                if not individual_links:
                    # 备用方案：寻找所有包含 .m3u 的链接
                    individual_links = soup.find_all('a', href=re.compile(r'\.m3u[8]?$', re.I))
                
                print(f"找到 {len(individual_links)} 个单个频道下载链接")
                
                for link_elem in individual_links:
                    href = link_elem.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href) if not href.startswith('http') else href
                        download_links.append(full_url)
                        
                        # 限制最多显示前5个链接的调试信息
                        if len(download_links) <= 5:
                            print(f"频道下载链接 {len(download_links)}: {full_url}")
                
                if len(download_links) > 5:
                    print(f"... 以及其他 {len(download_links) - 5} 个链接")
                    
        except Exception as e:
            print(f"解析 {region} 页面时出错: {e}")
            
        return download_links
            
    def _download_m3u_content(self, url: str) -> Optional[str]:
        """下载M3U文件内容
        
        Args:
            url: M3U文件URL
            
        Returns:
            M3U文件内容或None
        """
        response = self._make_request(url)
        if not response:
            return None
            
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    content = response.content.decode(encoding)
                    # 验证是否为有效的M3U文件
                    if '#EXTM3U' in content or '#EXTINF' in content:
                        print(f"成功解码M3U文件 (编码: {encoding})")
                        return content
                except UnicodeDecodeError:
                    continue
                    
            print(f"警告: 无法解码M3U文件 {url}")
            return None
            
        except Exception as e:
            print(f"下载M3U文件时出错: {e}")
            return None
            
    def _parse_m3u_content(self, content: str) -> List[Tuple[str, str]]:
        """解析M3U文件内容
        
        Args:
            content: M3U文件内容
            
        Returns:
            (频道信息, 流URL) 的元组列表
        """
        entries = []
        lines = content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过空行和注释（除了#EXTINF）
            if not line or (line.startswith('#') and not line.startswith('#EXTINF')):
                i += 1
                continue
                
            # 处理#EXTINF行
            if line.startswith('#EXTINF'):
                extinf = line
                i += 1
                
                # 查找对应的URL行
                while i < len(lines):
                    url_line = lines[i].strip()
                    if url_line and not url_line.startswith('#'):
                        # 验证URL格式
                        if self._is_valid_url(url_line):
                            entries.append((extinf, url_line))
                        break
                    i += 1
                    
            i += 1
            
        return entries
        
    def _is_valid_url(self, url: str) -> bool:
        """验证URL格式
        
        Args:
            url: 待验证的URL
            
        Returns:
            是否为有效URL
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    def crawl_region(self, region: str) -> List[Tuple[str, str]]:
        """爬取指定地区的M3U列表
        
        Args:
            region: 地区标识（如 'hong_kong__3'）
            
        Returns:
            (频道信息, 流URL) 的元组列表
        """
        print(f"\n开始处理地区: {region}")
        
        # 构建地区页面URL
        region_url = f"{self.base_url}/{region}"
        
        # 获取地区页面
        response = self._make_request(region_url)
        if not response:
            print(f"无法获取地区 {region} 的页面")
            return []
            
        # 提取所有下载链接
        download_urls = self._extract_all_download_links(response.text, region)
        if not download_urls:
            print(f"无法找到地区 {region} 的任何下载链接")
            return []
            
        print(f"找到 {len(download_urls)} 个下载链接")
        
        all_entries = []
        
        # 下载并解析每个M3U文件
        for i, download_url in enumerate(download_urls, 1):
            print(f"处理下载链接 {i}/{len(download_urls)}: {download_url}")
            
            # 下载M3U内容
            m3u_content = self._download_m3u_content(download_url)
            if not m3u_content:
                print(f"无法下载M3U内容: {download_url}")
                continue
                
            # 解析M3U内容
            entries = self._parse_m3u_content(m3u_content)
            if entries:
                all_entries.extend(entries)
                print(f"从链接 {i} 解析到 {len(entries)} 个频道")
            else:
                print(f"链接 {i} 没有解析到任何频道")
        
        print(f"从地区 {region} 总共解析到 {len(all_entries)} 个频道")
        
        return all_entries
        
    def merge_and_deduplicate(self, all_entries: List[List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
        """合并所有地区的M3U条目并去重
        
        Args:
            all_entries: 所有地区的条目列表
            
        Returns:
            去重后的条目列表
        """
        print(f"\n开始合并和去重...")
        
        seen_urls: Set[str] = set()
        merged_entries: List[Tuple[str, str]] = []
        
        total_entries = sum(len(entries) for entries in all_entries)
        print(f"合并前总计 {total_entries} 个频道")
        
        for entries in all_entries:
            for extinf, url in entries:
                if url not in seen_urls:
                    seen_urls.add(url)
                    merged_entries.append((extinf, url))
                    
        print(f"去重后保留 {len(merged_entries)} 个频道")
        return merged_entries
        
    def generate_m3u_file(self, entries: List[Tuple[str, str]], output_path: str):
        """生成最终的M3U文件
        
        Args:
            entries: 频道条目列表
            output_path: 输出文件路径
        """
        print(f"\n生成M3U文件: {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # 写入M3U文件头
                f.write('#EXTM3U\n')
                
                # 写入所有频道条目
                for extinf, url in entries:
                    f.write(f'{extinf}\n')
                    f.write(f'{url}\n')
                    
            print(f"成功生成M3U文件，包含 {len(entries)} 个频道")
            
        except Exception as e:
            print(f"生成M3U文件时出错: {e}")
            sys.exit(1)
            
    def run(self):
        """运行爬虫主程序"""
        print("=== IPTV M3U 播放列表更新器 ===")
        print(f"配置的地区: {', '.join(self.config['regions'])}")
        print(f"输出文件: {self.config['output_file']}")
        
        all_entries = []
        
        # 爬取所有地区
        for region in self.config['regions']:
            entries = self.crawl_region(region)
            if entries:
                all_entries.append(entries)
            else:
                print(f"警告: 地区 {region} 没有获取到任何频道")
                
        if not all_entries:
            print("错误: 没有从任何地区获取到频道数据")
            sys.exit(1)
            
        # 合并和去重
        merged_entries = self.merge_and_deduplicate(all_entries)
        
        if not merged_entries:
            print("错误: 合并后没有任何频道数据")
            sys.exit(1)
            
        # 生成文件
        self.generate_m3u_file(merged_entries, self.config['output_file'])
        
        print("\n=== 更新完成 ===")


def main():
    """主函数"""
    try:
        # 确保在正确的目录中运行
        script_dir = Path(__file__).parent
        config_path = script_dir.parent / "config.json"
        
        # 切换到项目根目录
        import os
        os.chdir(script_dir.parent)
        
        crawler = IPTVCrawler(str(config_path))
        crawler.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 