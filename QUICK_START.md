# Flet-Cli 版本升级快速参考

## 🚀 快速命令

```bash
# 升级到新版本
python integrate_packn.py 0.80.2

# 跳过备份（加快速度）
python integrate_packn.py 0.80.2 --no-backup

# 查看帮助
python integrate_packn.py --help
```

## 📋 完整升级流程

```bash
# 1. 升级到新版本
python integrate_packn.py 0.80.2

# 2. 检查变更
git status
git diff

# 3. 构建包
python -m build

# 4. 本地安装测试
pip install -e .

# 5. 测试 packn 命令
flet-cli packn --help

# 6. 提交变更
git add .
git commit -m "Integrate packn.py with flet-cli 0.80.2"
```

## 🔄 回滚到备份

```bash
# 删除当前文件
rm -rf src pyproject.toml README.md LICENSE MANIFEST.in

# 恢复备份
cp -r .backup_0.80.2/* .
```

## ✅ 验证清单

- [ ] packn.py 存在于 `src/flet_cli/commands/packn.py`
- [ ] cli.py 包含 `import flet_cli.commands.packn`
- [ ] cli.py 包含 `packn.Command.register_to(sp, "packn")`
- [ ] pyproject.toml 包含自定义描述
- [ ] MANIFEST.in 文件存在
- [ ] `python -m build` 成功
- [ ] `flet-cli packn --help` 工作正常

## 📌 常用版本号

- 最新版本: 访问 https://github.com/flet-dev/flet/releases
- 版本格式: `0.80.2` 或 `v0.80.2`

## 🛠️ 故障排除

```bash
# 检查 packn.py
ls -lh src/flet_cli/commands/packn.py

# 检查 cli.py
grep "packn" src/flet_cli/cli.py

# 检查配置
cat pyproject.toml | grep -A5 "optional-dependencies"

# 手动验证
python -c "
from pathlib import Path
packn = Path('src/flet_cli/commands/packn.py')
print('packn.py exists:', packn.exists())
"
```
