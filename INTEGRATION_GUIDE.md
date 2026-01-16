# Flet-Cli Integration Guide

自动将自定义的 `packn.py` 整合进 flet-cli 官方新版本的脚本。

## 功能特性

- 🔽 自动从 GitHub 下载指定版本的 flet-cli 源码
- 📦 自动整合 `packn.py` 到官方版本
- 🔧 自动更新 `cli.py` 注册 `packn` 命令
- 📝 自动更新 `pyproject.toml` 添加自定义元数据
- 💾 自动备份当前版本
- ✅ 自动验证集成结果

## 使用方法

### 基本用法

整合 flet-cli 0.80.2 版本：

```bash
python integrate_packn.py 0.80.2
```

### 高级选项

```bash
# 不创建备份
python integrate_packn.py 0.80.2 --no-backup

# 跳过验证
python integrate_packn.py 0.80.2 --no-verify

# 指定源目录和输出目录
python integrate_packn.py 0.80.2 \
    --source /path/to/current/flet-cli \
    --output /path/to/new/flet-cli
```

## 工作流程

脚本执行以下步骤：

1. **下载官方版本** - 从 GitHub 下载指定版本的 flet-cli 源码
2. **备份当前版本** - 创建 `.backup_{version}` 目录备份当前代码
3. **整合 packn.py** - 将自定义的 `packn.py` 复制到官方版本
4. **更新 cli.py** - 添加 `packn` 命令的导入和注册
5. **更新配置** - 修改 `pyproject.toml` 添加描述和维护者信息
6. **创建 MANIFEST.in** - 确保打包时包含必要文件
7. **复制到输出** - 将整合后的代码复制到输出目录
8. **验证结果** - 检查所有文件是否正确整合

## 集成后的变更

### cli.py

自动添加：
```python
import flet_cli.commands.packn
```

和：
```python
flet_cli.commands.packn.Command.register_to(sp, "packn")
```

### pyproject.toml

自动更新：
```toml
description = "Flet CLI with Nuitka packaging support for Windows"
maintainers = [{ name = "LingyeSoul", email = "lingyesoul@users.noreply.github.com" }]

[project.optional-dependencies]
nuitka = ["nuitka"]
```

## 使用示例

### 示例 1: 更新到 0.80.2

```bash
# 1. 运行集成脚本
python integrate_packn.py 0.80.2

# 2. 检查变更
git diff

# 3. 测试构建
python -m build

# 4. 本地安装测试
pip install -e .

# 5. 验证 packn 命令
flet-cli packn --help
```

### 示例 2: 从现有项目更新

```bash
# 假设当前在 flet_cli 项目目录
python integrate_packn.py 0.80.2

# 查看备份目录
ls .backup_0.80.2/

# 如果需要回滚
rm -rf src/pyproject.toml
cp -r .backup_0.80.2/* .
```

## 注意事项

1. **版本格式**: 使用语义化版本号，如 `0.80.2` 或 `v0.80.2`
2. **网络连接**: 需要能够访问 GitHub 下载源码
3. **packn.py**: 必须存在于 `src/flet_cli/commands/packn.py`
4. **备份**: 默认会创建备份，建议保留以便回滚

## 故障排除

### 下载失败

如果下载失败，可以手动下载：

```bash
# 手动下载
wget https://github.com/flet-dev/flet/archive/refs/tags/0.80.2.tar.gz

# 然后使用本地目录
python integrate_packn.py 0.80.2 --source /path/to/downloaded
```

### 验证失败

如果验证失败，检查：

```bash
# 检查 packn.py 是否存在
ls src/flet_cli/commands/packn.py

# 检查 cli.py 是否正确更新
grep "packn" src/flet_cli/cli.py

# 检查 pyproject.toml
grep -A2 "optional-dependencies" pyproject.toml
```

### 回滚到备份

```bash
# 删除当前文件
rm -rf src/pyproject.toml README.md LICENSE MANIFEST.in

# 恢复备份
cp -r .backup_0.80.2/* .
```

## 版本升级流程

推荐的版本升级流程：

```bash
# 1. 检查当前版本
cat pyproject.toml | grep version

# 2. 查看最新版本
# 访问 https://github.com/flet-dev/flet/releases

# 3. 运行集成脚本
python integrate_packn.py 0.80.2

# 4. 查看变更
git status
git diff

# 5. 提交变更
git add .
git commit -m "Integrate packn.py with flet-cli 0.80.2"

# 6. 测试
python -m build
pip install --force-reinstall dist/flet_cli-0.80.2-py3-none-any.whl
flet-cli packn --help
```

## 许可证

Apache-2.0 (与 flet-cli 保持一致)
