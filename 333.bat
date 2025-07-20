@echo off
title 自动生成图站并写入SEO信息
echo ========================================
echo 正在运行 Python 脚本生成图站内容...
echo ========================================

REM 启动 Python 脚本
python generate_site_v2.py

echo.
echo ✅ 网站页面已生成，sitemap.xml 已创建
echo ✅ 已尝试通知 Google 抓取
echo.
pause
