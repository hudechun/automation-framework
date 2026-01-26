"""
生成配置加密密钥
运行此脚本生成加密密钥，并添加到.env文件中
"""
from cryptography.fernet import Fernet


def generate_key():
    """生成加密密钥"""
    key = Fernet.generate_key()
    
    print('=' * 60)
    print('配置加密密钥生成成功！')
    print('=' * 60)
    print()
    print('请将以下内容添加到.env文件中：')
    print()
    print(f'CONFIG_ENCRYPTION_KEY={key.decode()}')
    print()
    print('=' * 60)
    print('注意事项：')
    print('1. 请妥善保管此密钥，丢失后无法解密已加密的配置')
    print('2. 生产环境和测试环境应使用不同的密钥')
    print('3. 定期轮换密钥以提高安全性')
    print('4. 不要将密钥提交到版本控制系统')
    print('=' * 60)


if __name__ == '__main__':
    generate_key()
