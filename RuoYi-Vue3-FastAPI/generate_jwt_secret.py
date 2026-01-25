"""
生成新的 JWT 密钥
"""
import secrets

print("=" * 60)
print("生成新的 JWT 密钥")
print("=" * 60)
print()
print("开发环境 JWT 密钥:")
dev_key = secrets.token_hex(32)
print(dev_key)
print()
print("生产环境 JWT 密钥:")
prod_key = secrets.token_hex(32)
print(prod_key)
print()
print("=" * 60)
print("请将上述密钥分别复制到 .env.dev 和 .env.prod 文件中")
print("=" * 60)
