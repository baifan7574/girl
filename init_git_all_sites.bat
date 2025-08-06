@echo off
setlocal enabledelayedexpansion

:: 设置 GitHub 用户信息（只执行一次）
git config --global user.name "baifan7574"
git config --global user.email "baifan7574@gmail.com"

:: 设置项目根目录
set "BASE_DIR=D:\项目"

:: 设置最大网站编号
set "START=1"
set "END=40"

echo ===========================
echo 🚀 正在批量初始化 Git 仓库...
echo ===========================

for /L %%i in (%START%,1,%END%) do (
    set "SITE=g%%i"
    set "PATH=!BASE_DIR!\!SITE!"

    if exist "!PATH!" (
        cd /d "!PATH!"

        :: 如果没有 .git 文件夹，则初始化
        if not exist ".git" (
            echo 🔧 初始化 Git 仓库：!SITE!
            git init
        )

        :: 检查是否已设置远程
        git remote -v | findstr "origin" >nul
        if errorlevel 1 (
            echo 🌐 设置远程仓库：origin → https://github.com/baifan7574/!SITE!.git
            git remote add origin https://github.com/baifan7574/!SITE!.git
        ) else (
            echo ✅ 已有远程仓库：!SITE!
        )
    ) else (
        echo ❌ 未找到目录：!PATH!
    )
)

echo.
echo ✅ 所有网站 Git 初始化完成
pause
